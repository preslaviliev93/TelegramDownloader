# TelegramDownloader

TelegramDownloader is a Python tool for extracting and archiving content from Telegram groups and channels.  
It uses the official Telegram API via Telethon and allows you to download media files, and prepare datasets for analysis, machine learning, or archives.


---

## Table of Contents

- [Features](#features)  
- [Planned Extensions](#planned-planned-extensions)  
- [Requirements](#requirements)  
- [Installation](#installation)  
- [Environment Configuration](#environment-configuration)  
- [Usage](#usage)  
- [Project Structure](#project-structure)  
- [Notes](#notes)  
- [Legal and Ethical Considerations](#legal-and-ethical-considerations)  
- [Contributing](#contributing)  
- [License](#license)

---

## Features

- Authenticate using a Telegram user account.
- Download media from public or private groups/channels.
- Automatic folder creation based on channel name.
- Download all available media (photos, videos, documents, audio).
- Fully asynchronous message iteration for efficient scraping.
- Resolve channels by:
  - Username  
  - t.me link  
  - Group title (for private groups)
- Customizable download directory via `.env`.
- Interactive menu allowing:
  - Text-only export (.csv)
  - Media-only download
  - Full download (text + media)
- CSV export including:
  - message id
  - timestamp
  - sender_id
  - sender username
  - cleaned text


---

## Planned Extensions

- Export conversations to CSV, JSON, or Parquet.
- Export text-only datasets for NLP tasks.
- Export media reference datasets.
- Incremental synchronization (download only new messages).
- Parallel media downloads.
- Channel discovery utilities.
- Dataset preprocessing pipeline.

---

## Requirements

- Python 3.10 or higher  
- A Telegram account  
- API ID and API Hash from https://my.telegram.org  
- Dependencies:
  - telethon
  - python-dotenv

---

## Installation

Clone the repository:

```bash
git clone https://github.com/preslaviliev93/TelegramDownloader.git
cd TelegramDownloader
```
```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Linux/macOS
```

```bash
pip install -r requirements.txt
```

```bash
API_ID=your_api_id
API_HASH=your_api_hash
DOWNLOAD_DIR=downloads
```
## Usage

```bash
    python main.py
```