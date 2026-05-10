import logging

logger = logging.getLogger(__name__)

# Try to use chardet for more accurate encoding detection
try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False


def _detect_encoding(filepath: str) -> str:
    """
    Detect file encoding. Uses chardet if available, otherwise falls back
    to trying common encodings in order.
    
    Returns the detected encoding name, or None if detection fails.
    """
    if HAS_CHARDET:
        try:
            # Read a sample of the file for detection
            with open(filepath, "rb") as f:
                raw_data = f.read(65536)  # Read first 64KB
            result = chardet.detect(raw_data)
            detected = result.get("encoding")
            confidence = result.get("confidence", 0)
            if detected and confidence > 0.5:
                logger.debug("chardet detected encoding: %s (confidence: %.2f)", detected, confidence)
                return detected
            logger.debug("chardet low confidence (%.2f) for %s, falling back", confidence, detected)
        except Exception as e:
            logger.debug("chardet detection failed: %s", e)
    
    # Fallback: try common encodings in order
    return None


def _try_encodings(filepath: str, encodings: list) -> str:
    """
    Try reading file with given encodings in order.
    Returns the text content if successful, raises exception if all fail.
    """
    last_error = None
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                text = f.read()
            logger.debug("Successfully decoded %s with encoding %s", filepath, enc)
            return text
        except UnicodeDecodeError as e:
            last_error = e
            continue
        except Exception as e:
            last_error = e
            continue
    raise last_error or UnicodeDecodeError("All encodings failed")


def parse_text(filepath, mime=None):
    # Step 1: Try chardet-based detection if available
    if HAS_CHARDET:
        detected_enc = _detect_encoding(filepath)
        if detected_enc:
            try:
                with open(filepath, "r", encoding=detected_enc) as f:
                    text = f.read()
                return {
                    "extract_type": "text",
                    "text": text,
                    "metadata": {"mime": mime or "text/plain", "encoding": detected_enc},
                }
            except (UnicodeDecodeError, Exception) as e:
                logger.debug("chardet encoding %s failed: %s, trying fallbacks", detected_enc, e)
    
    # Step 2: Try common encodings in order (UTF-8 → GBK → Latin-1)
    common_encodings = ["utf-8", "gbk", "latin-1"]
    try:
        text = _try_encodings(filepath, common_encodings)
        return {
            "extract_type": "text",
            "text": text,
            "metadata": {"mime": mime or "text/plain"},
        }
    except Exception:
        pass
    
    # Step 3: All encodings failed — fallback with error replacement
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        logger.warning("Fallback reading %s with utf-8 replace mode", filepath)
        return {
            "extract_type": "text",
            "text": text,
            "metadata": {"mime": mime or "text/plain"},
        }
    except Exception as e:
        logger.exception("Failed to parse text file %s: %s", filepath, e)
        return None
