import logging

logger = logging.getLogger(__name__)


def parse_text(filepath, mime=None):
    # Try multiple encodings for Chinese Windows compatibility
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            with open(filepath, "r", encoding=enc) as f:
                text = f.read()
            break
        except UnicodeDecodeError:
            continue
    else:
        # All encodings failed — fallback with error replacement
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except Exception as e:
            logger.exception("Failed to parse text file %s: %s", filepath, e)
            return None

    return {
        "extract_type": "text",
        "text": text,
        "metadata": {"mime": mime or "text/plain"},
    }
