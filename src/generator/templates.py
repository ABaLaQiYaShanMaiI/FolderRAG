"""
FolderKnowledgeSiteGeneratorForAI — HTML Templates
Loads and renders HTML templates from the templates/ directory.
English-only output for clean, compact HTML.
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


def wrap_doc_html(
    title: str, text: str, folder_name: str,
    char_count: int, file_size_hr: str,
    index_link: str = "index.html",
    mtime: str = "", ctime: str = "",
    prev_page: str = None, next_page: str = None,
    page_info: str = None,
) -> str:
    escaped_title = escape(title)
    escaped_text = escape(text)
    escaped_folder = escape(folder_name)
    title_parts = title.replace('\\', '/').split('/')
    breadcrumb_name = title_parts[-1] if title_parts else title

    meta_lines = ""
    if mtime:
        meta_lines += f'<span>Modified: {escape(mtime)}</span>'
    if ctime:
        meta_lines += f'<span>Created: {escape(ctime)}</span>'

    pagination_html = ""
    if prev_page or next_page or page_info:
        nav_links = []
        if prev_page:
            nav_links.append(f'<a href="{escape(prev_page)}" class="page-nav prev">&#x2B05; Prev</a>')
        if page_info:
            nav_links.append(f'<span class="page-info">{escape(page_info)}</span>')
        if next_page:
            nav_links.append(f'<a href="{escape(next_page)}" class="page-nav next">Next &#x27A1;</a>')
        pagination_html = f'<div class="pagination">{" ".join(nav_links)}</div>'

    template = _load_template("doc_page.html")
    result = template.replace("$escaped_title", escaped_title)
    result = result.replace("$escaped_folder", escaped_folder)
    result = result.replace("$breadcrumb_name", escape(breadcrumb_name))
    result = result.replace("$index_link", escape(index_link))
    result = result.replace("$pagination_html", pagination_html)
    result = result.replace("$pagination_html_bottom", pagination_html)
    result = result.replace("$file_size_hr", escape(file_size_hr))
    result = result.replace("$char_count", f"{char_count:,}")
    result = result.replace("$char_count_raw", str(char_count))
    result = result.replace("$escaped_text", escaped_text)
    result = result.replace("$meta_lines", meta_lines)
    return result


def wrap_skipped_html(
    title: str, folder_name: str, file_size_hr: str,
    filepath: str, index_link: str = "../index.html",
    mtime: str = "", ctime: str = "",
) -> str:
    """
    Wrap skipped/unsupported file info into an HTML page template.

    Note: This function is retained as a public API for potential external use;
    the current portal generator does not generate skipped file pages, it only
    shows skipped files in the file tree on the index page.
    """
    escaped_title = escape(title)
    escaped_folder = escape(folder_name)
    escaped_filepath = escape(filepath)
    title_parts = title.replace('\\', '/').split('/')
    breadcrumb_name = title_parts[-1] if title_parts else title

    meta_lines = ""
    if mtime:
        meta_lines += f'<span>Modified: {escape(mtime)}</span>'
    if ctime:
        meta_lines += f'<span>Created: {escape(ctime)}</span>'

    template = _load_template("skipped_page.html")
    result = template.replace("$escaped_title", escaped_title)
    result = result.replace("$escaped_folder", escaped_folder)
    result = result.replace("$breadcrumb_name", escape(breadcrumb_name))
    result = result.replace("$index_link", escape(index_link))
    result = result.replace("$meta_lines", meta_lines)
    result = result.replace("$file_size_hr", escape(file_size_hr))
    result = result.replace("$escaped_filepath", escaped_filepath)
    return result


def wrap_index_html(
    docs_meta: list, folder_name: str, folder_path: str,
    total_chars: int, generated_at: str, file_tree_html: str = "",
    language: str = "en",
) -> str:
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
            title_html = f'<a class="card-title" href="{file_link}" target="_blank">{title}</a>'
        else:
            title_html = f'<span class="card-title" style="color:#999;">{title}</span>'

        card_class = "doc-card"
        icon = "📄"
        if is_skipped:
            card_class += " skipped-card"
            icon = "⏭️"

        meta_size = f'<span>📏 {size_hr}</span>'
        meta_chars = f'<span>{icon} Skipped</span>' if is_skipped else f'<span>📝 {char_count:,} chars</span>'

        cards_html += f"""
  <div class="{card_class}" data-index="{i}" data-search="{title.lower()}">
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
    return result


def _format_total_size(docs_meta: list) -> str:
    total = sum(d.get("size", 0) for d in docs_meta)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if total < 1024:
            return f"{total:.1f} {unit}"
        total /= 1024
    return f"{total:.1f} TB"