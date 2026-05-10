import os
import hashlib
import threading
from pathlib import Path
from datetime import datetime, timezone
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from parser import parse_file
from embedder import Embedder
from chunker import Chunker
from vector_store import VectorStore
import logging

logger = logging.getLogger(__name__)


class DebouncedHandler:
    """Mixin for debouncing file system events."""

    def __init__(self, debounce_seconds: float = 1.0):
        self._debounce_seconds = debounce_seconds
        self._timers = {}
        self._lock = threading.Lock()

    def _debounce(self, filepath: str, callback):
        """Delay processing of a file, resetting the timer on each call."""
        with self._lock:
            # Cancel existing timer for this filepath
            if filepath in self._timers:
                self._timers[filepath].cancel()
            # Create a new timer
            timer = threading.Timer(self._debounce_seconds, callback)
            timer.daemon = True
            self._timers[filepath] = timer
            timer.start()

    def _cleanup_timer(self, filepath: str):
        with self._lock:
            self._timers.pop(filepath, None)


class FileChangeHandler(FileSystemEventHandler, DebouncedHandler):
    def __init__(self, watch_dir, chunker, embedder, vector_store, config):
        FileSystemEventHandler.__init__(self)
        DebouncedHandler.__init__(self, debounce_seconds=1.0)
        self.watch_dir = watch_dir
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store
        self.config = config

    def on_created(self, event):
        if not event.is_directory:
            self._debounce(event.src_path, lambda: self.process_file(event.src_path))

    def on_modified(self, event):
        if not event.is_directory:
            self._debounce(event.src_path, lambda: self.process_file(event.src_path))

    def process_file(self, filepath):
        try:
            # Clean up the debounce timer entry
            self._cleanup_timer(filepath)

            filepath = os.path.abspath(filepath)
            if not os.path.isfile(filepath):
                return
            # Skip hidden files or system files
            if os.path.basename(filepath).startswith('.'):
                return
            logger.info(f"Processing file: {filepath}")

            # Compute file hash BEFORE parsing to check for duplicates
            file_hash = self.hash_file(filepath)

            # Check if this file content has already been indexed (hash dedup)
            stored_hash = self.vector_store.get_file_hash(source=filepath)
            if stored_hash == file_hash:
                logger.info(f"Skipping {filepath}: content unchanged (hash: {file_hash[:8]}...)")
                return

            parsed = parse_file(filepath, self.config)
            if not parsed:
                return

            modified_at = datetime.fromtimestamp(os.path.getmtime(filepath), tz=timezone.utc).isoformat()
            # Upsert with metadata
            self.vector_store.upsert_file(
                source=filepath,
                file_hash=file_hash,
                modified_at=modified_at,
                parsed_data=parsed,
                chunker=self.chunker,
                embedder=self.embedder,
            )
        except Exception as e:
            logger.exception(f"Error processing {filepath}: {e}")

    @staticmethod
    def hash_file(filepath):
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()


class FolderWatcher:
    def __init__(self, watch_dir, config, embedder, chunker, vector_store):
        self.watch_dir = watch_dir
        self.config = config
        self.embedder = embedder
        self.chunker = chunker
        self.vector_store = vector_store
        self._observer = None

    def run(self):
        event_handler = FileChangeHandler(
            self.watch_dir, self.chunker, self.embedder, self.vector_store, self.config
        )
        observer = Observer()
        self._observer = observer
        observer.schedule(event_handler, self.watch_dir, recursive=True)
        observer.start()
        logger.info(f"Started watching directory: {self.watch_dir}")
        # observer.join() blocks the current thread; since this is called from
        # a daemon thread in main.py, KeyboardInterrupt goes to the main thread (uvicorn),
        # so the try/except here would never fire. Use observer.join() without
        # catching KeyboardInterrupt - the observer stops when the process exits.
        observer.join()

    def stop(self):
        """Stop the observer. Called from the main thread on shutdown."""
        if self._observer is not None:
            self._observer.stop()
            self._observer.join()
            logger.info("Folder watcher stopped.")
