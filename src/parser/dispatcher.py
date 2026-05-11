import os
import logging
import magic
from .text_parser import parse_text
from .pdf_parser import parse_pdf
from .office_parser import parse_office

_magic = magic.Magic(mime=True)

logger = logging.getLogger(__name__)

# Common code/text file extensions that should be parsed as text even if
# python-magic doesn't identify them as text/ MIME type.
# This ensures .cs, .swift, .kt, and other code files are always handled.
_FALLBACK_TEXT_EXTS = frozenset({
    # C-family
    '.c', '.h', '.cpp', '.hpp', '.cc', '.cxx', '.hh', '.hxx',
    '.cs', '.fs', '.vb',
    # Java & JVM
    '.java', '.kt', '.scala', '.groovy', '.clj', '.cljs',
    # Python
    '.py', '.pyw', '.pyx', '.pxd', '.pxi',
    # Web
    '.js', '.jsx', '.ts', '.tsx', '.html', '.htm', '.xhtml',
    '.css', '.scss', '.less', '.sass',
    # Scripting
    '.sh', '.bash', '.zsh', '.fish', '.ps1', '.psm1', '.psd1',
    '.bat', '.cmd', '.vbs', '.pl', '.pm', '.tcl', '.lua',
    '.rb', '.php', '.phtml', '.php3', '.php4', '.php5',
    '.r', '.R', '.m', '.mm',
    # Functional
    '.hs', '.lhs', '.erl', '.hrl', '.ex', '.exs', '.elm',
    # Mobile
    '.swift', '.dart',
    # Go / Rust
    '.go', '.rs',
    # SQL
    '.sql', '.ddl', '.dml',
    # Config / text
    '.md', '.markdown', '.rst', '.txt', '.text',
    '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
    '.csv', '.tsv', '.log',
    # Training / ML text files
    '.cfg', '.weights', '.prototxt', '.pbtxt',
    '.solver', '.trainval', '.test',
})

# Known binary file extensions that should NOT be parsed as text
_KNOWN_BINARY_EXTS = frozenset({
    '.pt', '.pth', '.pkl', '.joblib',  # PyTorch / pickle
    '.onnx',                           # ONNX model
    '.h5', '.hdf5', '.hdf',           # HDF5
    '.pb', '.pbtxt',                   # TensorFlow (pbtxt is text but handled above)
    '.meta', '.index', '.data-00000-of-00001',  # TF checkpoint
    '.npy', '.npz',                     # NumPy
    '.bin', '.dat', '.raw',             # Binary data
    '.weights',                         # Darknet (binary)
    '.caffemodel',                      # Caffe model
    '.zip', '.gz', '.bz2', '.xz',       # Archives
    '.tar', '.7z', '.rar',
    '.so', '.dll', '.dylib',            # Libraries
    '.exe', '.msi', '.dmg',            # Executables
    '.o', '.obj', '.a', '.lib',        # Object files
    '.pyc', '.pyo', '.class',           # Compiled
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',  # Images
    '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac',   # Media
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
    
    # Extension-based fallback: try to parse as text for known code/text extensions
    # This handles .cs, .swift, .kt, and other code files where magic might
    # return unexpected MIME types (e.g., application/octet-stream)
    if _should_try_text_fallback(filepath):
        logger.debug("Trying text fallback for %s (mime=%s, ext=%s)", filepath, mime, ext)
        try:
            result = parse_text(filepath, mime)
            if result and result.get("text", "").strip():
                return result
        except Exception as e:
            logger.debug("Text fallback failed for %s: %s", filepath, e)
    
    return None