import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".terry_companion"

CONFIG_FILE = CONFIG_DIR/ "config.json"

DEFAULT_CONFIG = default_user = {
    "onboarded": False,
    "username": "",
    "api_key": "",
    "api_url": "https://hackatime.hackclub.com/api/hackatime/v1",
    "webhook_url": "",
    "goal_hours": "10.0",
    "editor_cmd": "code",
    "last_state": "",
}








