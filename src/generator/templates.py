"""
FolderKnowledgeSiteGeneratorForAI — HTML Templates
Loads and renders HTML templates from the templates/ directory.
Generates single-page knowledge portal with collapsible file contents.
"""

import os
import string
import base64
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


# Import shared type mappings from constants module
try:
    from src.constants import FILE_TYPE_MAP, FILE_TYPE_ICONS
except ImportError:
    # Fallback mappings if constants module unavailable
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


def _get_file_type(filename: str) -> str:
    """Determine file type from extension using shared constants."""
    ext = os.path.splitext(filename)[1].lower()
    return FILE_TYPE_MAP.get(ext, ext.upper().lstrip('.').replace('.', '') if ext else 'Unknown')


def _get_file_type_icon(file_type: str) -> str:
    """Return an emoji icon for the given file type using shared constants."""
    return FILE_TYPE_ICONS.get(file_type, '📄')


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
        # Base64 encode the filename to avoid CSS selector escaping issues
        # with special characters like &, ", ', etc.
        safe_filename_b64 = base64.b64encode(title.replace('\\', '/').encode('utf-8')).decode('ascii')
        
        # Build pre-computed search index (lowercase title + tags for fast JS filtering)
        search_index = (title.lower() + ' ' + ' '.join(t.lower() for t in tags)).strip()
        safe_search_index = escape(search_index)
        
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
            f'<div class="doc-block" data-filename-b64="{safe_filename_b64}" data-index="{safe_search_index}">\n'
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


def build_ai_raw_text_block(
    docs_texts: list,
    folder_name: str,
    total_chars: int,
    generated_at: str,
) -> str:
    """
    Build a hidden AI-readable plain-text block containing all file contents.
    
    This produces a pure-text representation of all files, separated by
    ASCII dividers, wrapped in a <pre> tag. It is placed in the HTML with
    'position: absolute; left: -9999px' so that:
      - Human users never see it
      - Screen readers skip it (via aria-hidden="true")
      - AI text extractors (Edge Copilot, ChatGPT, etc.) can read the full
        content because they check 'display' property, not visual position
    
    Args:
        docs_texts: list of dicts with keys:
            - title: display title / relative path
            - text: full file text content
            - size: char count
            - size_hr: human-readable size (optional)
        folder_name: Source folder name
        total_chars: Total character count across all files
        generated_at: Timestamp string
    
    Returns:
        HTML string: a <pre> block containing all file texts in plain text
        format, already HTML-escaped and ready for template insertion.
    """
    lines = []
    
    # ── Header / metadata block ──
    lines.append("=" * 80)
    lines.append("  KNOWLEDGE PORTAL — AI-READABLE TEXT EXTRACT")
    lines.append("=" * 80)
    lines.append(f"  Source folder : {folder_name}")
    lines.append(f"  Total files   : {len(docs_texts)}")
    lines.append(f"  Total chars   : {total_chars:,}")
    lines.append(f"  Generated at  : {generated_at}")
    lines.append("=" * 80)
    lines.append("")
    
    # ── Each file ──
    for i, doc in enumerate(docs_texts):
        title = doc.get("title", f"file_{i}")
        text = doc.get("text", "")
        size = doc.get("size", 0)
        size_hr = doc.get("size_hr", "")
        
        # File header separator
        lines.append("-" * 80)
        lines.append(f"  FILE: {title}")
        lines.append(f"  Size: {size_hr}  |  {size:,} characters")
        lines.append("-" * 80)
        lines.append("")
        
        # The actual file content — keep as-is (will be HTML-escaped once as a whole)
        lines.append(text)
        
        # Trailing newline before next file
        lines.append("")
    
    # Footer
    lines.append("=" * 80)
    lines.append("  END OF AI-READABLE TEXT EXTRACT")
    lines.append("=" * 80)
    
    raw_text = "\n".join(lines)
    
    # HTML-escape the entire block and wrap in <pre> tags for formatting preservation
    escaped_raw_text = escape(raw_text)
    
    return f"<pre>{escaped_raw_text}</pre>"


def wrap_index_html(
    docs_meta: list,
    folder_name: str,
    folder_path: str,
    total_chars: int,
    generated_at: str,
    file_tree_html: str = "",
    file_contents_html: str = "",
    language: str = "en",
    ai_raw_text_html: str = "",
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
    tpl = string.Template(template)
    result = tpl.safe_substitute({
        "escaped_folder": escaped_folder,
        "language": language,
        "escaped_subtitle": "Knowledge Portal",
        "escaped_path": escaped_path,
        "doc_count": str(doc_count),
        "skipped_count": str(skipped_count),
        "total_chars": f"{total_chars:,}",
        "total_size_hr": total_size_hr,
        "generated_at_escaped": escape(generated_at),
        "tags_cloud_html": tags_cloud_html,
        "cards_html": "",
        "file_tree_html": file_tree_html,
        "file_contents_html": file_contents_html,
        "ai_raw_text_html": ai_raw_text_html,
        "meta_description_escaped": escaped_index_meta_desc,
        "meta_keywords_escaped": escaped_index_keywords,
    })
    return result


def _format_total_size(docs_meta: list) -> str:
    total = sum(d.get("size", 0) for d in docs_meta)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if total < 1024:
            return f"{total:.1f} {unit}"
        total /= 1024
    return f"{total:.1f} TB"


def wrap_skipped_html(
    title: str,
    folder_name: str,
    file_size_hr: str = "",
    filepath: str = "",
) -> str:
    """Wrap skipped file page with HTML template.
    
    NOTE: This function is kept as a public API for compatibility, but
    the portal generator no longer generates individual skipped pages.
    Skipped files now appear only in the file tree on the index page.
    
    Args:
        title: File name / title
        folder_name: Parent folder name
        file_size_hr: Human-readable file size (optional)
        filepath: Full file path (optional)
    
    Returns:
        Complete HTML string for a skipped file info page
    """
    template = _load_template("skipped_page.html")
    tpl = string.Template(template)
    result = tpl.safe_substitute({
        "escaped_title": escape(title),
        "escaped_folder": escape(folder_name),
        "file_size_hr": escape(file_size_hr) if file_size_hr else "Unknown",
        "escaped_filepath": escape(filepath) if filepath else "N/A",
        "breadcrumb_name": escape(title),
        "index_link": "index.html",
        "meta_lines": "",
    })
    return result