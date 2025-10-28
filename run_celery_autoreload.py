# run_celery_autoreload.py
import subprocess
import sys
import time
import signal
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CeleryAutoReload:
    def __init__(self):
        self.celery_process = None
        self.observer = Observer()
        self.restart_required = False
        
    def start_celery(self):
        """Start the Celery worker process"""
        print("🚀 Starting Celery worker...")
        self.celery_process = subprocess.Popen([
            sys.executable, '-m', 'celery', 
            '-A', 'celery_app', 
            'worker', 
            '--loglevel=info',
            '--concurrency=1'
        ])
        
    def stop_celery(self):
        """Stop the Celery worker process"""
        if self.celery_process:
            print("🛑 Stopping Celery worker...")
            self.celery_process.terminate()
            try:
                self.celery_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print("⚠️  Force killing Celery...")
                self.celery_process.kill()
                
    def restart_celery(self):
        """Restart Celery worker"""
        self.stop_celery()
        time.sleep(2)  # Give it time to clean up
        self.start_celery()

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, reloader):
        self.reloader = reloader
        self.debounce_seconds = 1
        self.last_trigger = 0
        
    def on_modified(self, event):
        if event.src_path.endswith('.py') and not event.src_path.endswith('.pyc'):
            current_time = time.time()
            # Debounce to avoid multiple rapid triggers
            if current_time - self.last_trigger > self.debounce_seconds:
                self.last_trigger = current_time
                print(f"🔄 File changed: {os.path.basename(event.src_path)}")
                self.reloader.restart_celery()

def main():
    reloader = CeleryAutoReload()
    event_handler = FileChangeHandler(reloader)
    
    # Start watching for file changes
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    
    # Initial start
    reloader.start_celery()
    
    print("👀 Auto-reload enabled! Watching for file changes...")
    print("💡 Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        observer.stop()
        reloader.stop_celery()
    
    observer.join()

if __name__ == "__main__":
    main()