import os
import hashlib
import json
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

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, watch_dir, chunker, embedder, vector_store, config):
        super().__init__()
        self.watch_dir = watch_dir
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store
        self.config = config

    def on_created(self, event):
        if not event.is_directory:
            self.process_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.process_file(event.src_path)

    def process_file(self, filepath):
        try:
            filepath = os.path.abspath(filepath)
            if not os.path.isfile(filepath):
                return
            # Check if file should be processed
            # Skip hidden files or system files
            if os.path.basename(filepath).startswith('.'):
                return
            logger.info(f"Processing file: {filepath}")
            parsed = parse_file(filepath, self.config)
            if not parsed:
                return
            file_hash = self.hash_file(filepath)
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

    def run(self):
        event_handler = FileChangeHandler(
            self.watch_dir, self.chunker, self.embedder, self.vector_store, self.config
        )
        observer = Observer()
        observer.schedule(event_handler, self.watch_dir, recursive=True)
        observer.start()
        logger.info(f"Started watching directory: {self.watch_dir}")
        try:
            # Keep the thread alive; watchdog's own threads will handle events
            observer.join()
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
