"""
FolderKnowledgeSiteGeneratorForAI — Shared Constants
Single source of truth for file extension sets, filter rules, and type mappings.
"""

import os

# ── File extensions supported for text parsing ──
# Used by gui_scanner.py (fallback when magic unavailable) and dispatcher.py
SUPPORTED_TEXT_EXTS = frozenset({
    '.txt', '.md', '.html', '.htm', '.json', '.xml', '.csv',
    '.yaml', '.yml', '.toml', '.ini', '.log', '.cfg', '.conf',
    '.py', '.pyw', '.js', '.jsx', '.ts', '.tsx', '.css', '.scss', '.less',
    '.sh', '.bash', '.zsh', '.fish', '.bat', '.cmd', '.ps1', '.psm1', '.psd1',
    '.rb', '.java', '.c', '.cpp', '.h', '.hpp', '.cc', '.cxx', '.hh', '.hxx',
    '.rs', '.go', '.php', '.swift', '.kt', '.kts', '.scala',
    '.cs', '.fs', '.vb', '.dart', '.lua', '.r', '.R', '.m', '.mm',
    '.hs', '.erl', '.hrl', '.ex', '.exs', '.elm', '.clj', '.cljs',
    '.sql', '.ddl', '.dml', '.pl', '.pm', '.tcl',
    '.markdown', '.rst', '.text', '.tsv',
    '.pdf', '.docx', '.pptx', '.xlsx',
    # Training / ML text config files
    '.prototxt', '.pbtxt', '.solver', '.trainval', '.test',
    '.cfg',
    # .NET project & solution files (XML/text)
    '.csproj', '.fsproj', '.vbproj',
    '.sln', '.suo', '.user', '.vsconfig',
    '.xaml', '.axaml',
})

# ── Files to exclude from scanning/portal ──
FILTER_EXTS = frozenset({
    '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib',
    '.obj', '.o', '.a', '.lib', '.exe', '.msi',
    '.class', '.jar', '.war',
    '.min.js', '.min.css', '.min.css.map', '.min.js.map',
    '.log', '.lock', '.tmp', '.swp', '.swo', '.bak', '.old',
    '.svg',
    '.DS_Store', '.directory', '.lst',
})

FILTER_DIRS = frozenset({
    '.git', '.svn', '.hg', '__pycache__', '.mypy_cache',
    '.pytest_cache', '.venv', 'venv', 'env', 'node_modules',
    'bower_components', '.idea', '.vscode', '.vs',
    '.sass-cache', '.tox', '.eggs', 'eggs',
    '.ruff_cache', '.mypy_cache',
})

FILTER_FILES = frozenset({
    '.gitignore', '.gitattributes', '.gitmodules',
    '.gitkeep', '.gitlab-ci.yml', '.travis.yml',
    'LICENSE', 'COPYING', 'AUTHORS',
    'thumbs.db', 'desktop.ini',
})

# ── File type → display name mapping ──
FILE_TYPE_MAP = {
    # Office / PDF
    '.pdf': 'PDF', '.docx': 'DOCX', '.doc': 'DOC',
    '.pptx': 'PowerPoint', '.ppt': 'PowerPoint',
    '.xlsx': 'Excel', '.xls': 'Excel',
    '.rtf': 'RTF',
    # Text / Markup
    '.txt': 'TXT', '.md': 'Markdown', '.rst': 'reStructuredText',
    '.html': 'HTML', '.htm': 'HTML', '.xhtml': 'XHTML',
    '.css': 'CSS', '.scss': 'SCSS', '.less': 'Less', '.sass': 'Sass',
    '.json': 'JSON', '.xml': 'XML', '.yaml': 'YAML', '.yml': 'YAML',
    '.toml': 'TOML', '.ini': 'Config', '.cfg': 'Config', '.conf': 'Config',
    '.csv': 'CSV', '.tsv': 'TSV',
    # Scripting / Programming
    '.py': 'Python', '.pyw': 'Python',
    '.js': 'JavaScript', '.jsx': 'JSX',
    '.ts': 'TypeScript', '.tsx': 'TSX',
    '.sh': 'Shell Script', '.bash': 'Bash', '.zsh': 'Zsh', '.fish': 'Fish',
    '.bat': 'Batch', '.cmd': 'Batch', '.ps1': 'PowerShell',
    '.psm1': 'PowerShell Module', '.psd1': 'PowerShell Data',
    '.vbs': 'VBScript',
    # C-family / .NET
    '.cs': 'C#', '.fs': 'F#', '.vb': 'VB.NET',
    '.csproj': 'C# Project', '.fsproj': 'F# Project', '.vbproj': 'VB.NET Project',
    '.sln': 'Solution File', '.suo': 'Solution User Options',
    '.user': 'User Settings', '.vsconfig': 'VS Config',
    '.xaml': 'XAML', '.axaml': 'Avalonia XAML',
    '.cpp': 'C++', '.c': 'C', '.h': 'C Header',
    '.hpp': 'C++ Header', '.cc': 'C++', '.cxx': 'C++', '.hh': 'C++ Header', '.hxx': 'C++ Header',
    # Java & JVM
    '.java': 'Java', '.kt': 'Kotlin', '.kts': 'Kotlin Script',
    '.scala': 'Scala', '.groovy': 'Groovy',
    '.clj': 'Clojure', '.cljs': 'ClojureScript',
    # Functional
    '.hs': 'Haskell', '.lhs': 'Literate Haskell',
    '.erl': 'Erlang', '.hrl': 'Erlang Header',
    '.ex': 'Elixir', '.exs': 'Elixir Script', '.elm': 'Elm',
    # Mobile
    '.swift': 'Swift', '.dart': 'Dart',
    # Web / Server
    '.php': 'PHP', '.phtml': 'PHP',
    '.rb': 'Ruby', '.pl': 'Perl', '.pm': 'Perl Module',
    '.tcl': 'Tcl',
    '.sql': 'SQL', '.ddl': 'SQL DDL', '.dml': 'SQL DML',
    '.lua': 'Lua',
    # Systems
    '.go': 'Go', '.rs': 'Rust',
    '.r': 'R', '.R': 'R', '.m': 'MATLAB', '.mm': 'Objective-C++',
    # Data / ML text config
    '.prototxt': 'Caffe Proto', '.pbtxt': 'Protobuf Text',
    '.solver': 'Caffe Solver', '.trainval': 'Training Config',
    '.test': 'Test Config',
    # Config
    '.log': 'Log', '.lock': 'Lock File',
    '.markdown': 'Markdown', '.text': 'Text',
}

# ── Known binary file extensions that should NOT be parsed as text ──
# Used by dispatcher.py
KNOWN_BINARY_EXTS = frozenset({
    '.pt', '.pth', '.pkl', '.joblib',  # PyTorch / pickle
    '.onnx',                           # ONNX model
    '.h5', '.hdf5', '.hdf',           # HDF5
    '.pb',                             # TensorFlow model (binary)
    '.meta', '.index', '.data-00000-of-00001',  # TF checkpoint
    '.npy', '.npz',                     # NumPy
    '.bin', '.dat', '.raw',             # Binary data
    '.caffemodel',                      # Caffe model (binary)
    '.weights',                         # Darknet / YOLO (binary, not text config)
    '.zip', '.gz', '.bz2', '.xz',       # Archives
    '.tar', '.7z', '.rar',
    '.so', '.dll', '.dylib',            # Libraries
    '.exe', '.msi', '.dmg',            # Executables
    '.o', '.obj', '.a', '.lib',        # Object files
    '.pyc', '.pyo', '.class',           # Compiled
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',  # Images
    '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac',   # Media
})

# ── File type → emoji icon mapping ──
FILE_TYPE_ICONS = {
    'PDF': '📕', 'DOCX': '📘', 'DOC': '📘',
    'TXT': '📄', 'Markdown': '📝', 'reStructuredText': '📝',
    'Python': '🐍', 'JavaScript': '🟨', 'TypeScript': '🔵',
    'JSX': '⚛️', 'TSX': '⚛️',
    'HTML': '🌐', 'XHTML': '🌐', 'CSS': '🎨',
    'SCSS': '🎨', 'Less': '🎨', 'Sass': '🎨',
    'JSON': '📋', 'XML': '📰', 'YAML': '⚙️',
    'CSV': '📊', 'TSV': '📊', 'Excel': '📊',
    'PowerPoint': '📽️',
    'Log': '📃', 'Config': '⚙️',
    'Shell Script': '💻', 'Bash': '💻', 'Zsh': '💻', 'Fish': '💻',
    'Batch': '💻', 'PowerShell': '💻', 'PowerShell Module': '💻',
    'PowerShell Data': '💻', 'VBScript': '💻',
    'SQL': '🗃️', 'SQL DDL': '🗃️', 'SQL DML': '🗃️',
    'Ruby': '💎', 'Java': '☕',
    'C#': '🔷', 'F#': '🔷', 'VB.NET': '🔷',
    'C# Project': '🔷', 'F# Project': '🔷', 'VB.NET Project': '🔷',
    'Solution File': '📋', 'Solution User Options': '⚙️',
    'User Settings': '⚙️', 'VS Config': '⚙️',
    'XAML': '🪟', 'Avalonia XAML': '🪟',
    'C++': '⚡', 'C': '⚡', 'C Header': '⚡',
    'C++ Header': '⚡',
    'Go': '🔷', 'Rust': '🦀', 'PHP': '🐘',
    'Swift': '🍎', 'Kotlin': '🅺', 'Kotlin Script': '🅺',
    'Scala': '🔺', 'Groovy': '🔺',
    'Clojure': '🍃', 'ClojureScript': '🍃',
    'Haskell': 'λ', 'Literate Haskell': 'λ',
    'Erlang': '🟠', 'Erlang Header': '🟠',
    'Elixir': '💧', 'Elixir Script': '💧', 'Elm': '🌳',
    'Dart': '🎯',
    'Perl': '🐪', 'Perl Module': '🐪',
    'Tcl': '🔧', 'Lua': '🌙',
    'R': '📊', 'MATLAB': '📐', 'Objective-C++': '🍎',
    'TOML': '⚙️', 'Lock File': '🔒',
    'Caffe Proto': '🧠', 'Protobuf Text': '🧠',
    'Caffe Solver': '🧠', 'Training Config': '🧠',
    'Test Config': '🧠',
    'Text': '📄',
}