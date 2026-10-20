import json
from pathlib import Path
import datetime 
import requests 
import os 


#this app is for tracking weekly hourse and goals for hackatime to help users win in Terra 

CONFIG_DIR = Path.home() / ".terry_companion"

CONFIG_FILE = CONFIG_DIR/ "config.json"

DEFAULT_CONFIG = default_user = {
    "onboarded": False,
    "username": "",
    "api_key": "",
    "api_url": "https://hackatime.hackclub.com/api/hackatime/v1",
    "webhook_url": "",
    "goal_hours": 10.0,
    "editor_cmd": "code",
    "last_state": "",
}

def load_config():
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    # Ensure all default keys are present
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value

    return config
##holy copilot
def save_config(config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

#I have no idea why copoilot is doing this but it is so funny
def fetch_week_hours(config):
    api_key = config.get("api_key").strip()
    api_url = config.get("api_url").strip().rstrip("/")

    today_datetime = datetime.date.today()
    monday_date = today_datetime - datetime.timedelta(days=today_datetime.weekday())

    today_date_str = today_datetime.strftime("%Y-%m-%d")
    monday_date_str = monday_date.strftime("%Y-%m-%d")

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    try:
        response = requests.get(f"{api_url}/users/me/hours?start_date={monday_date_str}&end_date={today_date_str}", headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("total_hours", 0.0)
    except requests.RequestException as e:
        print(f"Error fetching week hours: {e}")
        return 0.0


def send_webhook(webhook_url, message):
    payload = {
        "text": message
    }
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error sending webhook: {e}")    

