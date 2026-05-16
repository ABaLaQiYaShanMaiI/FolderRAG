"""
FolderKnowledgeSiteGeneratorForAI — Shared Utility Functions
"""


def human_readable_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format.

    Supports units from B through PB.
    """
    if size_bytes == 0:
        return "0 B"
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    for unit in units:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
