import os
import logging
import magic
from .text_parser import parse_text
from .pdf_parser import parse_pdf
from .office_parser import parse_office

_magic = magic.Magic(mime=True)

logger = logging.getLogger(__name__)


def parse_file(filepath):
    """Dispatch a file to the appropriate parser based on MIME type."""
    if not os.path.isfile(filepath):
        return None
    mime = _magic.from_file(filepath)
    if mime:
        if mime.startswith("text/"):
            return parse_text(filepath, mime)
        elif mime == "application/pdf":
            return parse_pdf(filepath)
        elif mime in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        ]:
            if mime == "application/msword":
                logger.warning(
                    "Legacy .doc format detected: %s. python-docx cannot parse old .doc files. "
                    "Consider converting to .docx.", filepath
                )
            return parse_office(filepath, "docx")
        elif mime in [
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/vnd.ms-powerpoint",
        ]:
            if mime == "application/vnd.ms-powerpoint":
                logger.warning(
                    "Legacy .ppt format detected: %s. python-pptx cannot parse old .ppt files. "
                    "Consider converting to .pptx.", filepath
                )
            return parse_office(filepath, "pptx")
        elif mime in [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
        ]:
            if mime == "application/vnd.ms-excel":
                logger.warning(
                    "Legacy .xls format detected: %s. openpyxl cannot parse old .xls files. "
                    "Consider converting to .xlsx.", filepath
                )
            return parse_office(filepath, "xlsx")
    # Unsupported file type – skip silently
    return None
