from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

EVENT_DIR = BASE_DIR.parent / "event"
OUTPUT_DIR = BASE_DIR.parent / "result" / "organized"
CONFIG_PATH = BASE_DIR / "rules.json"
SETTINGS_PATH = BASE_DIR / "settings.json"
LOG_PATH = BASE_DIR.parent / "result" / "logs"