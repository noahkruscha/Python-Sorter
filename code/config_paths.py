from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

EVENT_DIR = BASE_DIR.parent / "event"
OUTPUT_DIR = BASE_DIR.parent / "result" / "organized"
CONFIG_PATH = BASE_DIR / "rules.json"
SETTINGS_PATH = BASE_DIR / "settings.json"
LOG_PATH = BASE_DIR.parent / "result" / "logs"

os.environ['TKDND_LIBRARY'] = str(BASE_DIR.parent / 'python_env' / 'libs' / 'tkinterdnd2' / 'tkdnd')
