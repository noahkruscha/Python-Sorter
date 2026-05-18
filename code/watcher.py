from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import config_paths as cp
import sorter
import time

# Event Handler
class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        time.sleep(0.5)
        sorter.sort_file(file_path)
        

# observer starten
observer = Observer()
event_handler = Handler()
observer.schedule(event_handler, cp.EVENT_DIR, recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    observer.stop()

observer.join()