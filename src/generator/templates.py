"""
FolderKnowledgeSiteGeneratorForAI — HTML Templates
Loads and renders HTML templates from the templates/ directory.
English-only output for clean, compact HTML.
"""

import os
import json
import re
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
        '.pdf': 'PDF',
        '.docx': 'DOCX',
        '.doc': 'DOC',
        '.txt': 'TXT',
        '.md': 'Markdown',
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.html': 'HTML',
        '.css': 'CSS',
        '.json': 'JSON',
        '.xml': 'XML',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.csv': 'CSV',
        '.xlsx': 'Excel',
        '.xls': 'Excel',
        '.pptx': 'PowerPoint',
        '.ppt': 'PowerPoint',
        '.rtf': 'RTF',
        '.log': 'Log',
        '.cfg': 'Config',
        '.ini': 'Config',
        '.conf': 'Config',
        '.sh': 'Shell Script',
        '.bat': 'Batch',
        '.ps1': 'PowerShell',
        '.sql': 'SQL',
        '.rb': 'Ruby',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.h': 'C Header',
        '.go': 'Go',
        '.rs': 'Rust',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.r': 'R',
        '.lua': 'Lua',
        '.toml': 'TOML',
        '.lock': 'Lock File',
    }
    return type_map.get(ext, ext.upper().lstrip('.').replace('.', '') if ext else 'Unknown')


def _build_toc_html(text: str) -> str:
    """Generate a Table of Contents from Markdown headings in text."""
    heading_pattern = re.compile(r'^(#{1,4})\s+(.+)$', re.MULTILINE)
    headings = list(heading_pattern.finditer(text))
    if len(headings) < 2:
        return ""

    parts = []
    parts.append('<nav class="toc-container" aria-label="Table of Contents">')
    parts.append('<div class="toc-title">📑 Table of Contents</div>')
    parts.append('<ul class="toc-list">')
    for match in headings:
        level = len(match.group(1))
        title_text = match.group(2).strip()
        anchor_id = re.sub(r'[^\w\u4e00-\u9fff\- ]', '', title_text.lower())
        anchor_id = re.sub(r'\s+', '-', anchor_id)
        cls = {2: 'toc-h2', 3: 'toc-h3', 4: 'toc-h4'}.get(level, 'toc-h2')
        parts.append(f'<li class="{cls}"><a href="#{escape(anchor_id)}">{escape(title_text)}</a></li>')
    parts.append('</ul>')
    parts.append('</nav>')
    return "\n".join(parts)


def _build_related_docs_html(current_title: str, current_keywords: list, all_docs_meta: list, max_items: int = 5) -> str:
    """Find related documents based on keyword overlap (Jaccard similarity)."""
    if not current_keywords or not all_docs_meta:
        return ""

    current_kw_set = set(k.lower() for k in current_keywords)
    if not current_kw_set:
        return ""

    scored = []
    for doc in all_docs_meta:
        if doc.get("skipped") or not doc.get("file"):
            continue
        # Skip self
        doc_title = doc.get("title", "")
        if doc_title == current_title:
            continue
        doc_tags = [t.lower() for t in doc.get("tags", [])]
        if not doc_tags:
            continue
        doc_kw_set = set(doc_tags)
        intersection = len(current_kw_set & doc_kw_set)
        union = len(current_kw_set | doc_kw_set)
        if union == 0:
            continue
        score = intersection / union
        if score > 0:
            scored.append((score, doc))

    scored.sort(key=lambda x: -x[0])
    top = scored[:max_items]

    if not top:
        return ""

    parts = []
    parts.append('<div class="related-docs">')
    parts.append('<div class="related-title">🔗 Related Documents</div>')
    parts.append('<ul class="related-list">')
    for score, doc in top:
        d_title = escape(doc.get("title", ""))
        # Strip "docs/" prefix since doc pages are already inside docs/ directory
        d_file = doc.get("file", "")
        d_link = escape(d_file.replace("docs/", "", 1))
        score_pct = int(score * 100)
        parts.append(f'<li><a href="{d_link}">📄 {d_title}</a> <span class="rel-score">({score_pct}% match)</span></li>')
    parts.append('</ul>')
    parts.append('</div>')
    return "\n".join(parts)


def wrap_doc_html(
    title: str, text: str, folder_name: str,
    char_count: int, file_size_hr: str,
    index_link: str = "index.html",
    mtime: str = "", ctime: str = "",
    prev_page: str = None, next_page: str = None,
    page_info: str = None,
    keywords: list = None,
    rel_path: str = "",
    total_parts: int = 1,
    part_idx: int = 0,
    all_docs_meta: list = None,
) -> str:
    # Inject anchor IDs into headings so TOC links work
    def _inject_heading_anchors(t: str) -> str:
        """Add <a id="..."> before each Markdown heading so TOC links can jump to them."""
        lines = t.split('\n')
        result_lines = []
        for line in lines:
            m = re.match(r'^(#{1,4})\s+(.+)$', line)
            if m:
                title_text = m.group(2).strip()
                anchor_id = re.sub(r'[^\w\u4e00-\u9fff\- ]', '', title_text.lower())
                anchor_id = re.sub(r'\s+', '-', anchor_id)
                result_lines.append(f'<a id="{anchor_id}"></a>{line}')
            else:
                result_lines.append(line)
        return '\n'.join(result_lines)

    text_with_anchors = _inject_heading_anchors(text)
    escaped_title = escape(title)
    escaped_text = escape(text_with_anchors)
    escaped_folder = escape(folder_name)
    title_parts = title.replace('\\', '/').split('/')
    breadcrumb_name = title_parts[-1] if title_parts else title

    # --- Meta description (first 200 chars of text) ---
    text_clean = text.replace('\n', ' ').strip()
    meta_desc = text_clean[:200]
    if len(text_clean) > 200:
        meta_desc += "..."
    escaped_meta_desc = escape(meta_desc)

    # --- Keywords ---
    kw_list = keywords or []
    kw_str = ", ".join(kw_list)
    escaped_kw = escape(kw_str)

    # --- File type ---
    file_type = _get_file_type(title)

    # --- Rel path ---
    escaped_rel_path = escape(rel_path)

    # --- Page info numbers ---
    page_info_num = ""
    total_parts_str = ""
    if total_parts > 1:
        page_info_num = str(part_idx + 1) if part_idx > 0 else "1"
        total_parts_str = str(total_parts)

    # --- Prev/Next links <link> tags ---
    prev_next_links = ""
    if prev_page:
        prev_next_links += f'<link rel="prev" href="{escape(prev_page)}">\n'
    if next_page:
        prev_next_links += f'<link rel="next" href="{escape(next_page)}">\n'

    # --- Canonical URL: point to current page ---
    safe_file = re.sub(r'[<>:"/\\|?*]', '_', title).replace(' ', '_')
    canonical_url = escape(f"{safe_file}.html")

    # --- Base href ---
    base_href = "./"

    # --- Mtime ISO format ---
    mtime_iso = mtime
    mtime_str = mtime
    try:
        from datetime import datetime
        if mtime:
            dt = datetime.strptime(mtime, "%Y-%m-%d %H:%M")
            mtime_iso = dt.strftime("%Y-%m-%dT%H:%M:%S")
    except (ValueError, Exception):
        pass

    # --- JSON-LD Article ---
    json_ld_obj = {
        "@context": "https://schema.org",
        "@type": "Article",
        "name": title,
        "description": meta_desc[:200],
        "keywords": kw_str if kw_str else None,
        "dateModified": mtime_iso,
        "isPartOf": {
            "@type": "Collection",
            "name": folder_name
        }
    }
    # Remove None values
    json_ld_obj = {k: v for k, v in json_ld_obj.items() if v is not None}
    json_ld_html = f'<script type="application/ld+json">\n{json.dumps(json_ld_obj, ensure_ascii=False, indent=2)}\n</script>'

    # --- BreadcrumbList JSON-LD ---
    breadcrumb_items = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": index_link}
    ]
    if folder_name:
        breadcrumb_items.append({"@type": "ListItem", "position": 2, "name": folder_name, "item": index_link})
    breadcrumb_items.append({"@type": "ListItem", "position": 3, "name": breadcrumb_name})
    breadcrumb_json_ld = f'''<script type="application/ld+json">
{json.dumps({
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": breadcrumb_items
}, ensure_ascii=False, indent=2)}
</script>'''

    # --- Open Graph meta tags ---
    og_meta_tags = ""
    og_meta_tags += f'<meta property="og:title" content="{escape(title)}">\n'
    og_meta_tags += f'<meta property="og:description" content="{escaped_meta_desc}">\n'
    og_meta_tags += '<meta property="og:type" content="article">\n'
    og_meta_tags += f'<meta property="og:url" content="{canonical_url}">\n'
    og_meta_tags += f'<meta property="og:site_name" content="{escape(folder_name)} Knowledge Portal">\n'

    # --- Twitter Card meta tags ---
    twitter_meta_tags = ""
    twitter_meta_tags += '<meta name="twitter:card" content="summary">\n'
    twitter_meta_tags += f'<meta name="twitter:title" content="{escape(title)}">\n'
    twitter_meta_tags += f'<meta name="twitter:description" content="{escaped_meta_desc}">\n'

    # --- Summary (first 300 chars) ---
    summary_300 = text_clean[:300]
    if len(text_clean) > 300:
        summary_300 += "..."
    escaped_summary_300 = escape(summary_300)

    # --- Doc summary section ---
    doc_summary_parts = ['<div class="doc-summary" role="doc-summary" aria-label="Document Summary">']
    doc_summary_parts.append('<div class="sum-title">📋 Document Summary</div>')
    doc_summary_parts.append(f'<div class="sum-row"><span class="sum-label">Path:</span><span>{escaped_rel_path}</span></div>')
    doc_summary_parts.append(f'<div class="sum-row"><span class="sum-label">Type:</span><span>{escape(file_type)}</span></div>')
    if mtime:
        doc_summary_parts.append(f'<div class="sum-row"><span class="sum-label">Modified:</span><span>{escape(mtime)}</span></div>')
    doc_summary_parts.append(f'<div class="sum-row"><span class="sum-label">Chars:</span><span>{char_count:,}</span></div>')
    if total_parts > 1:
        doc_summary_parts.append(f'<div class="sum-row"><span class="sum-label">Page:</span><span>{page_info_num} of {total_parts_str}</span></div>')
    if kw_list:
        tags_html = "".join(f'<span class="sum-tag">{escape(k)}</span>' for k in kw_list[:10])
        doc_summary_parts.append(f'<div class="sum-row"><span class="sum-label">Keywords:</span><span class="sum-keywords">{tags_html}</span></div>')
    doc_summary_parts.append(f'<div class="sum-text">{escaped_summary_300}</div>')
    doc_summary_parts.append('</div>')
    doc_summary_html = "\n".join(doc_summary_parts)

    # --- Table of Contents (anchors injected in text above) ---
    toc_html = _build_toc_html(text)

    # --- Related documents ---
    related_docs_html = _build_related_docs_html(title, kw_list, all_docs_meta or [])

    # --- Reading progress bar ---
    progress_bar_html = ""
    if total_parts > 1:
        progress_pct = int((part_idx + 1) / total_parts * 100)
        progress_bar_html = (
            f'<div class="progress-bar-container" role="progressbar" '
            f'aria-valuenow="{progress_pct}" aria-valuemin="0" aria-valuemax="100" '
            f'aria-label="Reading progress">\n'
            f'  <div class="progress-bar-fill" style="width: {progress_pct}%;"></div>\n'
            f'</div>\n'
            f'<div style="text-align:center;font-size:0.8em;color:#888;margin-bottom:12px;">'
            f'📖 Page {page_info_num} of {total_parts_str} ({progress_pct}% complete)</div>'
        )

    # --- Page info for copilot-hint ---
    if page_info and total_parts > 1:
        page_info_full = f"Page {page_info_num} of {total_parts_str} ({page_info})"
    elif page_info:
        page_info_full = page_info
    elif total_parts > 1:
        page_info_full = f"Page {page_info_num} of {total_parts_str}"
    else:
        page_info_full = "Single page (no pagination)"
    escaped_page_info = escape(page_info_full)

    # --- Meta lines (existing) ---
    meta_lines = ""
    if mtime:
        meta_lines += f'<span>Modified: {escape(mtime)}</span>'
    if ctime:
        meta_lines += f'<span>Created: {escape(ctime)}</span>'

    # --- Pagination HTML (existing, with aria-label) ---
    pagination_html = ""
    if prev_page or next_page or page_info:
        nav_links = []
        if prev_page:
            nav_links.append(f'<a href="{escape(prev_page)}" class="page-nav prev" aria-label="Previous page">&#x2B05; Prev</a>')
        if page_info:
            nav_links.append(f'<span class="page-info">{escape(page_info)}</span>')
        if next_page:
            nav_links.append(f'<a href="{escape(next_page)}" class="page-nav next" aria-label="Next page">Next &#x27A1;</a>')
        pagination_html = f'<nav aria-label="Pagination">{" ".join(nav_links)}</nav>'

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
    # New template variables
    result = result.replace("$meta_description", escaped_meta_desc)
    result = result.replace("$meta_keywords", escaped_kw)
    result = result.replace("$rel_path", escaped_rel_path)
    result = result.replace("$page_info_num", escape(page_info_num))
    result = result.replace("$total_parts_str", escape(total_parts_str))
    result = result.replace("$json_ld_html", json_ld_html)
    result = result.replace("$breadcrumb_json_ld", breadcrumb_json_ld)
    result = result.replace("$prev_next_links", prev_next_links)
    result = result.replace("$doc_summary_html", doc_summary_html)
    result = result.replace("$file_type", escape(file_type))
    result = result.replace("$mtime_str", escape(mtime_str))
    result = result.replace("$mtime_iso", escape(mtime_iso))
    result = result.replace("$page_info_full", escaped_page_info)
    result = result.replace("$summary_300_escaped", escaped_summary_300)
    result = result.replace("$og_meta_tags", og_meta_tags)
    result = result.replace("$twitter_meta_tags", twitter_meta_tags)
    result = result.replace("$base_href", base_href)
    result = result.replace("$canonical_url", canonical_url)
    result = result.replace("$progress_bar_html", progress_bar_html)
    result = result.replace("$toc_html", toc_html)
    result = result.replace("$related_docs_html", related_docs_html)
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
    sitemap_xml_url: str = "",
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

    # --- Build sitemap (plain HTML nav, no JS) ---
    sitemap_html = ""
    if doc_count > 0:
        sitemap_lines = []
        sitemap_lines.append('<nav id="sitemap" aria-label="Document Sitemap">')
        sitemap_lines.append(f'<h2 style="font-size:1em;margin-bottom:8px;color:#666;">📑 Document Index ({doc_count} pages)</h2>')
        sitemap_lines.append('<ul style="list-style:none;padding:0;margin:0;font-size:0.85em;line-height:1.8;">')
        for doc in docs_meta:
            if doc.get("skipped") or not doc.get("file"):
                continue
            d_title = escape(doc["title"])
            d_link = escape(doc["file"])
            d_tags = ", ".join(escape(t) for t in doc.get("tags", [])[:3])
            d_size = doc.get("size", 0)
            sitemap_lines.append(f'<li style="padding:2px 0;"><a href="{d_link}" style="color:#1a73e8;text-decoration:none;">📄 {d_title}</a> <span style="color:#999;">({d_size:,} chars{d_tags and f", {d_tags}" or ""})</span></li>')
        sitemap_lines.append('</ul>')
        sitemap_lines.append('</nav>')
        sitemap_html = "\n".join(sitemap_lines)

    # --- Build AI-friendly meta description for index page ---
    index_meta_desc = f'Knowledge portal for folder "{folder_name}" with {doc_count} documents, {total_chars:,} total characters, generated at {generated_at}'
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
    result = result.replace("$sitemap_html", sitemap_html)
    result = result.replace("$sitemap_xml_url", escape(sitemap_xml_url))
    result = result.replace("$index_meta_description", escaped_index_meta_desc)
    result = result.replace("$index_meta_keywords", escaped_index_keywords)
    return result


def generate_sitemap_xml(docs_meta: list, base_url: str = "") -> str:
    """Generate a standard XML sitemap for all document pages."""
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    # Index page
    lines.append('  <url>')
    lines.append(f'    <loc>{base_url}index.html</loc>')
    lines.append('    <changefreq>weekly</changefreq>')
    lines.append('    <priority>1.0</priority>')
    lines.append('  </url>')
    # Document pages
    for doc in docs_meta:
        if doc.get("skipped") or not doc.get("file"):
            continue
        mtime = doc.get("mtime", "")
        d_link = doc.get("file", "")
        lines.append('  <url>')
        lines.append(f'    <loc>{base_url}{escape(d_link)}</loc>')
        if mtime:
            try:
                from datetime import datetime
                dt = datetime.strptime(mtime, "%Y-%m-%d %H:%M")
                lines.append(f'    <lastmod>{dt.strftime("%Y-%m-%d")}</lastmod>')
            except (ValueError, Exception):
                pass
        lines.append('    <changefreq>monthly</changefreq>')
        lines.append('    <priority>0.8</priority>')
        lines.append('  </url>')
    lines.append('</urlset>')
    return "\n".join(lines)


def generate_robots_txt(sitemap_filename: str = "sitemap.xml") -> str:
    """Generate robots.txt content."""
    return f"""User-agent: *
Allow: /

# Sitemap
Sitemap: {sitemap_filename}
"""


def _format_total_size(docs_meta: list) -> str:
    total = sum(d.get("size", 0) for d in docs_meta)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if total < 1024:
            return f"{total:.1f} {unit}"
        total /= 1024
    return f"{total:.1f} TB"