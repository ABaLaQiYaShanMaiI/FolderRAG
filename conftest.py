"""Root conftest: ensures src/ is discoverable for module-level imports like `from vector_store import VectorStore`."""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))
