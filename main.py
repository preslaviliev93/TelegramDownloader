import os
import csv
from pathlib import Path
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()


class TelegramDownloader:
    def __init__(self):
        self.api_id: int = int(os.getenv("API_ID"))
        self.api_hash: str = os.getenv("API_HASH")
        self.session_name: str = "telegram_downloader"
        self.directory: Path = self.get_download_dir()
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)

    @staticmethod
    def get_download_dir() -> Path:
        raw_dir = os.getenv("DOWNLOAD_DIR")
        if not raw_dir:
            raise ValueError("DOWNLOAD_DIR is not set in the .env file")

        download_dir = Path(raw_dir).expanduser()
        download_dir.mkdir(parents=True, exist_ok=True)
        return download_dir

    def get_channels_from_user_input(self) -> list[str]:
        all_channels: list[str] = []
        while True:
            ch = input("Enter [channel/group name/link] or [0] for exit: ")
            ch = ch.strip()
            if ch == "0":
                break
            if ch:
                all_channels.append(ch)
        return all_channels

    def get_download_mode_from_user(self) -> str:
        """
        Returns one of: 'text', 'media', 'all'
        """
        print("Select download mode:")
        print("[1] Download only TEXT (.csv)")
        print("[2] Download only MEDIA")
        print("[3] Download ALL (text + media)")

        while True:
            choice = input("Enter choice [1-3] (or 0 to exit): ").strip()
            if choice == "0":
                return ""
            if choice == "1":
                return "text"
            if choice == "2":
                return "media"
            if choice == "3":
                return "all"
            print("Invalid choice, please enter 1, 2, 3 or 0.")

    async def resolve_entity(self, raw: str):
        """
        Find channel/chat by:
        - @username
        - t.me link
        - chat name (you must participate in the chat conversation)
        """
        # 1)  @username or t.me link
        if raw.startswith("@") or "t.me/" in raw:
            return await self.client.get_entity(raw)

        # 2) Search in dialogs
        dialogs = await self.client.get_dialogs()

        for d in dialogs:
            if d.name and d.name.lower() == raw.lower():
                print(f'   [*] Matched by title: "{d.name}"')
                return d.entity

        for d in dialogs:
            if d.name and raw.lower() in d.name.lower():
                print(f'   [*] Partial match: "{d.name}"')
                return d.entity

        raise ValueError(f'Cannot find any chat/channel with title or username matching "{raw}"')

    async def dump_channel(self, channel_raw: str, mode: str = "all", limit: int = 100):
        """
        mode:
          - 'text'  -> only text in *.csv
          - 'media' -> only media
          - 'all'   -> media & text
        """
        print(f"==> Resolving: {channel_raw} ...")
        entity = await self.resolve_entity(channel_raw)

        safe_name = channel_raw.replace("https://t.me/", "").replace("@", "").replace(" ", "_")
        channel_dir = self.directory / safe_name
        channel_dir.mkdir(parents=True, exist_ok=True)

        print(f"==> Downloading into folder: {channel_dir}")
        if mode in ("text", "all"):
            csv_path = channel_dir / f"{safe_name}.csv"
            print(f"    -> text will be saved to: {csv_path}")
        else:
            csv_path = None

        csv_file = None
        writer = None

        try:
            if csv_path:
                csv_file = open(csv_path, "w", newline="", encoding="utf-8")
                writer = csv.writer(csv_file)

                writer.writerow(["id", "date", "sender_id", "username", "text"])

            async for msg in self.client.iter_messages(entity, limit=limit):
                text = (msg.text or "").replace("\n", " ")
                print(f"[{msg.id}] {msg.date} | {text[:80]}")

                # ----- TEXT / CSV -----
                if writer is not None and mode in ("text", "all"):
                    try:
                        sender_id = getattr(msg, "sender_id", None)

                        # Take sender name
                        username = ""
                        try:
                            sender = await msg.get_sender()
                            if sender and getattr(sender, "username", None):
                                username = sender.username
                        except Exception as e:
                            print(f"    !! get_sender error: {e}")

                        writer.writerow(
                            [
                                msg.id,
                                msg.date.isoformat() if msg.date else "",
                                str(sender_id) if sender_id is not None else "",
                                username,
                                text,
                            ]
                        )
                    except Exception as e:
                        print(f"    !! csv write error: {e}")

                # ----- MEDIA -----
                if msg.media and mode in ("media", "all"):
                    try:
                        file_path = await self.client.download_media(msg, channel_dir)
                        print(f"    -> media saved to: {file_path}")
                    except Exception as e:
                        print(f"    !! media error: {e}")

        finally:
            if csv_file is not None:
                csv_file.close()

    async def main(self):
        mode = self.get_download_mode_from_user()
        if not mode:
            print("No mode selected. Exiting.")
            return

        channels = self.get_channels_from_user_input()
        if not channels:
            print("No channels entered. Exiting.")
            return

        for ch in channels:
            try:
                # limit=None -> all messages
                # if you configure limit 100 -> the script will get only 100 messages
                await self.dump_channel(ch, mode=mode, limit=None)
            except Exception as e:
                print(f"[ERROR] While processing '{ch}': {e}")


if __name__ == "__main__":
    tg = TelegramDownloader()

    # First time it will ask you for phone number and code
    tg.client.start()

    # Session is established
    tg.client.loop.run_until_complete(tg.main())
