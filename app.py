import requests
import schedule
import time
import os
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# 1. Load secrets
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL_TO_MONITOR = "http://127.0.0.1:5500/webpage/DataAnnotation.html"
# Real URL: "https://app.dataannotation.tech/workers/projects"

def parse_projects(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    project_root = soup.find('div', id='workers/WorkerProjectsTable-hybrid-root')
    
    if not project_root:
        # ⚠️ Silent failure risk: If the site structure changes, we might return []
        # and accidentally clear our "seen" list.
        print("Warning: Could not find project table. Possible login issue or layout change.")
        return None # Return None instead of [] to signal error

    raw_props = project_root.get('data-props')
    try:
        data = json.loads(raw_props)
        return data.get('dashboardMerchTargeting', {}).get('projects', [])
    except json.JSONDecodeError:
        print("Failed to decode project JSON.")
        return None

def check_for_new_projects(current_projects):
    filename = "seen_projects.json"
    
    # Map ID -> Name
    current_project_map = {p['id']: p['name'] for p in current_projects}
    current_ids = set(current_project_map.keys())

    is_first_run = False  # <--- New Flag

    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                seen_ids = set(json.load(f))
            except json.JSONDecodeError:
                seen_ids = set()
    else:
        seen_ids = set()
        is_first_run = True  # <--- Mark as first run

    # Calculate new items
    new_project_ids = current_ids - seen_ids

    # Update the file immediately
    with open(filename, 'w') as f:
        json.dump(list(current_ids), f)

    # --- LOGIC FIX ---
    if is_first_run:
        print(f"-> System initialized. Memorized {len(current_ids)} existing projects. No alert sent.")
        return [] # Return empty list so no alert is triggered

    if new_project_ids:
        print(f"found {len(new_project_ids)} NEW projects!")
        new_names = []
        for pid in new_project_ids:
            name = current_project_map.get(pid, "Unknown Project")
            print(f" -> NEW: {name}")
            new_names.append(name)
        return new_names
    else:
        print("No new projects found.")
        return []
    
def send_telegram_alert(project_names):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Create a nice formatted message
    msg_text = f"🚨 <b>New Projects Found!</b>\n\n"
    for name in project_names:
        msg_text += f"• {name}\n"
    
    params = {
        "chat_id": CHAT_ID, 
        "text": msg_text, 
        "parse_mode": "HTML" # Allows bolding
    }
    
    try:
        requests.get(url, params=params)
        print(" -> Alert sent to Telegram!")
    except Exception as e:
        print(f"Error sending alert: {e}")

def check_website():
    print(f"[{time.strftime('%H:%M:%S')}] Checking website...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(URL_TO_MONITOR, headers=headers)
    
        # Parse it
        projects = parse_projects(response.text)
        
        # Only proceed if parsing succeeded (projects is not None)
        if projects is not None:
            new_projects_list = check_for_new_projects(projects)
            
            if new_projects_list:
                send_telegram_alert(new_projects_list) 
        else:
            print("Skipping check due to parse error.")
            
    except Exception as e:
        print(f"Error: {e}")

# Schedule
schedule.every(5).minutes.do(check_website)

print("Monitor started... (Press Ctrl+C to stop)")
check_website()
while True:
    schedule.run_pending()
    time.sleep(1)