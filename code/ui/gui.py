import customtkinter
from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinterdnd2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from pathlib import Path
import sys
import os
import re
import subprocess
from collections import Counter
code_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(code_dir))
import config_paths as cp
import sorter

def start_gui():
    with open(cp.CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    with open(cp.SETTINGS_PATH, "r", encoding="utf-8") as f:
        settings = json.load(f)

    app = customtkinter.CTk()
    app.geometry("800x305")
    app.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
    app.grid_rowconfigure((0, 1, 2,), weight=1)

    dnd_binary_dir = os.path.join(os.path.dirname(tkinterdnd2.__file__), "tkdnd", "win-x64")

    app.tk.call('lappend', 'auto_path', dnd_binary_dir)

    app.tk.call('package', 'require', 'tkdnd')

    appearance_mode = settings["appearance"]["mode"]
    color_theme = settings["appearance"]["color_theme"]
    chart_infill_color = "#2b2b2b"
    chart_text_color = "white"

    customtkinter.set_appearance_mode(appearance_mode)
    customtkinter.set_default_color_theme(color_theme)

    if config["logging"]["enabled"]:
        global logging_switch_var
        logging_switch_var = customtkinter.StringVar(value="on")
    else:
        logging_switch_var = customtkinter.StringVar(value="off")

    if settings["watcher"]["enabled"]:
        global watcher_switch_var
        watcher_switch_var = customtkinter.StringVar(value="on")
    else:
        watcher_switch_var = customtkinter.StringVar(value="off")

    def watcher_switch_event():
        if watcher_switch_var.get() == 'off':
            settings["watcher"]["enabled"] = False
            pid_file = cp.LOG_PATH / "watcher.pid"
            if pid_file.exists():
                pid = int(pid_file.read_text())
                subprocess.run(["taskkill", "/PID", str(pid), "/F"])
                pid_file.unlink()
        else:
            pid_file = cp.LOG_PATH / "watcher.pid"
            if pid_file.exists():
                return
            settings["watcher"]["enabled"] = True
            python_exe = sys.executable
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(
                [str(python_exe), str(code_dir / "watcher.py")],
                startupinfo=startupinfo
            )
        with open(cp.SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)

    def datei_gedroppt(event):
        dateipfad = event.data
        if dateipfad.startswith("{") and dateipfad.endswith("}"):
            dateipfad = dateipfad[1:-1]
        print(f"Datei erhalten: {dateipfad}")
        sorter.sort_file(dateipfad)
        refresh_chart()

    def restart_app():
        app.quit()
        app.destroy()
        subprocess.Popen([sys.executable, sys.argv[0]])
        sys.exit()

    def appearance_color_theme_optionmenu_callback(choice):
        color_theme = choice
        settings["appearance"]["color_theme"] = color_theme
        with open(cp.SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        customtkinter.set_default_color_theme(color_theme)

    def appearance_mode_optionmenu_callback(choice):
        global chart_infill_color
        global chart_text_color
        if choice == "Dark":
            appearance_mode = "Dark"
            chart_infill_color = "#2b2b2b"
            chart_text_color = "white"
        else:
            appearance_mode = "Light"
            chart_infill_color = "#dbdbdb"
            chart_text_color = "black"
        settings["appearance"]["mode"] = appearance_mode
        with open(cp.SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        customtkinter.set_appearance_mode(appearance_mode)
        refresh_chart()

    def logging_switch_event():
        print("logging_switch toggled, current value:", logging_switch_var.get()) 
        if logging_switch_var == 'off':
            config["logging"]["enabled"] = False
        else:
            config["logging"]["enabled"] = True
        with open(cp.CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def reset_statistics():
        app_log_dir = cp.LOG_PATH / "app.log"
        suffix_log_dir = cp.LOG_PATH / "suffix.log"

        warn_fenster = customtkinter.CTkToplevel(app)
        warn_fenster.title("Warnung!")
        warn_fenster.geometry("350x150")
        
        warn_fenster.attributes("-topmost", True)
        
        warn_fenster.grid_columnconfigure((0, 1), weight=1)
        warn_fenster.grid_rowconfigure((0, 1), weight=1)

        warn_label = customtkinter.CTkLabel(
            master=warn_fenster, 
            text="Achtung: Das zurücksetzten der\n Statistik löscht alle logs.\n Dieser Vorgang kann nicht\n rückgängig gemacht werden!",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color="#ff4444"
        )
        warn_label.grid(row=0, column=0, columnspan=2, padx=20, pady=10)

        cancel_button = customtkinter.CTkButton(
            master=warn_fenster, 
            text="Abbrechen", 
            command=warn_fenster.destroy
        )
        cancel_button.grid(row=1, column=0, padx=20, pady=10)

        reset_button = customtkinter.CTkButton(
            master=warn_fenster, 
            text="Zurücksetzen", 
            command=lambda: [app_log_dir.unlink(), suffix_log_dir.unlink(), refresh_chart(), print("Statistics successfully reset")]
        )
        reset_button.grid(row=1, column=1, padx=20, pady=10)

    tabview = customtkinter.CTkTabview(app)
    tabview.grid(row=0, column=0, rowspan=3, columnspan=5, sticky="nsew", padx=20, pady=10)

    tabview.add("Übersicht")
    tabview.add("Statistik")
    tabview.add("Einstellungen")
    tabview.set("Übersicht")

    tabview.tab("Übersicht").grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
    tabview.tab("Übersicht").grid_rowconfigure((0, 1, 2,), weight=1)

    tabview.tab("Statistik").grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
    tabview.tab("Statistik").grid_rowconfigure((0, 1, 2,), weight=1)

    tabview.tab("Einstellungen").grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
    tabview.tab("Einstellungen").grid_rowconfigure((0, 1, 2, 3 , 4), weight=1)

    chart_frame = customtkinter.CTkFrame(tabview.tab("Statistik"))
    chart_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    fig, ax = plt.subplots(figsize=(3, 3), dpi=100)

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill="both", expand=True)

    def refresh_chart():
        ax.clear()
        
        log_path = cp.LOG_PATH
        suffix_log_path = cp.LOG_PATH / "suffix.log"

        if suffix_log_path.exists():
            with open(suffix_log_path, "r", encoding="utf-8") as f:
                endungen = [line.strip().lower() for line in f if line.strip()]
        else:
            endungen = []

        anzahl_pro_endung = Counter(endungen)
        gesamt_anzahl = len(endungen)
        top_endungen = anzahl_pro_endung.most_common(4)

        kategorien = []
        prozent_werte = []
        prozent_labels = []

        if gesamt_anzahl > 0:
            for endung, anzahl in top_endungen:
                prozent = (anzahl / gesamt_anzahl) * 100
                kategorien.append(endung)
                prozent_werte.append(prozent)
                prozent_labels.append(f"{prozent:.1f}%")
        else:
            kategorien = ["Keine Daten"]
            prozent_werte = [0]
            prozent_labels = ["0.0%"]

        fig.patch.set_facecolor(chart_infill_color)
        ax.set_facecolor(chart_infill_color)

        balken_farben = ['#1f538d', '#a21f1f', '#1fa253', '#dca11d']
        balken = ax.bar(kategorien, prozent_werte, width=0.40, color=balken_farben[:len(kategorien)], edgecolor='none')

        for bar in balken:
            bar.set_capstyle('round')
            bar.set_linewidth(6)
            bar.set_edgecolor(bar.get_facecolor())
            bar.set_joinstyle('round')

        ax.bar_label(balken, labels=prozent_labels, padding=6, color=chart_text_color)
        ax.tick_params(colors=chart_text_color)
        ax.spines['bottom'].set_color(chart_text_color)
        ax.spines['left'].set_color(chart_text_color)
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')

        ax.set_ylim(0, 60)
        ax.yaxis.set_major_formatter(lambda x, pos: f'{x:.0f}%')

        canvas.draw()

    logging_switch = customtkinter.CTkSwitch(master=tabview.tab("Einstellungen"),
                                            text="erstelle logs", 
                                            command=logging_switch_event,
                                            variable=logging_switch_var, 
                                            onvalue="on", 
                                            offvalue="off")
    logging_switch.grid(row=4, column=4, padx=0, pady=0)

    reset_statistics_button = customtkinter.CTkButton(master=tabview.tab("Statistik"), 
                                                    text="Statistik zurücksetzen", 
                                                    command=reset_statistics)
    reset_statistics_button.grid(row=0, column=4, padx=20, pady=20)

    appearance_mode_optionmenu_var = customtkinter.StringVar(value=appearance_mode)
    appearance_mode_optionmenu = customtkinter.CTkOptionMenu(master=tabview.tab("Einstellungen"),
                                                            values=["Dark", "Light"],
                                                            command=appearance_mode_optionmenu_callback,
                                                            variable=appearance_mode_optionmenu_var)
    appearance_mode_optionmenu.grid(row=0, column=0, padx=20, pady=20)

    appearance_color_theme_optionmenu_var = customtkinter.StringVar(value=color_theme)
    appearance_color_theme_optionmenu = customtkinter.CTkOptionMenu(master=tabview.tab("Einstellungen"),
                                                                    values=["blue", "dark-blue", "green"],
                                                                    command=appearance_color_theme_optionmenu_callback,
                                                                    variable=appearance_color_theme_optionmenu_var)
    appearance_color_theme_optionmenu.grid(row=1, column=0, padx=20, pady=20)

    restart_button = customtkinter.CTkButton(master=tabview.tab("Einstellungen"),
                                            text="App neu starten",
                                            hover_color="#ff4444",
                                            command=restart_app
    )
    restart_button.grid(row=2, column=0, padx=20, pady=20)

    quit_app_button = customtkinter.CTkButton(master=tabview.tab("Einstellungen"),
                                            text="App beenden",
                                            hover_color="#ff4444",
                                            command=lambda: [app.quit(), app.destroy()]
    )
    quit_app_button.grid(row=0, column=4, padx=20, pady=20)

    dnd_frame = customtkinter.CTkFrame(master=tabview.tab("Übersicht"),
                                    fg_color=("#dbdbdb", "#2b2b2b"),
                                    border_color=("#979da2", "#1f538d"),
                                    border_width=2,
                                    corner_radius=12
    )
    dnd_frame.grid(row=0, column=0, rowspan=3, columnspan=3, sticky="nsew", padx=40, pady=40)
    dnd_frame.grid_rowconfigure(0, weight=1)
    dnd_frame.grid_columnconfigure(0, weight=1)

    dnd_label = customtkinter.CTkLabel(master=dnd_frame,
                                    text="📂 Dateien oder Ordner hierher ziehen",
                                    font=customtkinter.CTkFont(size=16, weight="bold")
    )
    dnd_label.grid(row=0, column=0)

    dnd_frame.drop_target_register(DND_FILES)
    dnd_frame.dnd_bind('<<Drop>>', datei_gedroppt)

    watcher_switch = customtkinter.CTkSwitch(master=tabview.tab("Einstellungen"),
                                            text="Datei-Beobachter aktivieren", 
                                            command=watcher_switch_event,
                                            variable=watcher_switch_var, 
                                            onvalue="on", 
                                            offvalue="off")
    watcher_switch.grid(row=1, column=4, padx=0, pady=0)


    refresh_chart()

    if settings["watcher"]["enabled"]:
        python_exe = sys.executable
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.Popen(
            [str(python_exe), str(code_dir / "watcher.py")],
            startupinfo=startupinfo
        )

    app.mainloop()




'''
custom_color_entry = customtkinter.CTkEntry(master=tabview.tab("Einstellungen"), 
                                            placeholder_text="Eigene Farbe (z.B. #1f1f1f)")
custom_color_entry.grid(row=3, column=0, padx=20, pady=20)

def set_custom_color():
    color_theme = custom_color_entry.get().strip()

    hex_muster = re.compile(r"^#[0-9a-fA-F]{6}$")
    
    if hex_muster.match(color_theme):
        custom_color_entry.configure(border_color="#565b5e")

        settings["appearance"]["custom_color"] = color_theme
        with open(cp.SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        
        print(f"Erfolgreich gespeichert: {color_theme}")
        customtkinter.set_default_color_theme(color_theme)
    else:
        custom_color_entry.configure(border_color="#ff4444")

set_custom_color_entry = customtkinter.CTkButton(master=tabview.tab("Einstellungen"),
                                                 text="Enter",
                                                 command=set_custom_color)
set_custom_color_entry.grid(row=4, column=0, padx=20, pady=20)
'''





'''
log_path = cp.LOG_PATH
suffix_log_path = cp.LOG_PATH / "suffix.log"

if suffix_log_path.exists():
    with open(suffix_log_path, "r", encoding="utf-8") as f:
        # Liest alle Zeilen, entfernt Leerzeichen/Absätze und ignoriert leere Zeilen
        endungen = [line.strip().lower() for line in f if line.strip()]
else:
    endungen = []

# 2. Häufigkeiten zählen und Gesamtzahl ermitteln
anzahl_pro_endung = Counter(endungen)
gesamt_anzahl = len(endungen)

# 3. Die häufigsten Endungen für das Diagramm vorbereiten
top_endungen = anzahl_pro_endung.most_common(4)

kategorien = []
werte = []
prozent_labels = []

for endung, anzahl in top_endungen:
    # Prozentwert berechnen (Anteil an der Gesamtzahl)
    prozent = (anzahl / gesamt_anzahl) * 100
    
    kategorien.append(endung)
    werte.append(anzahl)  # Die Höhe der Balken (Anzahl)
    prozent_labels.append(f"{prozent:.1f}%")  # Für die spätere Beschriftung

print(kategorien, "\n", werte, "\n", prozent_labels)


# Frame für das Diagramm erstellen
chart_frame = customtkinter.CTkFrame(app)

# Füge das Frame in die nächste freie Reihe (z. B. row=2) ein
chart_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)

# Wichtig: Damit das Diagramm mitskaliert, wenn das Fenster vergrößert wird:
app.grid_rowconfigure(2, weight=1)
app.grid_columnconfigure(0, weight=1)


# Figur und Achsen erzeugen
fig, ax = plt.subplots(figsize=(5, 4), dpi=100)

# Farben an den CTk Dark-Mode anpassen (#242424 ist das Standard-CTk-Dunkel)
fig.patch.set_facecolor('#242424')
ax.set_facecolor('#2b2b2b')

# Balken zeichnen
ax.bar(kategorien, werte, color='#1f538d', edgecolor='white')

# Texte und Achsen weiß färben
ax.tick_params(colors='white')
ax.spines['bottom'].set_color('white')
ax.spines['left'].set_color('white')
ax.spines['top'].set_color('none')  # Obere Rahmenlinie ausblenden
ax.spines['right'].set_color('none')  # Rechte Rahmenlinie ausblenden


# 3. Diagramm in CustomTkinter einbetten
canvas = FigureCanvasTkAgg(fig, master=chart_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill="both", expand=True)

# Grafik rendern
canvas.draw()
'''
'''
# 1. Daten auslesen und vorbereiten
log_path = cp.LOG_PATH
suffix_log_path = cp.LOG_PATH / "suffix.log"

if suffix_log_path.exists():
    with open(suffix_log_path, "r", encoding="utf-8") as f:
        # Liest alle Zeilen, entfernt Leerzeichen/Absätze und ignoriert leere Zeilen
        endungen = [line.strip().lower() for line in f if line.strip()]
else:
    endungen = []

# Häufigkeiten zählen und Gesamtzahl ermitteln
anzahl_pro_endung = Counter(endungen)
gesamt_anzahl = len(endungen)

# Die häufigsten Endungen für das Diagramm vorbereiten
top_endungen = anzahl_pro_endung.most_common(4)

kategorien = []
prozent_werte = []  # Speichert die reinen Prozentzahlen für die Balkenhöhe
prozent_labels = []

# Falls die Datei leer ist, Division durch Null verhindern
if gesamt_anzahl > 0:
    for endung, anzahl in top_endungen:
        # Prozentwert berechnen (Anteil an der Gesamtzahl)
        prozent = (anzahl / gesamt_anzahl) * 100
        
        kategorien.append(endung)
        prozent_werte.append(prozent)  # Prozentwert bestimmt die Höhe
        prozent_labels.append(f"{prozent:.1f}%")  # Text für die Beschriftung
else:
    kategorien = ["Keine Daten"]
    prozent_werte = [0]
    prozent_labels = ["0.0%"]

print(kategorien, "\n", prozent_werte, "\n", prozent_labels)


# 2. GUI Frame für das Diagramm erstellen
chart_frame = customtkinter.CTkFrame(app)

# Füge das Frame in die nächste freie Reihe (z. B. row=2) ein
chart_frame.grid(row=0, column=4, columnspan=1, sticky="nsew", padx=20, pady=10)

# 3. Matplotlib Diagramm konfigurieren und zeichnen
# Figur und Achsen erzeugen
fig, ax = plt.subplots(figsize=(3, 2), dpi=100)

# Farben an den CTk Dark-Mode anpassen (#242424 ist das Standard-CTk-Dunkel)
fig.patch.set_facecolor('#242424')
ax.set_facecolor('#2b2b2b')

# Farbpalette für die unterschiedlichen Balken definieren
balken_farben = ["#2669b6", '#a21f1f', '#1fa253', '#dca11d']

# Balken zeichnen 
# -> width=0.40 macht die Balken schmaler
# -> edgecolor='none' entfernt den weißen Rand
balken = ax.bar(kategorien, prozent_werte, width=0.40, color=balken_farben[:len(kategorien)], edgecolor='none')

# --- ÄNDERUNG: Ecken oben abrunden ---
# Wir laufen durch jeden gezeichneten Balken und verpassen ihm runde Ecken am oberen Ende
for bar in balken:
    bar.set_capstyle('round')
    # Um echte glatte "Säulen-Ecken" zu generieren, setzen wir den Pfad-Join auf 'round'
    # und geben dem Balken eine unsichtbare, gleichfarbige dicke Linie an der Oberseite
    bar.set_linewidth(6)
    bar.set_edgecolor(bar.get_facecolor())
    bar.set_joinstyle('round')

# Prozentwerte als Text direkt über die Balken schreiben
ax.bar_label(balken, labels=prozent_labels, padding=6, color='white')

# Texte und Achsen weiß färben
ax.tick_params(colors='white')
ax.spines['bottom'].set_color('white')
ax.spines['left'].set_color('white')
ax.spines['top'].set_color('none')  # Obere Rahmenlinie ausblenden
ax.spines['right'].set_color('none')  # Rechte Rahmenlinie ausblenden

# Y-Achse auf maximal 100% begrenzen und formatieren
ax.set_ylim(0, 60)
ax.yaxis.set_major_formatter(lambda x, pos: f'{x:.0f}%')


# 4. Diagramm in CustomTkinter einbetten
canvas = FigureCanvasTkAgg(fig, master=chart_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill="both", expand=True)

# Grafik rendern
canvas.draw()
'''