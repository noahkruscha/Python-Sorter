import config_paths as cp
import json
import shutil
from datetime import datetime
from pathlib import Path

def sort_file(file_path):
    file_path = Path(file_path)

    file_name = file_path.name
    file_suffix = file_path.suffix[1:]

    # alle nötigen directories aus config_path.py laden
    with open(cp.CONFIG_PATH, "r") as f:
        config = json.load(f)

    # Kategorien bzw später Ordnernamen aus rules.json laden
    categories = config["categories"]

    # Datei abgeleichen und passende Kategorie finden
    def get_category(file_suffix, categories):
        file_suffix = file_suffix.lower()

        for category, extensions in categories.items():
            if file_suffix in extensions:
                return category

        return "other"

    # Kategorie abrufen und in 'category' speichern
    category = get_category(file_suffix, categories)

    # Zielordner setzen und bei fehlen erstellen
    target_folder = cp.OUTPUT_DIR / category
    target_folder.mkdir(parents=True, exist_ok=True)

    target_path = target_folder / file_name

    # Datei in Zielordner bewegen
    shutil.move(str(file_path), str(target_path))

    # loggen
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if config["logging"]["enabled"]:
        log_path = Path(config["logging"]["file"])
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_entry = f"{file_name} wurde um {current_time} nach {category} bewegt"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
        suffix_log_path = Path(config["logging"]["suffix_log"])
        suffix_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(suffix_log_path, "a", encoding="utf-8") as f:
            f.write(file_suffix + "\n")