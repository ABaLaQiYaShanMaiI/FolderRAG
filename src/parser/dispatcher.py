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

# Configuration for Office parser behavior
# These defaults can be overridden via environment variables or direct import.
# For Chinese writing knowledge bases, tables are filtered by default.
OFFICE_INCLUDE_TABLES = os.environ.get('OFFICE_INCLUDE_TABLES', '0') == '1'
OFFICE_INCLUDE_HEADERS_FOOTERS = os.environ.get('OFFICE_INCLUDE_HEADERS_FOOTERS', '0') == '1'
OFFICE_INCLUDE_FOOTNOTES = os.environ.get('OFFICE_INCLUDE_FOOTNOTES', '0') == '1'
OFFICE_ANNOTATE_STYLES = os.environ.get('OFFICE_ANNOTATE_STYLES', '1') == '1'
OFFICE_EXTRACT_PPT_NOTES = os.environ.get('OFFICE_EXTRACT_PPT_NOTES', '0') == '1'
OFFICE_MAX_ROWS_XLSX = int(os.environ.get('OFFICE_MAX_ROWS_XLSX', '10000'))


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


def parse_file(filepath, **kwargs):
    """Dispatch a file to the appropriate parser based on MIME type.
    
    Args:
        filepath: Path to the file to parse.
        **kwargs: Additional arguments passed to parse_office() when applicable.
            - include_tables: bool (default from OFFICE_INCLUDE_TABLES env var)
            - include_headers_footers: bool
            - include_footnotes: bool
            - annotate_styles: bool
            - extract_ppt_notes: bool
            - max_rows_xlsx: int
    
    Returns:
        Dict with keys: extract_type, text, metadata
        Or None if file cannot be parsed.
    """
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

    # Collect office parser arguments from kwargs + env defaults
    office_kwargs = {
        'include_tables': kwargs.get('include_tables', OFFICE_INCLUDE_TABLES),
        'include_headers_footers': kwargs.get('include_headers_footers', OFFICE_INCLUDE_HEADERS_FOOTERS),
        'include_footnotes': kwargs.get('include_footnotes', OFFICE_INCLUDE_FOOTNOTES),
        'annotate_styles': kwargs.get('annotate_styles', OFFICE_ANNOTATE_STYLES),
        'extract_ppt_notes': kwargs.get('extract_ppt_notes', OFFICE_EXTRACT_PPT_NOTES),
        'max_rows_xlsx': kwargs.get('max_rows_xlsx', OFFICE_MAX_ROWS_XLSX),
    }

    # MIME-based dispatch
    if mime:
        if mime.startswith("text/"):
            return parse_text(filepath, mime)
        elif mime == "application/pdf":
            return parse_pdf(filepath)
        elif mime in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        ]:
            filetype = "doc" if mime == "application/msword" else "docx"
            return parse_office(filepath, filetype, **office_kwargs)
        elif mime in [
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/vnd.ms-powerpoint",
        ]:
            filetype = "ppt" if mime == "application/vnd.ms-powerpoint" else "pptx"
            return parse_office(filepath, filetype, **office_kwargs)
        elif mime in [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
        ]:
            filetype = "xls" if mime == "application/vnd.ms-excel" else "xlsx"
            return parse_office(filepath, filetype, **office_kwargs)
    
    # Extension-based dispatch for formats python-magic may not identify
    # This handles legacy formats (.doc, .ppt, .xls) when magic is unavailable,
    # WPS-specific formats (.wps, .et, .dps),
    # and modern Office formats (.docx, .pptx, .xlsx) as a fallback
    # when python-magic is not available or returns non-standard MIME types.
    if ext in ('.doc', '.ppt', '.xls', '.wps', '.et', '.dps',
               '.docx', '.pptx', '.xlsx'):
        filetype_map = {
            '.doc': 'doc', '.ppt': 'ppt', '.xls': 'xls',
            '.wps': 'wps', '.et': 'et', '.dps': 'dps',
            '.docx': 'docx', '.pptx': 'pptx', '.xlsx': 'xlsx',
        }
        ft = filetype_map.get(ext, ext.lstrip('.'))
        logger.debug("Extension-based Office/WPS dispatch for %s (type=%s)", filepath, ft)
        return parse_office(filepath, ft, **office_kwargs)

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