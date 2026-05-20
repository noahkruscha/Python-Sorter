import os
import config_paths as cp
from ui import gui

os.environ['TKDND_LIBRARY'] = os.path.join(cp.BASE_DIR.parent,
                                           'python_env',
                                           'libs',
                                           'tkinterdnd2',
                                           'tkdnd'
)

gui.start_gui()