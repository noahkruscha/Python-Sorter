import customtkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from pathlib import Path
import sys
from collections import Counter
import config_paths as cp

app = customtkinter.CTk()
tabview = customtkinter.CTkTabview(master=app)
tabview.pack(padx=20, pady=20)

tabview.add("tab 1")
tabview.add("tab 2")
tabview.set("tab 2")

button = customtkinter.CTkButton(master=tabview.tab("tab 1"))
button.pack(padx=20, pady=20)

app.mainloop()