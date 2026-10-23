import json
from pathlib import Path
import datetime 
import requests
import os 
import subprocess
import sys
import multiprocessing
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
    

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
    "daily_goal": 1.5,
    "editor_cmd": "code",
    "last_state": "",
}


def get_assets_dir():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running as a PyInstaller bundle
        return Path(sys._MEIPASS) / "assets"
    return Path(__file__).parent / "assets"




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
        return 0.0, 0.0

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

        # 1. Total hours for the whole week (Monday -> Today)
        total_seconds = data.get("cumulative_total", {}).get("seconds", 0.0)
        week_hours = round(total_seconds / 3600.0, 2)

        # 2. Hours coded TODAY (the last day in the 'data' list)
        days_list = data.get("data", [])
        if days_list:
            today_seconds = days_list[-1].get("grand_total", {}).get("total_seconds", 0.0)
        else:
            today_seconds = 0.0
        today_hours = round(today_seconds / 3600.0, 2)

        return week_hours, today_hours

    
    except requests.RequestException as e:
        print(f"Error fetching hours: {e}")
        return 0.0, 0.0



def send_webhook(webhook_url, message):
    payload = {
        "text": message
    }
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error sending webhook: {e}")


def format_hours(hours):
    total_minutes = round(hours * 60)
    h, m = divmod(total_minutes, 60)
    return f"{h}h {m}m"

def compute_status(week_hours, today_hours, goal_hours, daily_goal):
    now = datetime.datetime.now()
    days_to_sunday = (6 - now.weekday()) % 7
    sunday_date = now + datetime.timedelta(days=days_to_sunday)
    sunday_cutoff = sunday_date.replace(hour=23, minute=59, second=59, microsecond=0)

    time_left = max(datetime.timedelta(seconds=0), sunday_cutoff - now)
    hours_left_in_week = time_left.total_seconds() / 3600.0

    # 1. Cumulative Quota Math (Day 1 = Mon, Day 2 = Tue, ..., Day 7 = Sun)
    day_number = now.weekday() + 1
    expected_by_tonight = min(goal_hours, day_number * daily_goal)

    # How much you need for the whole week vs. how much to catch up by tonight
    week_needed = max(0.0, goal_hours - week_hours)
    needed_for_tonight = max(0.0, expected_by_tonight - week_hours)

    # 2. Terry's 5 Moods
    if week_hours >= goal_hours:
        state = "ready"
        title = "WEEKLY QUOTA COMPLETED!"
        color = "emerald"
        msg = "Terry is proud of you! All 10 hours done for the week!"
    elif week_needed > hours_left_in_week:
        state = "eviction"
        title = "EVICTION NOTICE HAS BEEN SERVED"
        color = "stone"
        msg = f"Cooked! You need {format_hours(week_needed)}, but only {format_hours(hours_left_in_week)} are left this week!"
    elif hours_left_in_week <= 24.0 and week_needed > 0:
        state = "danger"
        title = "SUNDAY DANGER ZONE LOCK IN PLEASE"
        color = "rose"
        msg = f"Less than 24h left! Log {format_hours(week_needed)} before midnight!"
    elif needed_for_tonight == 0:
        state = "ready"
        title = f"DAY {day_number} QUOTA COMPLETE!"
        color = "emerald"
        msg = f"You passed Day {day_number}'s target ({format_hours(expected_by_tonight)})! {format_hours(week_needed)} left for the week."
    elif needed_for_tonight <= (daily_goal / 2):
        state = "safe"
        title = "WARMING ZONE"
        color = "green"
        msg = f"Almost at Day {day_number}'s {format_hours(expected_by_tonight)} target! Just {format_hours(needed_for_tonight)} more tonight."
    else:
        state = "hurry"
        title = "YOU NEED TO WORK!!"
        color = "amber"
        msg = f"Log {format_hours(needed_for_tonight)} more tonight to reach Day {day_number}'s target of {format_hours(expected_by_tonight)}!"

    return {
        "state": state,
        "title": title,
        "color": color,
        "msg": msg,
        "expected_by_tonight": expected_by_tonight,
        "needed_for_tonight": needed_for_tonight,
        "hours_left_str": format_hours(hours_left_in_week),
    }



def main():
    cfg = load_config()
    week_hours, today_hours = fetch_week_hours(cfg)
    status = compute_status(week_hours, today_hours, cfg["goal_hours"], cfg["daily_goal"])

    print(f" Coded Today: {today_hours} / {cfg['daily_goal']}h")
    print(f" Coded This Week: {week_hours} / {cfg['goal_hours']}h")
    print(f" Terry's Mood: [{status['state'].upper()}] {status['title']}")
    print(f" {status['msg']}")


if __name__ in {"__main__", "__mp_main__"}:
    main()



