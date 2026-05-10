import os
import logging
from binascii import hexlify

logger = logging.getLogger(__name__)


def parse_binary(filepath, config):
    try:
        max_bytes = config.get("binary", {}).get("hex_preview_bytes", 8192)
        with open(filepath, "rb") as f:
            data = f.read(max_bytes)
        hex_preview = hexlify(data).decode("ascii")
        # Extract printable ASCII segments
        ascii_segments = []
        current = []
        for byte in data:
            if 32 <= byte < 127:
                current.append(chr(byte))
            else:
                if len(current) >= 4:  # minimum segment length
                    ascii_segments.append("".join(current))
                current = []
        if current and len(current) >= 4:
            ascii_segments.append("".join(current))
        text = "\n".join(ascii_segments) if ascii_segments else ""
        return {
            "extract_type": "binary",
            "text": text,
            "hex_preview": hex_preview,
            "metadata": {
                "mime": "application/octet-stream",
                "size": os.path.getsize(filepath),
                "hex_preview_length": len(hex_preview),
            },
        }
    except Exception as e:
        logger.exception("Failed to parse binary file %s: %s", filepath, e)
        return None
