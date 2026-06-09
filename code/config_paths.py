from pathlib import Path
import os
import json

BASE_DIR = Path(__file__).resolve().parent

import sys


BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "settings.json", "r", encoding="utf-8") as f:
    settings = json.load(f)

EVENT_DIR = Path(settings.get("setup", {}).get("input_dir", None) or BASE_DIR.parent / "event")
OUTPUT_DIR = Path(settings.get("setup", {}).get("output_dir", None) or BASE_DIR.parent / "result" / "organized")
CONFIG_PATH = BASE_DIR / "rules.json"
SETTINGS_PATH = BASE_DIR / "settings.json"
LOG_PATH = BASE_DIR / "logs"

os.environ['TKDND_LIBRARY'] = str(BASE_DIR.parent / 'python_env' / 'libs' / 'tkinterdnd2' / 'tkdnd')