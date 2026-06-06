from pathlib import Path
import sys

code_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(code_dir))
import config_paths as cp

import json
import customtkinter as ctk
from tkinter import filedialog


def _load_config() -> dict:
    try:
        with open(cp.SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_config(data: dict) -> None:
    config = _load_config()
    config["setup"] = data
    with open(cp.SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def run_setup() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Setup")
    app.geometry("520x280")
    app.resizable(False, False)

    existing = _load_config().get("setup", {})

    ctk.CTkLabel(app, text="Setup", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(24, 4))
    ctk.CTkLabel(app, text="Ordner für Ein- und Ausgabe festlegen", text_color="gray70").pack(pady=(0, 20))

    input_var = ctk.StringVar(value=existing.get("input_dir", ""))
    output_var = ctk.StringVar(value=existing.get("output_dir", ""))

    def make_row(parent, label_text: str, var: ctk.StringVar) -> None:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=32, pady=6)

        ctk.CTkLabel(frame, text=label_text, width=100, anchor="w").pack(side="left")

        entry = ctk.CTkEntry(frame, textvariable=var, width=280, placeholder_text="Pfad wählen...")
        entry.pack(side="left", padx=(0, 8))

        def browse(v=var):
            path = filedialog.askdirectory(title=f"{label_text} wählen")
            if path:
                v.set(path)

        ctk.CTkButton(frame, text="...", width=36, command=browse).pack(side="left")

    make_row(app, "Eingabe", input_var)
    make_row(app, "Ausgabe", output_var)

    status_label = ctk.CTkLabel(app, text="", text_color="gray60")
    status_label.pack(pady=(10, 0))

    def on_save() -> None:
        input_dir = input_var.get().strip()
        output_dir = output_var.get().strip()

        if not input_dir or not output_dir:
            status_label.configure(text="Beide Ordner müssen angegeben werden.", text_color="#e05252")
            return

        _save_config({"input_dir": input_dir, "output_dir": output_dir})
        status_label.configure(text="Gespeichert.", text_color="#52e07a")
        app.after(800, app.destroy)

    ctk.CTkButton(app, text="Speichern", command=on_save, width=160).pack(pady=(8, 0))

    app.mainloop()