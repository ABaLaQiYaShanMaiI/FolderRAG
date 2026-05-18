"""
FolderKnowledgeSiteGeneratorForAI — Shared Constants
"""

# ── Directory filter rules ──
# Directories to always skip during scanning
FILTER_DIRS = frozenset({
    '__pycache__', '.git', '.svn', '.hg', '.idea', '.vscode',
    'node_modules', 'bower_components', '.venv', 'venv', 'env',
    '.tox', '.eggs', 'eggs', 'dist', 'build', '.next', '.nuxt',
    '__MACOSX', '.DS_Store',
})

# File patterns to always skip (applied to rel_path)
FILTER_FILES = frozenset({
    '.DS_Store', 'Thumbs.db', 'desktop.ini',
})

# File extensions to always skip
FILTER_EXTS = frozenset({
    '.exe', '.dll', '.so', '.dylib', '.bin', '.dat',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
    '.mp3', '.wav', '.ogg', '.flac', '.mp4', '.avi', '.mkv',
    '.zip', '.tar', '.gz', '.bz2', '.rar', '.7z',
    '.pyc', '.pyo', '.pyd',
    '.o', '.obj', '.lib', '.a', '.class', '.jar',
    '.ttf', '.otf', '.woff', '.woff2', '.eot',
})


def should_filter_dir(dirname: str) -> bool:
    """Check if a directory should be skipped during scanning."""
    return dirname in FILTER_DIRS or dirname.startswith('.')


def should_filter_file(rel_path: str) -> bool:
    """Check if a file should be skipped during scanning based on path.

    Applies multiple filter rules:
    - Hidden files (dot-prefixed)
    - Matching FILTER_FILES patterns
    - Matching FILTER_EXTS extensions
    - Inside hidden directories
    """
    import os
    basename = os.path.basename(rel_path)
    if basename in FILTER_FILES:
        return True
    if basename.startswith('.'):
        return True
    ext = os.path.splitext(basename)[1].lower()
    if ext in FILTER_EXTS:
        return True
    # Check if any path component is a hidden directory
    parts = rel_path.replace('\\', '/').split('/')
    for part in parts[:-1]:  # Exclude the filename itself
        if part in FILTER_DIRS or part.startswith('.'):
            return True
    return False


# ── Supported text file extensions ──
SUPPORTED_TEXT_EXTS = frozenset({
    # Programming languages
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
    '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.pl',
    '.pm', '.lua', '.r', '.m', '.mm',
    # Web
    '.html', '.htm', '.css', '.scss', '.sass', '.less', '.vue', '.svelte',
    '.xml', '.svg', '.json', '.yaml', '.yml',
    # Config & Scripts
    '.ini', '.cfg', '.conf', '.toml', '.env', '.editorconfig',
    '.gitignore', '.dockerfile',
    '.sh', '.bat', '.ps1', '.bash', '.zsh',
    # Markup & Docs
    '.md', '.mdx', '.rst', '.tex', '.txt', '.log',
    '.csv', '.tsv',
    # Training config
    '.yaml', '.yml',
    # Data
    '.sql', '.sqlite',
})

# 文件大小限制（字节）
DEFAULT_MAX_CHARS = 1_000_000
DEFAULT_MAX_CHARS_PER_FILE = 200_000
# Chunk 大小
DEFAULT_CHUNK_SIZE = 50_000
# 默认最大文件数
DEFAULT_MAX_FILES = 500
# 默认语言
DEFAULT_LANG = "zh"


# ── File type to display name mapping ──
FILE_TYPE_MAP = {
    '.txt': 'TXT', '.md': 'Markdown', '.py': 'Python', '.js': 'JavaScript',
    '.ts': 'TypeScript', '.html': 'HTML', '.css': 'CSS', '.json': 'JSON',
    '.xml': 'XML', '.yaml': 'YAML', '.yml': 'YAML', '.csv': 'CSV',
    '.ini': 'Config', '.cfg': 'Config', '.conf': 'Config',
    '.cs': 'C#', '.java': 'Java', '.cpp': 'C++', '.h': 'C Header',
    '.go': 'Go', '.rs': 'Rust', '.swift': 'Swift', '.kt': 'Kotlin',
    '.rb': 'Ruby', '.php': 'PHP', '.sh': 'Shell Script', '.bat': 'Batch',
    '.ps1': 'PowerShell', '.sql': 'SQL', '.r': 'R',
}

FILE_TYPE_ICONS = {
    'Python': '🐍', 'JavaScript': '🟨', 'TypeScript': '🔵',
    'HTML': '🌐', 'CSS': '🎨', 'Markdown': '📝', 'TXT': '📄',
    'C#': '🔷', 'Java': '☕', 'Go': '🔷', 'Rust': '🦀',
    'Swift': '🍎', 'Kotlin': '🅺',
}