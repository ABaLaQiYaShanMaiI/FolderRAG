import os
import logging
from .text_parser import parse_text
from .pdf_parser import parse_pdf
from .office_parser import parse_office

# Graceful fallback if python-magic is not installed or fails to load.
# We catch *all* exceptions because magic can raise:
#   - ImportError: not installed
#   - AttributeError: version mismatch (e.g., python-magic d0.4.24 lacks Magic)
#   - OSError/FileNotFoundError: shared library (libmagic) not found on system
#   - ctypes.CDLL error on Windows: bundled magic1.dll missing/corrupt
try:
    import magic
    _magic = magic.Magic(mime=True)
except Exception:
    magic = None
    _magic = None
    import logging as _logging
    _logging.getLogger(__name__).debug(
        "python-magic not available (or failed to load). "
        "Falling back to extension-based dispatch."
    )

logger = logging.getLogger(__name__)

# Common code/text file extensions that should be parsed as text even if
# python-magic doesn't identify them as text/ MIME type.
# This ensures .cs, .swift, .kt, and other code files are always handled.
# NOTE: Now sourced from src.constants.SUPPORTED_TEXT_EXTS for consistency.
try:
    from src.constants import SUPPORTED_TEXT_EXTS, KNOWN_BINARY_EXTS as CONST_BINARY_EXTS
    _FALLBACK_TEXT_EXTS = SUPPORTED_TEXT_EXTS
    _KNOWN_BINARY_EXTS = CONST_BINARY_EXTS
except ImportError:
    # Fallback if running as standalone
    _FALLBACK_TEXT_EXTS = frozenset({'.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.json', '.xml', '.csv', '.yaml', '.yml', '.log', '.ini', '.cfg', '.conf', '.cs', '.java', '.cpp', '.h'})
    _KNOWN_BINARY_EXTS = frozenset({
        '.pt', '.pth', '.pkl', '.joblib', '.onnx', '.h5', '.hdf5', '.hdf',
        '.pb', '.meta', '.index', '.data-00000-of-00001',
        '.npy', '.npz', '.bin', '.dat', '.raw',
        '.caffemodel', '.weights',
        '.zip', '.gz', '.bz2', '.xz', '.tar', '.7z', '.rar',
        '.so', '.dll', '.dylib', '.exe', '.msi', '.dmg',
        '.o', '.obj', '.a', '.lib', '.pyc', '.pyo', '.class',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
        '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac',
    })


def _should_try_text_fallback(filepath: str) -> bool:
    """Check if a file should be attempted as text based on extension."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in _KNOWN_BINARY_EXTS:
        return False
    if ext in _FALLBACK_TEXT_EXTS:
        return True
    # For unknown extensions, try to read a small sample to see if it's text
    try:
        with open(filepath, 'rb') as f:
            sample = f.read(8192)
        # Check if it's mostly printable ASCII / UTF-8
        try:
            sample.decode('utf-8')
            return True
        except UnicodeDecodeError:
            # Try latin-1 (all byte values valid)
            decoded = sample.decode('latin-1')
            # Count printable characters
            printable = sum(1 for c in decoded if c.isprintable() or c in '\n\r\t')
            if len(sample) > 0 and printable / len(sample) > 0.9:
                return True
    except Exception:
        pass
    return False


def parse_file(filepath):
    """Dispatch a file to the appropriate parser based on MIME type."""
    if not os.path.isfile(filepath):
        return None
    
    ext = os.path.splitext(filepath)[1].lower()
    
    # Skip known binary files early
    if ext in _KNOWN_BINARY_EXTS:
        logger.debug("Skipping known binary file: %s", filepath)
        return None
    
    # Try MIME-based dispatch (gracefully handle missing or broken python-magic).
    mime = None
    if _magic is not None:
        try:
            mime = _magic.from_file(filepath)
        except Exception:
            mime = None
            logger.debug("magic.from_file() failed for %s, falling back to extension", filepath)

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
    
    # Extension-based fallback: try to parse as text for known code/text extensions.
    # This handles .cs, .swift, .kt, csproj, sln, xaml, and other code files
    # where magic might return unexpected MIME types (e.g., application/octet-stream)
    # or simply crash (MagicException for .cs on some Windows setups).
    if _should_try_text_fallback(filepath):
        logger.debug("Trying text fallback for %s (mime=%s, ext=%s)", filepath, mime, ext)
        try:
            result = parse_text(filepath, mime)
            if result and result.get("text", "").strip():
                return result
        except Exception as e:
            logger.debug("Text fallback failed for %s: %s", filepath, e)
    
    return None