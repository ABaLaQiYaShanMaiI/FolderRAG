"""
FolderKnowledgeSiteGeneratorForAI — HTML Templates
Loads and renders HTML templates from the templates/ directory.
Generates single-page knowledge portal with collapsible file contents.
"""

import os
from html import escape

_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
_TEMPLATE_CACHE: dict[str, str] = {}


def _load_template(name: str) -> str:
    if name not in _TEMPLATE_CACHE:
        path = os.path.join(_TEMPLATES_DIR, name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Template not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            _TEMPLATE_CACHE[name] = f.read()
    return _TEMPLATE_CACHE[name]


def _get_file_type(filename: str) -> str:
    """Determine file type from extension."""
    ext = os.path.splitext(filename)[1].lower()
    type_map = {
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
        '.bat': 'Batch', '.cmd': 'Batch', '.ps1': 'PowerShell', '.psm1': 'PowerShell Module', '.psd1': 'PowerShell Data',
        '.vbs': 'VBScript',
        # C-family
        '.cs': 'C#', '.fs': 'F#', '.vb': 'VB.NET',
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
        '.test': 'Test Config', '.weights': 'Weights Config',
        # Config
        '.log': 'Log', '.lock': 'Lock File',
        '.markdown': 'Markdown', '.text': 'Text',
    }
    return type_map.get(ext, ext.upper().lstrip('.').replace('.', '') if ext else 'Unknown')


def _get_file_type_icon(file_type: str) -> str:
    """Return an emoji icon for the given file type."""
    icon_map = {
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
        'C++': '⚡', 'C': '⚡', 'C Header': '⚡',
        'C++ Header': '⚡',
        'Go': '🔷', 'Rust': '🦀', 'PHP': '🐘',
        'Swift': '🍎', 'Kotlin': '🅺', 'Kotlin Script': '🅺',
        'Scala': '🔺', 'Groovy': '🔺',
        'Clojure': '🍃', 'ClojureScript': '🍃',
        'Haskell': 'λ', 'Literate Haskell': 'λ',
        'Erlang': '🟠', 'Erlang Header': '🟠',
        'Elixir': '💧', 'Elixir Script': '💧', 'Elm': '🌳',
        'Dart': '🎯', 'Flutter': '🦋',
        'Perl': '🐪', 'Perl Module': '🐪',
        'Tcl': '🔧', 'Lua': '🌙',
        'R': '📊', 'MATLAB': '📐', 'Objective-C++': '🍎',
        'TOML': '⚙️', 'Lock File': '🔒',
        'Caffe Proto': '🧠', 'Protobuf Text': '🧠',
        'Caffe Solver': '🧠', 'Training Config': '🧠',
        'Test Config': '🧠', 'Weights Config': '🧠',
        'Text': '📄',
    }
    return icon_map.get(file_type, '📄')


def build_file_content_blocks(docs_texts: list) -> str:
    """
    Build HTML collapsible file blocks for all file contents.
    
    Each block has:
      - doc-header: icon, filename, size, tags, toggle button
      - doc-content: code preview (hidden by default)
    
    Args:
        docs_texts: list of dicts with keys:
            - title: display title / relative path
            - text: full file text content
            - size: char count
            - file_type: file type string
            - size_hr: human-readable size (optional)
            - tags: list of keyword strings (optional)
    
    Returns:
        HTML string with collapsible file blocks
    """
    parts = []
    for i, doc in enumerate(docs_texts):
        title = doc.get("title", f"file_{i}")
        text = doc.get("text", "")
        size = doc.get("size", 0)
        file_type = doc.get("file_type", _get_file_type(title))
        size_hr = doc.get("size_hr", "")
        tags = doc.get("tags", []) or []
        
        escaped_title = escape(title)
        escaped_text = escape(text)
        size_str = f"{size:,}" if size else "0"
        size_hr_escaped = escape(size_hr)
        safe_filename = escape(title.replace('\\', '/'))
        
        # Build tags string
        tags_html = ""
        for tag in tags[:5]:
            safe_tag = escape(tag)
            tags_html += f'<span class="file-tag">{safe_tag}</span>'
        
        # File type icon
        type_icon = _get_file_type_icon(file_type)
        
        # Build the file block with header + collapsible content
        # Use onclick on the entire header row for easy toggle
        block = (
            f'<div class="doc-block" data-filename="{safe_filename}">\n'
            f'  <div class="doc-header" onclick="toggleDocBlock(this)">\n'
            f'    <span class="file-icon">{type_icon}</span>\n'
            f'    <span class="file-name">{escaped_title}</span>\n'
            f'    <span class="file-size">{size_hr_escaped}</span>\n'
            f'    <span class="file-chars">{size_str} chars</span>\n'
            f'    <span class="file-tags">{tags_html}</span>\n'
            f'    <button class="toggle-btn" onclick="event.stopPropagation();toggleDocBlock(this.closest(\'.doc-block\').querySelector(\'.doc-header\'))">▶</button>\n'
            f'  </div>\n'
            f'  <div class="doc-content" style="display:none;">\n'
            f'    <pre><code>{escaped_text}</code></pre>\n'
            f'  </div>\n'
            f'</div>'
        )
        parts.append(block)
    
    return "\n".join(parts)


def wrap_index_html(
    docs_meta: list,
    folder_name: str,
    folder_path: str,
    total_chars: int,
    generated_at: str,
    file_tree_html: str = "",
    file_contents_html: str = "",
    language: str = "en",
) -> str:
    """Wrap index page with all portal content."""
    escaped_folder = escape(folder_name)
    escaped_path = escape(folder_path)

    # No longer build cards_html — all info is in the file blocks now

    # Keyword cloud from parsed docs only
    all_tags = set()
    for doc in docs_meta:
        for tag in doc.get("tags", []):
            if tag and tag != "Skipped":
                all_tags.add(tag)
    all_tags_sorted = sorted(all_tags)[:40]
    tags_cloud_html = ""
    for tag in all_tags_sorted:
        safe_tag = escape(tag)
        tags_cloud_html += f'<span class="cloud-tag" data-tag="{safe_tag}">{safe_tag}</span> '

    doc_count = sum(1 for d in docs_meta if not d.get("skipped"))
    skipped_count = sum(1 for d in docs_meta if d.get("skipped"))
    total_size_hr = _format_total_size(docs_meta)

    # --- Build AI-friendly meta description for index page ---
    index_meta_desc = (
        f'Knowledge portal for folder "{folder_name}" with {doc_count} documents, '
        f'{total_chars:,} total characters, generated at {generated_at}'
    )
    escaped_index_meta_desc = escape(index_meta_desc)

    # --- Build AI-friendly keywords for index page (top 20 from all docs) ---
    all_index_keywords = set()
    for doc in docs_meta:
        for tag in doc.get("tags", []):
            if tag and tag != "Skipped":
                all_index_keywords.add(tag)
    index_keywords_list = sorted(all_index_keywords)[:20]
    escaped_index_keywords = escape(", ".join(index_keywords_list))

    template = _load_template("index_page.html")
    result = template.replace("$escaped_folder", escaped_folder)
    result = result.replace("$language", language)
    result = result.replace("$escaped_subtitle", "Knowledge Portal")
    result = result.replace("$escaped_path", escaped_path)
    result = result.replace("$doc_count", str(doc_count))
    result = result.replace("$skipped_count", str(skipped_count))
    result = result.replace("$total_chars", f"{total_chars:,}")
    result = result.replace("$total_size_hr", total_size_hr)
    result = result.replace("$generated_at_escaped", escape(generated_at))
    result = result.replace("$tags_cloud_html", tags_cloud_html)
    result = result.replace("$cards_html", "")  # Cards removed, all info in file blocks
    result = result.replace("$file_tree_html", file_tree_html)
    result = result.replace("$file_contents_html", file_contents_html)
    result = result.replace("$index_meta_description", escaped_index_meta_desc)
    result = result.replace("$index_meta_keywords", escaped_index_keywords)

    return result


def _format_total_size(docs_meta: list) -> str:
    total = sum(d.get("size", 0) for d in docs_meta)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if total < 1024:
            return f"{total:.1f} {unit}"
        total /= 1024
    return f"{total:.1f} TB"