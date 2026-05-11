"""
FolderKnowledgeSiteGeneratorForAI — HTML Templates
Loads and renders HTML templates from the templates/ directory.
Generates single-page knowledge portal with collapsible file contents.
"""

import os
import json
import re
from html import escape
from typing import Optional

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
        '.pdf': 'PDF', '.docx': 'DOCX', '.doc': 'DOC',
        '.txt': 'TXT', '.md': 'Markdown',
        '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
        '.html': 'HTML', '.css': 'CSS', '.json': 'JSON',
        '.xml': 'XML', '.yaml': 'YAML', '.yml': 'YAML',
        '.csv': 'CSV', '.xlsx': 'Excel', '.xls': 'Excel',
        '.pptx': 'PowerPoint', '.ppt': 'PowerPoint',
        '.rtf': 'RTF', '.log': 'Log',
        '.cfg': 'Config', '.ini': 'Config', '.conf': 'Config',
        '.sh': 'Shell Script', '.bat': 'Batch', '.ps1': 'PowerShell',
        '.sql': 'SQL', '.rb': 'Ruby', '.java': 'Java',
        '.cpp': 'C++', '.c': 'C', '.h': 'C Header',
        '.go': 'Go', '.rs': 'Rust', '.php': 'PHP',
        '.swift': 'Swift', '.kt': 'Kotlin', '.scala': 'Scala',
        '.r': 'R', '.lua': 'Lua',
        '.toml': 'TOML', '.lock': 'Lock File',
    }
    return type_map.get(ext, ext.upper().lstrip('.').replace('.', '') if ext else 'Unknown')


def build_file_content_blocks(docs_texts: list) -> str:
    """
    Build HTML <details> blocks for all file contents.
    
    Args:
        docs_texts: list of dicts with keys:
            - title: display title / relative path
            - text: full file text content
            - size: char count
            - file_type: file type string
    
    Returns:
        HTML string with collapsible <details> blocks
    """
    parts = []
    for i, doc in enumerate(docs_texts):
        title = doc.get("title", f"file_{i}")
        text = doc.get("text", "")
        size = doc.get("size", 0)
        file_type = doc.get("file_type", _get_file_type(title))
        
        escaped_title = escape(title)
        escaped_text = escape(text)
        size_str = f"{size:,}" if size else "0"
        
        # Sanitize for data-filename attribute (strip HTML for DOM matching)
        safe_filename = escape(title.replace('\\', '/'))
        
        block = (
            f'<details class="file-content" data-filename="{safe_filename}">\n'
            f'  <summary>\n'
            f'    📄 {escaped_title}\n'
            f'    <span class="file-summary-info">{file_type} — {size_str} chars</span>\n'
            f'  </summary>\n'
            f'  <div class="file-content-body">\n'
            f'    <pre><code>{escaped_text}</code></pre>\n'
            f'  </div>\n'
            f'  <div class="file-actions">\n'
            f'    <button onclick="this.closest(\'details\').open = false">📁 Collapse</button>\n'
            f'  </div>\n'
            f'</details>'
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

    # Build document cards (only for supported/parsed docs)
    cards_html = ""
    for i, doc in enumerate(docs_meta):
        title = escape(doc["title"])
        file_path = doc.get("file")
        file_link = escape(file_path) if file_path else ""
        preview = escape(doc["preview"][:200])
        size_hr = escape(doc.get("size_hr", ""))
        char_count = doc["size"]

        tags_html = ""
        for tag in doc.get("tags", []):
            safe_tag = escape(tag)
            tags_html += f'<span class="tag">{safe_tag}</span>'

        is_skipped = doc.get("skipped", False)

        if file_link and not is_skipped:
            title_html = f'<a class="card-title" onclick="jumpToFile(\'{escape(doc.get("title",""))}\')">{title}</a>'
        else:
            title_html = f'<span class="card-title" style="color:#999;">{title}</span>'

        card_class = "doc-card"
        icon = "📄"
        if is_skipped:
            card_class += " skipped-card"
            icon = "⏭️"

        meta_size = f'<span>📏 {size_hr}</span>'
        meta_chars = f'<span>{icon} Skipped</span>' if is_skipped else f'<span>📝 {char_count:,} chars</span>'

        # --- Enriched data-* attributes ---
        doc_tags = doc.get("tags", [])
        kw_attr = escape(", ".join(doc_tags)) if doc_tags else ""
        file_type_val = _get_file_type(doc.get("title", ""))
        mtime_val = escape(doc.get("mtime", ""))
        data_attrs = (
            f'data-index="{i}" '
            f'data-search="{title.lower()}" '
            f'data-file-type="{escape(file_type_val)}" '
            f'data-chars="{char_count}" '
            f'data-keywords="{kw_attr}" '
            f'data-mtime="{mtime_val}"'
        )

        cards_html += f"""
  <div class="{card_class}" {data_attrs}>
    <div class="card-header">
      <span class="card-icon">{icon}</span>
      {title_html}
    </div>
    <div class="card-meta">
      {meta_size}
      {meta_chars}
    </div>
    <div class="card-preview">{preview}</div>
    <div class="card-tags">{tags_html}</div>
  </div>"""

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
    result = result.replace("$cards_html", cards_html)
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