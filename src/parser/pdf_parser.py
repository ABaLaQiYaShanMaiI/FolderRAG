from pdfminer.high_level import extract_text

def parse_pdf(filepath):
    try:
        text = extract_text(filepath)
        return {
            "extract_type": "text",
            "text": text,
            "hex_preview": None,
            "metadata": {"mime": "application/pdf"},
        }
    except Exception:
        return None
