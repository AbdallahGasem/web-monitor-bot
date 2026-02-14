# 🔍 DataAnnotation Project Monitor

A lightweight, passive Python utility designed to monitor the DataAnnotation dashboard for new project availability and send instant notifications via Telegram.

> **Disclaimer:** This tool is for **personal use only** to assist with availability monitoring. It does not automate work, accept tasks, or interact with the platform's core inputs. It is designed to run passively with conservative rate limits to ensure compliance with standard web usage policies.

## Features

* **Passive Monitoring:** Checks the project dashboard at scheduled intervals (default: 5 minutes) without user interaction.
* **Instant Notifications:** Sends a message to your Telegram account immediately when a new project appears.
* **State Tracking:** Uses a local JSON file (`seen_projects.json`) to track project history, preventing duplicate alerts for existing projects.
* **Smart "Cold Start":** On the very first run, it memorizes existing projects silently without spamming you with alerts.


## Prerequisites

* Python 3.8 or higher
* A Telegram account (for notifications)

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/AbdallahGasem/web-monitor-bot
cd web-monitor-bot

```


2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Configuration:**
Create a file named `.env` in the root directory and add your keys:
```env
TELEGRAM_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

```



## Usage

Run the monitor script:

```bash
python app.py

```

The script will start the scheduling loop. You will see logs in the console indicating when it checks the website and if any changes are detected.

To stop the monitor, simply press `Ctrl + C` in your terminal.

## Project Structure

* `app.py`: The main application logic.
* `requirements.txt`: List of Python libraries required.
* `.env`: (Ignored by Git) Stores your secret API keys.
* `seen_projects.json`: (Generated automatically) Local database of project IDs.

## How It Works

1. **Fetch:** The script requests the dashboard HTML using standard HTTP requests.
2. **Parse:** It utilizes `BeautifulSoup` to locate the specific embedded JSON data within the page structure (`data-props`), ensuring accurate data extraction without fragile HTML text scraping.
3. **Compare:** It compares the current list of Project IDs against the locally saved `seen_projects.json`.
4. **Notify:** If a set difference is found (New ID - Old IDs), it triggers the Telegram API to send an alert.

## Compliance & Ethics

This tool is designed to be **non-intrusive**:

* It does **not** solve tasks.
* It does **not** auto-refresh rapidly (default interval is 5 minutes).
* It does **not** bypass login screens (requires session cookie management if run against the live site).