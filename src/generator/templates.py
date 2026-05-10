"""
FolderRAG Portal — HTML Templates
提供所有门户页面的 HTML 模板，包含搜索、文档卡片、页面包装等。
"""

from html import escape


def wrap_doc_html(
    title: str,
    text: str,
    folder_name: str,
    char_count: int,
    file_size_hr: str,
    index_link: str = "index.html",
    mtime: str = "",
    ctime: str = "",
) -> str:
    """
    将单个文档内容包装为独立的 HTML 页面。
    页面控制在 8000 字符以内，确保 Edge Copilot 能完整读取。
    """
    escaped_title = escape(title)
    escaped_text = escape(text)
    escaped_folder = escape(folder_name)

    # Breadcrumb: extract the file name from title
    title_parts = title.replace('\\', '/').split('/')
    breadcrumb_name = title_parts[-1] if title_parts else title

    # Metadata timestamps
    meta_lines = ""
    if mtime:
        meta_lines += f'<span>🕐 修改时间：{escape(mtime)}</span>'
    if ctime:
        meta_lines += f'<span>📅 创建时间：{escape(ctime)}</span>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="copilot-reading-context" content="full">
<meta name="color-scheme" content="light dark">
<title>{escaped_title} — {escaped_folder}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 900px; margin: 0 auto; padding: 24px 20px;
    background: #f8f9fa; color: #333; line-height: 1.7;
  }}
  .breadcrumb {{
    display: flex; align-items: center; gap: 6px;
    font-size: 0.85em; color: #888; margin-bottom: 8px;
    flex-wrap: wrap;
  }}
  .breadcrumb a {{ color: #1a73e8; text-decoration: none; }}
  .breadcrumb a:hover {{ text-decoration: underline; }}
  .breadcrumb .sep {{ color: #ccc; user-select: none; }}

  .nav-bar {{
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 20px; padding-bottom: 12px;
    border-bottom: 1px solid #e0e0e0; flex-wrap: wrap;
  }}
  .nav-bar a {{
    color: #1a73e8; text-decoration: none; font-size: 0.9em;
    padding: 4px 12px; border-radius: 4px; transition: background 0.2s;
  }}
  .nav-bar a:hover {{ background: #e8f0fe; }}
  .nav-bar .title {{ font-size: 1.1em; font-weight: 600; color: #1a73e8; flex: 1; }}
  .doc-meta {{
    background: #e8f0fe; border-radius: 8px; padding: 10px 14px;
    margin-bottom: 20px; font-size: 0.85em; color: #444;
    display: flex; gap: 16px; flex-wrap: wrap;
  }}
  .doc-meta span {{ display: inline-flex; align-items: center; gap: 4px; }}
  .doc-content {{
    background: #fff; border: 1px solid #e0e0e0; border-radius: 8px;
    padding: 20px; white-space: pre-wrap; word-break: break-word;
    font-size: 0.95em; line-height: 1.7;
  }}
  .copy-btn {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 14px; background: #1a73e8; color: white;
    border: none; border-radius: 6px; cursor: pointer;
    font-size: 0.85em; transition: background 0.2s;
  }}
  .copy-btn:hover {{ background: #1557b0; }}
  .footer {{
    text-align: center; color: #999; font-size: 0.82em;
    margin-top: 24px; padding-top: 16px; border-top: 1px solid #e0e0e0;
  }}
  .copilot-hint {{
    display: none;
  }}

  /* Dark mode */
  @media (prefers-color-scheme: dark) {{
    body {{ background: #1a1a2e; color: #e0e0e0; }}
    .nav-bar {{ border-bottom-color: #333; }}
    .nav-bar a:hover {{ background: #2a2a4e; }}
    .nav-bar .title {{ color: #64b5f6; }}
    .doc-meta {{ background: #2a2a4e; color: #ccc; }}
    .doc-content {{ background: #16213e; border-color: #333; color: #e0e0e0; }}
    .copy-btn {{ background: #1565c0; }}
    .copy-btn:hover {{ background: #1976d2; }}
    .footer {{ border-top-color: #333; color: #666; }}
    .breadcrumb {{ color: #888; }}
    .breadcrumb a {{ color: #64b5f6; }}
    .breadcrumb .sep {{ color: #555; }}
  }}

  /* Print styles */
  @media print {{
    body {{ background: white; color: black; padding: 0.5in; }}
    .nav-bar {{ border-bottom: 1px solid #ccc; }}
    .doc-meta {{ background: #f5f5f5; border: 1px solid #ddd; }}
    .doc-content {{ background: white; border: 1px solid #ddd; }}
    .copy-btn {{ display: none; }}
    .footer {{ border-top: 1px solid #ccc; }}
  }}
</style>
</head>
<body>
<div class="breadcrumb">
  <a href="{escape(index_link)}">首页</a>
  <span class="sep">›</span>
  <span>{escape(breadcrumb_name)}</span>
</div>

<div class="nav-bar">
  <span class="title">📄 {escaped_title}</span>
  <a href="{escape(index_link)}">⬅ 返回首页</a>
</div>

<div class="doc-meta">
  <span>📂 {escaped_folder}</span>
  <span>📏 大小：{escape(file_size_hr)}</span>
  <span>📝 字符：{char_count:,}</span>
  {meta_lines}
  <span>
    <button class="copy-btn" onclick="copyContent()">📋 复制全文</button>
  </span>
</div>

<div class="doc-content" id="doc-content">{escaped_text}</div>

<div class="footer">
  <p>由 FolderRAG Portal 生成 | {escaped_folder}</p>
</div>

<div class="copilot-hint">
  ═══════════════════════════════
  FolderRAG 知识页 | {escaped_title}
  文件大小：{escape(file_size_hr)} | 字符数：{char_count}
  索引位置：{escaped_folder}/{escaped_title}
  ═══════════════════════════════
</div>

<script>
function copyContent() {{
  const content = document.getElementById('doc-content');
  const text = content.textContent || content.innerText;
  navigator.clipboard.writeText(text).then(() => {{
    const btn = document.querySelector('.copy-btn');
    btn.textContent = '\\u2705 已复制';
    setTimeout(() => {{ btn.textContent = '\\ud83d\\udccb 复制全文'; }}, 2000);
  }});
}}
</script>
</body>
</html>"""


def wrap_index_html(
    docs_meta: list,
    folder_name: str,
    folder_path: str,
    total_chars: int,
    generated_at: str,
) -> str:
    """
    生成知识门户首页（index.html）。

    docs_meta: [
        {
            "title": "相对路径",
            "file": "docs/safe_name.html",
            "size": 1234,
            "preview": "前200字摘要",
            "tags": ["关键词1", "关键词2"],
            "size_hr": "12.3 KB",
        },
        ...
    ]
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

        # Skip document cards that have no file (skipped docs)
        if file_link:
            title_html = f'<a class="card-title" href="{file_link}" target="_blank">{title}</a>'
        else:
            title_html = f'<span class="card-title" style="color:#999;cursor:default;">{title}</span>'

        cards_html += f"""
  <div class="doc-card" data-index="{i}" data-search="{title.lower()}">
    <div class="card-header">
      <span class="card-icon">📄</span>
      {title_html}
    </div>
    <div class="card-meta">
      <span>📏 {size_hr}</span>
      <span>📝 {char_count:,} 字符</span>
    </div>
    <div class="card-preview">{preview}…</div>
    <div class="card-tags">{tags_html}</div>
  </div>"""

    # Auto-extract keywords from all docs for keyword cloud
    all_tags_set = set()
    for doc in docs_meta:
        for tag in doc.get("tags", []):
            all_tags_set.add(tag)
    all_tags = sorted(all_tags_set)[:40]

    tags_cloud_html = ""
    for tag in all_tags:
        safe_tag = escape(tag)
        tags_cloud_html += f'<span class="cloud-tag" data-tag="{safe_tag}">{safe_tag}</span> '

    doc_count = len(docs_meta)
    total_size_hr = _format_total_size(docs_meta)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="light dark">
<title>{escaped_folder} — 知识门户</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 960px; margin: 0 auto; padding: 24px 20px;
    background: #f8f9fa; color: #333;
  }}

  /* Header */
  .portal-header {{
    background: linear-gradient(135deg, #1a73e8, #1557b0);
    color: white; border-radius: 12px; padding: 28px 24px;
    margin-bottom: 20px;
  }}
  .portal-header h1 {{ font-size: 1.8em; margin-bottom: 6px; }}
  .portal-header .sub {{ font-size: 0.95em; opacity: 0.9; }}
  .portal-header .stats {{
    display: flex; gap: 20px; margin-top: 12px; font-size: 0.85em;
    flex-wrap: wrap;
  }}
  .portal-header .stats span {{ display: inline-flex; align-items: center; gap: 4px; }}

  /* Search */
  .search-section {{
    background: white; border-radius: 10px; padding: 16px 20px;
    margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }}
  .search-box {{
    width: 100%; padding: 10px 14px; font-size: 1em;
    border: 2px solid #dadce0; border-radius: 8px;
    outline: none; transition: border-color 0.2s;
  }}
  .search-box:focus {{ border-color: #1a73e8; }}
  .search-hint {{ font-size: 0.82em; color: #888; margin-top: 6px; }}

  /* Tag Cloud */
  .tag-cloud {{
    background: white; border-radius: 10px; padding: 12px 16px;
    margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }}
  .tag-cloud-title {{ font-size: 0.85em; color: #666; margin-bottom: 8px; }}
  .cloud-tag {{
    display: inline-block; padding: 2px 10px; margin: 2px 3px;
    background: #e8f0fe; color: #1a73e8; border-radius: 12px;
    font-size: 0.82em; cursor: pointer; transition: all 0.2s;
  }}
  .cloud-tag:hover {{ background: #1a73e8; color: white; }}
  .cloud-tag.active {{ background: #1a73e8; color: white; }}

  /* Document Grid */
  .doc-grid {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 12px;
  }}
  @media (max-width: 600px) {{
    .doc-grid {{ grid-template-columns: 1fr; }}
  }}

  .doc-card {{
    background: white; border: 1px solid #e0e0e0; border-radius: 10px;
    padding: 14px 16px; transition: box-shadow 0.2s, opacity 0.2s;
    opacity: 1;
  }}
  .doc-card.hidden {{ display: none; }}
  .doc-card:hover {{ box-shadow: 0 2px 12px rgba(0,0,0,0.1); }}

  .card-header {{
    display: flex; align-items: center; gap: 8px; margin-bottom: 6px;
  }}
  .card-icon {{ font-size: 1.1em; }}
  .card-title {{
    font-weight: 600; color: #1a73e8; text-decoration: none;
    word-break: break-all; font-size: 0.95em;
  }}
  .card-title:hover {{ text-decoration: underline; }}

  .card-meta {{
    font-size: 0.82em; color: #888; margin-bottom: 6px;
    display: flex; gap: 12px;
  }}

  .card-preview {{
    font-size: 0.88em; color: #555; line-height: 1.5;
    margin-bottom: 8px; display: -webkit-box;
    -webkit-line-clamp: 3; -webkit-box-orient: vertical;
    overflow: hidden;
  }}

  .card-tags {{
    display: flex; flex-wrap: wrap; gap: 4px;
  }}
  .tag {{
    display: inline-block; padding: 1px 8px;
    background: #f0f0f0; color: #666; border-radius: 10px;
    font-size: 0.78em;
  }}

  .empty-state {{
    text-align: center; padding: 40px 20px; color: #888;
    display: none;
  }}
  .empty-state.visible {{ display: block; }}

  .footer {{
    text-align: center; color: #999; font-size: 0.82em;
    margin-top: 24px; padding-top: 16px; border-top: 1px solid #e0e0e0;
  }}

  /* Dark mode for index */
  @media (prefers-color-scheme: dark) {{
    body {{ background: #1a1a2e; color: #e0e0e0; }}
    .search-section {{ background: #16213e; }}
    .search-box {{ background: #1a1a2e; border-color: #333; color: #e0e0e0; }}
    .search-box:focus {{ border-color: #64b5f6; }}
    .tag-cloud {{ background: #16213e; }}
    .tag-cloud-title {{ color: #aaa; }}
    .cloud-tag {{ background: #2a2a4e; color: #64b5f6; }}
    .cloud-tag:hover {{ background: #64b5f6; color: #1a1a2e; }}
    .doc-card {{ background: #16213e; border-color: #333; }}
    .card-title {{ color: #64b5f6; }}
    .card-preview {{ color: #bbb; }}
    .card-meta {{ color: #888; }}
    .tag {{ background: #2a2a4e; color: #aaa; }}
    .footer {{ border-top-color: #333; color: #666; }}
    .empty-state {{ color: #888; }}
  }}

  /* Print styles for index */
  @media print {{
    body {{ background: white; color: black; padding: 0.2in; }}
    .portal-header {{ background: #1a73e8 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .search-section, .tag-cloud {{ display: none; }}
    .doc-card {{ break-inside: avoid; border: 1px solid #ccc; }}
  }}
</style>
</head>
<body>

<div class="portal-header">
  <h1>📁 {escaped_folder}</h1>
  <div class="sub">知识门户 — 从本地文件夹生成的可搜索文档库</div>
  <div class="stats">
    <span>📄 文档数：{doc_count}</span>
    <span>📝 总字符：{total_chars:,}</span>
    <span>💾 总大小：{total_size_hr}</span>
    <span>🕐 生成时间：{escape(generated_at)}</span>
    <span>📂 {escaped_path}</span>
  </div>
</div>

<div class="search-section">
  <input type="text" class="search-box" id="searchInput"
         placeholder="🔍 搜索文档名称或内容...">
  <div class="search-hint">
    💡 输入关键词快速过滤文档 &nbsp;|&nbsp; 点击文档标题在新标签页中打开
    &nbsp;|&nbsp; 打开后按 Ctrl+Shift+. 唤醒 Edge Copilot 提问
  </div>
</div>

<div class="tag-cloud">
  <div class="tag-cloud-title">🏷️ 关键词标签（点击过滤）</div>
  <div>{tags_cloud_html}</div>
</div>

<div class="doc-grid" id="docGrid">
  {cards_html}
</div>

<div class="empty-state" id="emptyState">
  <p>😕 没有找到匹配的文档</p>
  <p style="font-size:0.85em;margin-top:6px;">试试其他关键词</p>
</div>

<div class="footer">
  <p>由 FolderRAG Portal 生成 | 共 {doc_count} 个文档，{total_chars:,} 字符 | {escape(generated_at)}</p>
</div>

<script>
(function() {{
  const searchInput = document.getElementById('searchInput');
  const docGrid = document.getElementById('docGrid');
  const emptyState = document.getElementById('emptyState');
  const cards = docGrid.querySelectorAll('.doc-card');
  const cloudTags = document.querySelectorAll('.cloud-tag');

  function filterDocs(query) {{
    const q = query.toLowerCase().trim();
    let visibleCount = 0;

    cards.forEach(card => {{
      const searchData = card.getAttribute('data-search') || '';
      const match = !q || searchData.includes(q);
      card.classList.toggle('hidden', !match);
      if (match) visibleCount++;
    }});

    emptyState.classList.toggle('visible', visibleCount === 0);
  }}

  searchInput.addEventListener('input', function() {{
    cloudTags.forEach(t => t.classList.remove('active'));
    filterDocs(this.value);
  }});

  cloudTags.forEach(tag => {{
    tag.addEventListener('click', function() {{
      const tagText = this.getAttribute('data-tag') || this.textContent.trim();
      cloudTags.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      searchInput.value = tagText;
      filterDocs(tagText);
    }});
  }});

  searchInput.addEventListener('keydown', function(e) {{
    if (e.key === 'Enter') {{
      filterDocs(this.value);
    }}
  }});
}})();
</script>
</body>
</html>"""


def _format_total_size(docs_meta: list) -> str:
    """计算所有文档的总大小并格式化为人类可读格式。"""
    total = sum(d.get("size", 0) for d in docs_meta)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if total < 1024:
            return f"{total:.1f} {unit}"
        total /= 1024
    return f"{total:.1f} TB"
