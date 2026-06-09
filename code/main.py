import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config_paths as cp
import json
from ui import gui
from ui import setup

os.environ['TKDND_LIBRARY'] = os.path.join(cp.BASE_DIR.parent, 
                                           'python_env', 
                                           'libs', 
                                           'tkinterdnd2', 
                                           'tkdnd' 
)

with open(cp.SETTINGS_PATH, "r", encoding="utf-8") as f:
    settings = json.load(f)

if not settings.get("setup", {}).get("done", False):
    completed = setup.run_setup()
    with open(cp.SETTINGS_PATH, "r", encoding="utf-8") as f:
        settings = json.load(f)
    settings["setup"]["done"] = True
    with open(cp.SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

gui.start_gui()