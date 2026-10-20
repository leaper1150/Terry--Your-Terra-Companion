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
    if not api_key:
        return 0.0

    # 1. Put the date math & headers back!
    today_datetime = datetime.date.today()
    monday_date = today_datetime - datetime.timedelta(days=today_datetime.weekday())
    today_date_str = today_datetime.strftime("%Y-%m-%d")
    monday_date_str = monday_date.strftime("%Y-%m-%d")

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    try:
        url = f"{api_url}/users/current/summaries?start={monday_date_str}&end={today_date_str}"
        response = requests.get(url, headers=headers, timeout=6)
        response.raise_for_status()
        data = response.json()

        # 2. Replace "total_hours" with Hackatime's seconds -> hours math:
        total_seconds = data.get("cumulative_total", {}).get("seconds", 0.0)
        return round(total_seconds / 3600.0, 2)
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


def main():
    cfg = load_config()
    print("Config file is saved at:", CONFIG_FILE)
    hours = fetch_week_hours(cfg)
    print(f"🦖 You have coded {hours} hours this week!")

if __name__ == "__main__":
    main()