"""
DocPortal — HTML Templates
Loads and renders HTML templates from the templates/ directory.
All templates support bilingual UI (Chinese + English).
"""

import os
from html import escape

_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

# Cache loaded templates
_TEMPLATE_CACHE: dict[str, str] = {}

def _load_template(name: str) -> str:
    """Load a template file from the templates directory (cached)."""
    if name not in _TEMPLATE_CACHE:
        path = os.path.join(_TEMPLATES_DIR, name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Template not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            _TEMPLATE_CACHE[name] = f.read()
    return _TEMPLATE_CACHE[name]


def _t(text_zh: str, text_en: str) -> str:
    """
    Create bilingual text span. Both languages are displayed inline:
    中文 / English
    """
    return f'<span class="lang-zh">{escape(text_zh)}</span> <span class="lang-en">/ {escape(text_en)}</span>'


def _meta_label(icon: str, text_zh: str, text_en: str, value: str) -> str:
    """Create a metadata label with icon, bilingual name, and value."""
    return f'<span>{icon} {_t(text_zh, text_en)}：{escape(value)}</span>'


def wrap_doc_html(
    title: str,
    text: str,
    folder_name: str,
    char_count: int,
    file_size_hr: str,
    index_link: str = "index.html",
    mtime: str = "",
    ctime: str = "",
    prev_page: str = None,
    next_page: str = None,
    page_info: str = None,
) -> str:
    """
    Wrap document content as an independent HTML page with bilingual UI.
    """
    escaped_title = escape(title)
    escaped_text = escape(text)
    escaped_folder = escape(folder_name)

    title_parts = title.replace('\\', '/').split('/')
    breadcrumb_name = title_parts[-1] if title_parts else title

    # Metadata timestamps
    meta_lines = ""
    if mtime:
        meta_lines += _meta_label("🕐", "修改时间", "Modified", mtime)
    if ctime:
        meta_lines += _meta_label("📅", "创建时间", "Created", ctime)

    # Pagination navigation
    pagination_html = ""
    if prev_page or next_page or page_info:
        nav_links = []
        if prev_page:
            nav_links.append(
                f'<a href="{escape(prev_page)}" class="page-nav prev">'
                f'<span class="lang-zh">⬅ 上一页</span><span class="lang-en">⬅ Prev</span>'
                f'</a>'
            )
        if page_info:
            nav_links.append(f'<span class="page-info">{escape(page_info)}</span>')
        if next_page:
            nav_links.append(
                f'<a href="{escape(next_page)}" class="page-nav next">'
                f'<span class="lang-zh">下一页 ➡</span><span class="lang-en">Next ➡</span>'
                f'</a>'
            )
        pagination_html = f"""
<div class="pagination">
  {' '.join(nav_links)}
</div>"""

    # Load template and apply variables
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
    title: str,
    folder_name: str,
    file_size_hr: str,
    filepath: str,
    index_link: str = "../index.html",
    mtime: str = "",
    ctime: str = "",
) -> str:
    """Placeholder page for unsupported file types — bilingual."""
    escaped_title = escape(title)
    escaped_folder = escape(folder_name)
    escaped_filepath = escape(filepath)

    title_parts = title.replace('\\', '/').split('/')
    breadcrumb_name = title_parts[-1] if title_parts else title

    meta_lines = ""
    if mtime:
        meta_lines += f'<span>🕐 <span class="lang-zh">修改时间</span><span class="lang-en">Modified</span>：{escape(mtime)}</span>'
    if ctime:
        meta_lines += f'<span>📅 <span class="lang-zh">创建时间</span><span class="lang-en">Created</span>：{escape(ctime)}</span>'

    # Load template
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
    docs_meta: list,
    folder_name: str,
    folder_path: str,
    total_chars: int,
    generated_at: str,
) -> str:
    """
    Generate the knowledge portal index page (index.html) — bilingual UI.
    """
    escaped_folder = escape(folder_name)
    escaped_path = escape(folder_path)

    # Build document cards HTML
    cards_html = ""
    for i, doc in enumerate(docs_meta):
        title = escape(doc["title"])
        file_path = doc.get("file")
        file_link = escape(file_path) if file_path else ""
        preview = escape(doc["preview"][:200])
        size_hr = escape(doc.get("size_hr", ""))
        char_count = doc["size"]

        # Tags
        tags_html = ""
        for tag in doc.get("tags", []):
            safe_tag = escape(tag)
            tags_html += f'<span class="tag" data-tag="{safe_tag}">{safe_tag}</span>'

        is_skipped = doc.get("skipped", False)

        if file_link and not is_skipped:
            title_html = f'<a class="card-title" href="{file_link}" target="_blank">{title}</a>'
        elif file_link and is_skipped:
            title_html = f'<a class="card-title skipped" href="{file_link}" target="_blank">{title}</a>'
        else:
            title_html = f'<span class="card-title" style="color:#999;cursor:default;">{title}</span>'

        card_class = "doc-card"
        icon = "📄"
        if is_skipped:
            card_class += " skipped-card"
            icon = "⏭️"

        cards_html += f"""
  <div class="{card_class}" data-index="{i}" data-search="{title.lower()}">
    <div class="card-header">
      <span class="card-icon">{icon}</span>
      {title_html}
    </div>
    <div class="card-meta">
      <span>📏 {size_hr}</span>
      <span>{'⏭️ ' + escape('已跳过 / Skipped') if is_skipped else f'📝 {char_count:,} ' + escape('字符 / chars')}</span>
    </div>
    <div class="card-preview">{preview}</div>
    <div class="card-tags">{tags_html}</div>
  </div>"""

    # Auto-extract keywords from all docs for keyword cloud
    all_tags_set = set()
    for doc in docs_meta:
        for tag in doc.get("tags", []):
            if tag != "已跳过":
                all_tags_set.add(tag)
    all_tags = sorted(all_tags_set)[:40]

    tags_cloud_html = ""
    for tag in all_tags:
        safe_tag = escape(tag)
        tags_cloud_html += f'<span class="cloud-tag" data-tag="{safe_tag}">{safe_tag}</span> '

    doc_count = len(docs_meta)
    total_size_hr = _format_total_size(docs_meta)

    # Load template
    template = _load_template("index_page.html")
    result = template.replace("$escaped_folder", escaped_folder)
    result = result.replace("$escaped_subtitle", escape("知识门户 / Knowledge Portal"))
    result = result.replace("$escaped_path", escaped_path)
    result = result.replace("$doc_count", str(doc_count))
    result = result.replace("$total_chars", f"{total_chars:,}")
    result = result.replace("$total_size_hr", total_size_hr)
    result = result.replace("$generated_at_escaped", escape(generated_at))
    result = result.replace("$search_placeholder", escape("搜索文档名称或内容... / Search docs by name or content..."))
    result = result.replace("$tags_cloud_html", tags_cloud_html)
    result = result.replace("$cards_html", cards_html)
    result = result.replace("$footer_text", escape("共 / Total"))
    result = result.replace("$footer_units", escape("个文档 / docs"))
    result = result.replace("$footer_chars_unit", escape("字符 / chars"))
    return result


def _format_total_size(docs_meta: list) -> str:
    """Format total size as human-readable string."""
    total = sum(d.get("size", 0) for d in docs_meta)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if total < 1024:
            return f"{total:.1f} {unit}"
        total /= 1024
    return f"{total:.1f} TB"
