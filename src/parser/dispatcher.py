import os
from .text_parser import parse_text
from .pdf_parser import parse_pdf
from .office_parser import parse_office
from .binary_parser import parse_binary

# Module-level singleton for magic.Magic to avoid repeated instantiation
import magic
_magic = magic.Magic(mime=True)


def parse_file(filepath, config):
    if not os.path.isfile(filepath):
        return None
    mime = _magic.from_file(filepath)
    if mime:
        if mime.startswith("text/"):
            return parse_text(filepath)
        elif mime == "application/pdf":
            return parse_pdf(filepath)
        elif mime in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        ]:
            return parse_office(filepath, "docx")
        elif mime in [
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/vnd.ms-powerpoint",
        ]:
            return parse_office(filepath, "pptx")
        elif mime in [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
        ]:
            return parse_office(filepath, "xlsx")
    # Default: binary handler
    return parse_binary(filepath, config)
