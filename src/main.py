import os
import sys
from pathlib import Path

# Add src to python path to allow imports from other directories in src
sys.path.append(os.path.join(os.path.dirname(__file__)))

import threading
from src.watcher import FolderWatcher
from src.api.server import create_app
from src.vector_store import VectorStore
from src.embedder import Embedder
from src.chunker import Chunker
from dotenv import load_dotenv
import yaml
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
load_dotenv()


def load_config():
    # Use absolute path based on this file's location: src/main.py -> FolderRAG/config.yaml
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()
    watch_dir = os.getenv("WATCH_DIR", "./watch_folder")
    os.makedirs(watch_dir, exist_ok=True)

    embedder = Embedder(config["embedder"])
    chunker = Chunker(config["chunk"])
    vector_store = VectorStore(config["vector_store"])

    watcher = FolderWatcher(
        watch_dir=watch_dir,
        config=config,
        embedder=embedder,
        chunker=chunker,
        vector_store=vector_store,
    )

    # Start watcher in a daemon thread (watchdog runs its own thread)
    t = threading.Thread(target=watcher.run, daemon=True)
    t.start()

    app = create_app(vector_store, embedder)

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
