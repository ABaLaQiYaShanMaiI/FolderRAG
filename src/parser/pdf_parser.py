import logging
from pdfminer.high_level import extract_text

logger = logging.getLogger(__name__)


def parse_pdf(filepath):
    try:
        text = extract_text(filepath)
        return {
            "extract_type": "text",
            "text": text,
            "metadata": {"mime": "application/pdf"},
        }
    except Exception as e:
        logger.exception("Failed to parse PDF file %s: %s", filepath, e)
        return None
