import logging

logger = logging.getLogger(__name__)


def parse_text(filepath, mime=None):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        return {
            "extract_type": "text",
            "text": text,
            "hex_preview": None,
            "metadata": {"mime": mime or "text/plain"},
        }
    except Exception as e:
        logger.exception("Failed to parse text file %s: %s", filepath, e)
        return None
