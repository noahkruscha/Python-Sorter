import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import config_paths as cp
import sorter
import time

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        time.sleep(0.5)
        sorter.sort_file(file_path)

if __name__ == "__main__":
    pid_file = cp.LOG_PATH / "watcher.pid"
    pid_file.write_text(str(os.getpid()))

    print(f"Watching: {cp.EVENT_DIR}")  # <- existiert der Pfad?
    print(f"PID: {os.getpid()}")

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
