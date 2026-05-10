def parse_text(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        return {
            "extract_type": "text",
            "text": text,
            "hex_preview": None,
            "metadata": {"mime": "text/plain"},
        }
    except Exception:
        return None
