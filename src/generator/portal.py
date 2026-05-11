"""
FolderKnowledgeSiteGeneratorForAI Portal — Intelligent paginated knowledge portal generator

Parses a folder into a searchable knowledge portal:
- Each parsed document → independent HTML page (~8000 chars)
- Large documents → multi-page with prev/next navigation
- Unsupported files → shown only in the folder structure tree (no card)
- index.html with search, tag cloud, document cards, and file tree

Optimizations:
  [A] Temp-file based text storage to eliminate memory pressure
  [B] Pre-built shared sitemap + inverted-index related docs (O(N²)→O(N))
  [C] Reduced sitemap entries (100→20) + external CSS
"""

import os
import re
import io
import logging
import tempfile
from datetime import datetime
from collections import Counter, defaultdict

from src.parser.dispatcher import parse_file
from src.generator.templates import wrap_doc_html, wrap_index_html, generate_sitemap_xml, generate_robots_txt

logger = logging.getLogger(__name__)


# ============================================================
#  Utility functions
# ============================================================

def make_safe_filename(filepath: str, base_dir: str) -> str:
    """Generate a safe HTML filename from a file path."""
    rel = os.path.relpath(filepath, base_dir)
    name, _ = os.path.splitext(rel)
    safe = re.sub(r'[<>:"/\\|?*]', '_', name)
    safe = re.sub(r'[. ]+', '_', safe)
    safe = safe.strip('_')
    if not safe:
        safe = "document"
    return f"{safe}.html"


def human_readable_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    if size_bytes == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def extract_keywords(text: str, max_words: int = 8) -> list:
    """Extract keywords from text using frequency + stop word filtering."""
    chinese_chars = re.findall(r'[\u4e00-\u9fff]{2,6}', text)
    english_words = re.findall(r'\b[a-zA-Z]{3,15}\b', text.lower())

    stop_words = {
        'the','and','for','that','this','with','from','have','are','was','were',
        'been','being','has','had','does','did','will','would','could','should',
        'may','might','about','into','over','after','before','between','under',
        'above','such','only','other','than','then','also','very','just','more',
        'some','these','those','html','class','span','div','style','width',
        'height','which','what','when','where','there','their','they','them',
        'like','here','each','both','most','many','much','must','your','its',
        'can','see','way','use','make','new','one','two','how','all','any',
        'not','but','who','out','down','now','even','back','still','well','too',
        'own','while','because','ever','every','same','through','thing','things',
        'number','part','place','long','time','work','year','used','using',
        'based','also','called','without','within','across','along','among',
        'around','first','second','last','next','data','text','file','files',
        'code','type','string','value','name','key','page','list','line','lines',
        'word','words','char','chars','info','information','description','default',
        '的','了','在','是','我','有','和','就','不','人','都','一','一个','上',
        '也','很','到','说','要','去','你','会','着','没有','看','好','自己',
        '这','他','她','它','们','来','与','及','或','以','而','但','又','被',
        '让','对','从','把','向','为','比','等','能','可','所','如','之','其',
        '中','将','还','做','做','给','用','更','最','并','过','开','只','有',
        '学','年','月','日','时','间','后','前','下','此','因','如','何','道',
        '种','些','几','那','哪','两','多','少','个','每','既','除了','虽然',
        '因为','所以','但是','如果','可以','应该','需要','已经','没有','这些',
        '那些','关于','由于','而且','或者','不是','就是','而是','还是','并且',
        '从而','因此','其中','之一','之间','方面','部分','同时','之后','之前',
        '今天','明天','昨天','现在','然后','比如','比较','非常','一定','可能',
        '全部','最后','开始','继续','以及','不过','只是','为了','那里','这里',
        '怎么','什么','如果','否则','另外','帮助','关于','使用','提供','通过',
        '进行','包括','还有','以及','其他','其中','由于','因此','所有','功能',
        '支持','方法','方式','配置','设置','参数',
    }

    counter = Counter()
    for word in chinese_chars:
        if word not in stop_words:
            counter[word] += 1
    for word in english_words:
        if word not in stop_words and not word.isdigit() and len(word) >= 3:
            counter[word] += 1

    keywords = []
    for word, count in counter.most_common(max_words * 2):
        if re.match(r'^\d+$', word):
            continue
        keywords.append(word)
        if len(keywords) >= max_words:
            break
    return keywords


def split_large_text(text: str, max_chars: int = 12000) -> list:
    """Split text into chunks of max_chars. Prefers # heading boundaries.
    Returns [(text, part_title)]."""
    if len(text) <= max_chars:
        return [(text, None)]

    # First, try to split on Markdown headings (## or ###)
    heading_matches = list(re.finditer(r'^(#{1,4})\s+(.+)$', text, re.MULTILINE))

    if heading_matches:
        chunks = []
        current_chunk_start = 0

        for i, match in enumerate(heading_matches):
            heading_pos = match.start()
            heading_title = match.group(2).strip()

            if (heading_pos - current_chunk_start > max_chars * 0.8
                    and current_chunk_start > 0):
                chunks.append((text[current_chunk_start:heading_pos].strip(),
                               heading_title))
                current_chunk_start = heading_pos

        remaining = text[current_chunk_start:].strip()
        if remaining:
            last_title = heading_matches[-1].group(2).strip() if heading_matches else ""
            chunks.append((remaining, last_title))

        if len(chunks) >= 2:
            final_chunks = []
            for chunk_text, chunk_title in chunks:
                if len(chunk_text) > max_chars * 1.5:
                    sub_chunks = _split_by_paragraphs(chunk_text, max_chars, chunk_title)
                    final_chunks.extend(sub_chunks)
                else:
                    final_chunks.append((chunk_text, chunk_title))
            return final_chunks

    return _split_by_paragraphs(text, max_chars)


def _split_by_paragraphs(text: str, max_chars: int, base_title: str = None) -> list:
    """Split text by paragraphs, falling back when heading-based split isn't sufficient."""
    paragraphs = text.split('\n\n')
    parts = []
    current_part = []
    current_len = 0
    part_num = 1

    section_titles = []
    for line in text.split('\n'):
        m = re.match(r'^#{1,4}\s+(.+)$', line.strip())
        if m:
            section_titles.append(m.group(1).strip())

    for para in paragraphs:
        para_len = len(para)
        if current_len + para_len > max_chars and current_part:
            combined = '\n\n'.join(current_part)
            subtitle = ""
            if part_num <= len(section_titles) and not base_title:
                subtitle = " - %s" % section_titles[part_num - 1]
            part_title = "Part %d%s" % (part_num, subtitle)
            if base_title:
                part_title = "%s - %s" % (base_title, part_title)
            parts.append((combined, part_title))
            current_part = [para]
            current_len = para_len
            part_num += 1
        else:
            current_part.append(para)
            current_len += para_len

    if current_part:
        combined = '\n\n'.join(current_part)
        subtitle = ""
        if part_num <= len(section_titles) and not base_title:
            subtitle = " - %s" % section_titles[part_num - 1]
        part_title = "Part %d%s" % (part_num, subtitle)
        if base_title:
            part_title = "%s - %s" % (base_title, part_title)
        parts.append((combined, part_title))

    return parts


# ============================================================
#  Temp-file helper (Optimization A)
# ============================================================

def _write_text_to_temp(text: str, prefix: str = "portal_") -> str:
    """Write text to a temp file and return its path."""
    fd, tmp_path = tempfile.mkstemp(suffix=".txt", prefix=prefix)
    with io.open(fd, 'w', encoding='utf-8') as f:
        f.write(text)
    return tmp_path


def _read_text_from_temp(tmp_path: str) -> str:
    """Read text from a temp file."""
    with open(tmp_path, 'r', encoding='utf-8') as f:
        return f.read()


def _cleanup_temp(tmp_path: str):
    """Delete a temp file if it exists."""
    try:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
    except Exception:
        pass


# ============================================================
#  Inverted-index builder (Optimization B)
# ============================================================

def _build_keyword_inverted_index(docs_meta: list) -> dict:
    """Build inverted index: keyword → list of doc meta dicts."""
    kw_index = defaultdict(list)
    for doc in docs_meta:
        if doc.get("skipped") or not doc.get("file"):
            continue
        for tag in doc.get("tags", []):
            tag_lower = tag.lower()
            kw_index[tag_lower].append(doc)
    return dict(kw_index)


def _find_related_docs_via_index(
    current_title: str,
    current_keywords: list,
    kw_index: dict,
    max_items: int = 5,
) -> list:
    """
    Find related documents using inverted index.
    Instead of O(N) scan of all docs, only examine candidates from keyword index.
    """
    if not current_keywords or not kw_index:
        return []

    current_kw_set = set(k.lower() for k in current_keywords)
    if not current_kw_set:
        return []

    # Collect candidate docs from matching keywords
    candidates = {}
    for kw in current_kw_set:
        for doc in kw_index.get(kw, []):
            doc_title = doc.get("title", "")
            if doc_title == current_title:
                continue
            if doc_title not in candidates:
                candidates[doc_title] = {"doc": doc, "kw_set": set()}
            candidates[doc_title]["kw_set"].add(kw)

    if not candidates:
        return []

    # Score by Jaccard similarity
    scored = []
    for title, info in candidates.items():
        doc_tags = [t.lower() for t in info["doc"].get("tags", [])]
        doc_kw_set = set(doc_tags)
        intersection = len(current_kw_set & doc_kw_set)
        union = len(current_kw_set | doc_kw_set)
        if union == 0:
            continue
        score = intersection / union
        if score > 0:
            scored.append((score, info["doc"]))

    scored.sort(key=lambda x: -x[0])
    return scored[:max_items]


# ============================================================
#  File tree builder
# ============================================================

def build_file_tree_html(folder_path: str, docs_dir: str) -> str:
    """
    Build HTML unordered list of the folder structure.
    Parsed files link to their doc pages; skipped files are shown grayed out.
    """
    tree = {"_children": {}, "_files": []}

    for dirpath, _, filenames in os.walk(folder_path):
        rel_dir = os.path.relpath(dirpath, folder_path)
        if rel_dir == ".":
            rel_dir = ""
        parts = rel_dir.split(os.sep) if rel_dir else []

        node = tree
        for p in parts:
            if p not in node["_children"]:
                node["_children"][p] = {"_children": {}, "_files": []}
            node = node["_children"][p]

        for fname in sorted(filenames, key=str.lower):
            if fname.startswith('.'):
                continue
            full_path = os.path.join(dirpath, fname)
            if not os.path.isfile(full_path):
                continue
            size = os.path.getsize(full_path)
            size_hr = human_readable_size(size)
            safe_name = make_safe_filename(full_path, folder_path)
            doc_link = "docs/%s" % safe_name
            is_parsed = os.path.exists(os.path.join(docs_dir, safe_name))
            node["_files"].append({
                "name": fname,
                "size_hr": size_hr,
                "doc_link": doc_link if is_parsed else None,
                "parsed": is_parsed,
            })

    def _render(node, depth=0):
        indent = "  " * depth
        html = ""
        for fname in sorted(node["_children"].keys()):
            child = node["_children"][fname]
            html += '%s<li class="tree-folder">\U0001f4c1 %s</li>\n' % (indent, fname)
            html += _render(child, depth + 1)
        for f in node["_files"]:
            if f["parsed"] and f["doc_link"]:
                html += '%s<li class="tree-file">\U0001f4c4 <a href="%s">%s</a> <span class="tree-size">%s</span></li>\n' % (
                    indent, f["doc_link"], f["name"], f["size_hr"])
            else:
                html += '%s<li class="tree-file skipped">\u23ed\ufe0f %s <span class="tree-size">%s</span></li>\n' % (
                    indent, f["name"], f["size_hr"])
        return html

    return _render(tree)


# ============================================================
#  Main portal generation
# ============================================================

def generate_portal(
    folder_path: str,
    output_dir: str,
    max_chars_per_page: int = 12000,
    include_skipped: bool = True,
    show_progress: bool = True,
    language: str = "en",
) -> dict:
    """
    Parse a folder into a paginated, searchable knowledge portal.

    Args:
        folder_path: Path to the folder to scan
        output_dir: Output directory path
        max_chars_per_page: Max characters per doc page (default 12000)
        include_skipped: Show unsupported files in the file tree
        show_progress: Show CLI progress output

    Returns:
        dict with: doc_count, total_chars, output_dir, index_file, errors, skipped
    """
    if not os.path.isdir(folder_path):
        raise ValueError("Not a valid folder: %s" % folder_path)

    # Check output directory
    if os.path.exists(output_dir):
        existing = [i for i in os.listdir(output_dir) if not i.startswith('.')]
        if existing:
            print("[Note] Output dir exists & non-empty: %s" % output_dir)
            print("       Content: %d items (overwriting matching files)" % len(existing))

    docs_dir = os.path.join(output_dir, "docs")
    assets_dir = os.path.join(output_dir, "assets")
    os.makedirs(docs_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    # Write shared CSS files (Optimization C: external CSS)
    _write_shared_css(assets_dir)

    # Collect all files
    all_files = []
    for dirpath, _, filenames in os.walk(folder_path):
        for fname in filenames:
            if fname.startswith('.'):
                continue
            full_path = os.path.join(dirpath, fname)
            if os.path.isfile(full_path):
                all_files.append(full_path)

    total_files = len(all_files)
    folder_name = os.path.basename(os.path.abspath(folder_path))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    docs_meta = []
    page_entries = []
    temp_paths = []           # Track temp files for cleanup (Optimization A)
    total_chars = 0
    parsed_count = 0
    skipped_count = 0
    error_count = 0

    if show_progress:
        print("  [Scan] Found %d files, parsing..." % total_files)

    for file_idx, full_path in enumerate(all_files):
        rel_path = os.path.relpath(full_path, folder_path)
        file_size = os.path.getsize(full_path)
        size_hr = human_readable_size(file_size)

        # Progress bar
        if show_progress:
            pct = (file_idx + 1) / total_files * 100
            bar_len = 30
            filled = int(bar_len * (file_idx + 1) / total_files)
            bar = '#' * filled + '.' * (bar_len - filled)
            print("\r  [%s] %d/%d (%.0f%%) - %s" % (
                bar, file_idx + 1, total_files, pct, rel_path[:50]),
                end='', flush=True)

        # Parse
        try:
            result = parse_file(full_path)
        except Exception as e:
            logger.exception("Error parsing %s: %s", rel_path, e)
            if show_progress:
                print("\n  [Error] %s - %s" % (rel_path, e))
            error_count += 1
            continue

        # Get timestamps
        try:
            mtime = os.path.getmtime(full_path)
            ctime = os.path.getctime(full_path)
            mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            ctime_str = datetime.fromtimestamp(ctime).strftime("%Y-%m-%d %H:%M")
        except Exception:
            mtime_str = ""
            ctime_str = ""

        # Unsupported or empty → skip from cards, show only in tree
        if result is None:
            skipped_count += 1
            continue

        text = (result.get("text") or "").strip()
        if not text:
            skipped_count += 1
            continue

        # Split large documents
        text_parts = split_large_text(text, max_chars_per_page)
        safe_base = make_safe_filename(full_path, folder_path)
        base_name, base_ext = os.path.splitext(safe_base)

        part_filenames = []
        for part_idx in range(len(text_parts)):
            fname = safe_base if part_idx == 0 else "%s_part%d%s" % (base_name, part_idx + 1, base_ext)
            part_filenames.append(fname)

        # First pass: collect metadata; write part_text to temp files (Optimization A)
        for part_idx, (part_text, part_title) in enumerate(text_parts):
            char_count = len(part_text)
            total_chars += char_count

            doc_title = rel_path
            if part_title:
                doc_title = "%s - %s" % (rel_path, part_title)

            total_parts = len(text_parts)
            prev_page = None
            next_page = None
            page_info = None

            if total_parts > 1:
                page_info = "Page %d of %d" % (part_idx + 1, total_parts)
                if part_idx > 0:
                    prev_page = part_filenames[part_idx - 1]
                if part_idx < total_parts - 1:
                    next_page = part_filenames[part_idx + 1]

            keywords = extract_keywords(part_text)
            preview = part_text[:200].replace('\n', ' ').strip()

            if total_parts > 1 and part_idx == 0:
                display_title = "%s (p1/%d)" % (rel_path, total_parts)
            elif total_parts > 1:
                display_title = "%s (p%d)" % (rel_path, part_idx + 1)
            else:
                display_title = rel_path

            entry_meta = {
                "title": display_title,
                "file": "docs/%s" % part_filenames[part_idx],
                "size": char_count,
                "size_hr": size_hr,
                "preview": preview,
                "tags": keywords[:5],
                "skipped": False,
                "mtime": mtime_str,
                "ctime": ctime_str,
            }
            docs_meta.append(entry_meta)

            # Optimization A: Write part_text to temp file instead of keeping in memory
            tmp_path = _write_text_to_temp(part_text, prefix="portal_")
            temp_paths.append(tmp_path)

            page_entries.append({
                "part_idx": part_idx,
                "part_fname": part_filenames[part_idx],
                "doc_title": doc_title,
                "tmp_path": tmp_path,            # ← temp file path instead of text
                "prev_page": prev_page,
                "next_page": next_page,
                "page_info": page_info,
                "keywords": keywords,
                "total_parts": total_parts,
                "char_count": char_count,
                "rel_path": rel_path,
                "size_hr": size_hr,
                "mtime_str": mtime_str,
                "ctime_str": ctime_str,
            })
            parsed_count += 1

        if len(text_parts) > 1 and show_progress:
            print("\n  [Split] %s -> %d pages" % (rel_path, len(text_parts)))

    if show_progress:
        print()

    docs_meta.sort(key=lambda d: d.get("title", "").lower())

    # Optimization B: Pre-build shared sitemap HTML (single call, not per-page)
    # Use max_items=20 for smaller pages (Optimization C)
    from src.generator.templates import _build_doc_sitemap_html as _build_sitemap
    shared_sitemap_html = _build_sitemap(docs_meta, current_title="", index_link="../index.html", max_items=20) if docs_meta else ""

    # Optimization B: Build inverted index for related docs
    kw_index = _build_keyword_inverted_index(docs_meta)

    total_pages = len(page_entries)
    if show_progress and total_pages > 0:
        print("  [Generate] Generating %d HTML pages..." % total_pages)

    # Second pass: render HTML pages (Optimization A: read from temp files)
    for pg_idx, entry in enumerate(page_entries):
        if show_progress and total_pages > 0:
            pct = (pg_idx + 1) / total_pages * 100
            bar_len = 30
            filled = int(bar_len * (pg_idx + 1) / total_pages)
            bar = '#' * filled + '.' * (bar_len - filled)
            print("\r  [%s] %d/%d (%.0f%%) - writing %s" % (
                bar, pg_idx + 1, total_pages, pct, entry["part_fname"][:40]),
                end='', flush=True)

        # Read text from temp file (Optimization A)
        part_text = _read_text_from_temp(entry["tmp_path"])

        # Optimization B: Use inverted-index for related docs
        related_docs = _find_related_docs_via_index(
            entry["doc_title"], entry["keywords"], kw_index, max_items=5
        )

        # Determine CSS link path: from docs/ subdirectory → ../assets/doc.css
        css_path = "../assets/doc.css"

        page_html = wrap_doc_html(
            title=entry["doc_title"],
            text=part_text,
            folder_name=folder_name,
            char_count=entry["char_count"],
            file_size_hr=entry["size_hr"],
            index_link="../index.html",
            mtime=entry["mtime_str"],
            ctime=entry["ctime_str"],
            prev_page=entry["prev_page"],
            next_page=entry["next_page"],
            page_info=entry["page_info"],
            keywords=entry["keywords"],
            rel_path=entry["rel_path"],
            total_parts=entry["total_parts"],
            part_idx=entry["part_idx"],
            all_docs_meta=docs_meta,
            # Optimization B: pass pre-built sitemap
            prebuilt_sitemap=shared_sitemap_html,
            # Optimization B: pass pre-computed related docs
            prebuilt_related_docs=related_docs,
            # Optimization C: external CSS path
            css_path=css_path,
        )
        doc_path = os.path.join(docs_dir, entry["part_fname"])
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(page_html)

        # Clean up temp file immediately after use (Optimization A)
        _cleanup_temp(entry["tmp_path"])

    if show_progress and total_pages > 0:
        print()

    # Build file tree (includes skipped files for display)
    file_tree_html = build_file_tree_html(folder_path, docs_dir) if include_skipped else ""

    # Generate index.html
    if docs_meta or file_tree_html:
        index_html = wrap_index_html(
            docs_meta=docs_meta,
            folder_name=folder_name,
            folder_path=os.path.abspath(folder_path),
            total_chars=total_chars,
            generated_at=now,
            file_tree_html=file_tree_html,
            language=language,
            css_path="assets/index.css",  # Optimization C: external CSS
        )
        index_path = os.path.join(output_dir, "index.html")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_html)
        logger.info("Portal index: %s", index_path)
    else:
        index_path = None
        logger.warning("No documents parsed!")

    # Generate sitemap.xml
    if docs_meta:
        sitemap_xml = generate_sitemap_xml(docs_meta)
        sitemap_path = os.path.join(output_dir, "sitemap.xml")
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_xml)
        logger.info("Sitemap: %s", sitemap_path)

        # Generate robots.txt
        robots_txt = generate_robots_txt()
        robots_path = os.path.join(output_dir, "robots.txt")
        with open(robots_path, 'w', encoding='utf-8') as f:
            f.write(robots_txt)
        logger.info("Robots.txt: %s", robots_path)

    # Clean up any remaining temp files (safety net)
    for tmp_path in temp_paths:
        _cleanup_temp(tmp_path)

    return {
        "doc_count": parsed_count,
        "total_chars": total_chars,
        "skipped": skipped_count,
        "errors": error_count,
        "output_dir": output_dir,
        "index_file": index_path,
        "folder_name": folder_name,
        "sitemap_file": os.path.join(output_dir, "sitemap.xml") if docs_meta else None,
        "robots_file": os.path.join(output_dir, "robots.txt") if docs_meta else None,
    }


# ============================================================
#  Shared CSS writer (Optimization C)
# ============================================================

def _write_shared_css(assets_dir: str):
    """Write external CSS files shared by all pages."""
    # doc.css — styles for doc_page.html (extracted from template)
    doc_css = """/* FolderKnowledgeSiteGeneratorForAI — Doc Page Styles */
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
  max-width: 900px; margin: 0 auto; padding: 24px 20px;
  background: #f8f9fa; color: #333; line-height: 1.7;
}
.lang-en { color: #888; font-size: 0.92em; }
.lang-zh + .lang-en::before { content: ""; }
nav[aria-label="Breadcrumb"] {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.85em; color: #888; margin-bottom: 8px; flex-wrap: wrap;
}
nav[aria-label="Breadcrumb"] a { color: #1a73e8; text-decoration: none; }
nav[aria-label="Breadcrumb"] a:hover { text-decoration: underline; }
nav[aria-label="Breadcrumb"] .sep { color: #ccc; user-select: none; }
.nav-bar {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 20px; padding-bottom: 12px;
  border-bottom: 1px solid #e0e0e0; flex-wrap: wrap;
}
.nav-bar .title {
  font-size: 1.1em; font-weight: 600; color: #1a73e8;
  flex: 1; word-break: break-all;
}
.nav-bar a {
  color: #1a73e8; text-decoration: none; font-size: 0.9em;
  padding: 5px 14px; border-radius: 6px; transition: background 0.2s;
  white-space: nowrap;
}
.nav-bar a:hover { background: #e8f0fe; }
.doc-meta {
  background: #e8f0fe; border-radius: 8px; padding: 10px 14px;
  margin-bottom: 20px; font-size: 0.85em; color: #444;
  display: flex; gap: 12px; flex-wrap: wrap; align-items: center;
}
.doc-meta span { display: inline-flex; align-items: center; gap: 4px; }
.doc-meta .copy-btn {
  margin-left: auto; display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 14px; background: #1a73e8; color: white;
  border: none; border-radius: 6px; cursor: pointer;
  font-size: 0.85em; transition: background 0.2s;
}
.doc-meta .copy-btn:hover { background: #1557b0; }
.progress-bar-container {
  width: 100%; height: 4px;
  background: #e0e0e0; border-radius: 2px;
  margin-bottom: 12px; overflow: hidden;
}
.progress-bar-fill {
  height: 100%; background: #1a73e8;
  border-radius: 2px; transition: width 0.3s ease;
}
.doc-summary {
  background: #f0f4ff; border: 1px solid #d0d8f0;
  border-radius: 8px; padding: 12px 16px;
  margin-bottom: 20px; font-size: 0.85em; color: #444; line-height: 1.6;
}
.doc-summary .sum-title { font-weight: 600; color: #1a73e8; margin-bottom: 6px; }
.doc-summary .sum-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 4px; }
.doc-summary .sum-label { color: #888; font-weight: 500; min-width: 60px; }
.doc-summary .sum-keywords { display: flex; gap: 4px; flex-wrap: wrap; }
.doc-summary .sum-tag {
  display: inline-block; padding: 1px 8px;
  background: #e0e8ff; color: #1a73e8; border-radius: 10px; font-size: 0.9em;
}
.doc-summary .sum-text { margin-top: 6px; padding-top: 6px; border-top: 1px solid #d0d8f0; color: #555; line-height: 1.5; }
.toc-container {
  background: #f8f9fa; border: 1px solid #e0e0e0;
  border-radius: 8px; padding: 12px 16px; margin-bottom: 20px;
}
.toc-title { font-weight: 600; color: #1a73e8; font-size: 0.9em; margin-bottom: 8px; }
.toc-list { list-style: none; padding: 0; margin: 0; }
.toc-list li { padding: 2px 0; font-size: 0.85em; }
.toc-list a { color: #1a73e8; text-decoration: none; }
.toc-list a:hover { text-decoration: underline; }
.toc-h2 { padding-left: 0; }
.toc-h3 { padding-left: 16px; }
.toc-h4 { padding-left: 32px; }
.doc-content {
  background: #fff; border: 1px solid #e0e0e0; border-radius: 8px;
  padding: 24px; white-space: pre-wrap; word-break: break-word;
  font-size: 0.95em; line-height: 1.7;
}
.related-docs {
  background: #f8f9fa; border: 1px solid #e0e0e0;
  border-radius: 8px; padding: 12px 16px;
  margin-top: 20px; margin-bottom: 20px;
}
.related-title { font-weight: 600; color: #1a73e8; font-size: 0.9em; margin-bottom: 8px; }
.related-list { list-style: none; padding: 0; margin: 0; }
.related-list li { padding: 3px 0; font-size: 0.85em; }
.related-list a { color: #1a73e8; text-decoration: none; }
.related-list a:hover { text-decoration: underline; }
.related-list .rel-score { color: #999; font-size: 0.85em; }
nav[aria-label="Pagination"] {
  display: flex; justify-content: center; align-items: center;
  gap: 16px; margin-bottom: 20px; padding: 10px 0; flex-wrap: wrap;
}
.page-nav {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 6px 16px; background: #1a73e8; color: white;
  text-decoration: none; border-radius: 6px;
  font-size: 0.9em; transition: background 0.2s;
}
.page-nav:hover { background: #1557b0; }
.page-info { font-size: 0.85em; color: #888; }
.footer {
  text-align: center; color: #999; font-size: 0.82em;
  margin-top: 24px; padding-top: 16px; border-top: 1px solid #e0e0e0;
}
.copilot-hint { display: none; }
@media (prefers-color-scheme: dark) {
  body { background: #1a1a2e; color: #e0e0e0; }
  .lang-en { color: #999; }
  nav[aria-label="Breadcrumb"] { color: #888; }
  nav[aria-label="Breadcrumb"] a { color: #64b5f6; }
  nav[aria-label="Breadcrumb"] .sep { color: #555; }
  .nav-bar { border-bottom-color: #333; }
  .nav-bar .title { color: #64b5f6; }
  .nav-bar a { color: #64b5f6; }
  .nav-bar a:hover { background: #2a2a4e; }
  .doc-meta { background: #2a2a4e; color: #ccc; }
  .doc-meta .copy-btn { background: #1565c0; }
  .doc-meta .copy-btn:hover { background: #1976d2; }
  .progress-bar-container { background: #333; }
  .progress-bar-fill { background: #64b5f6; }
  .doc-summary { background: #1a2640; border-color: #2a3a5a; color: #ccc; }
  .doc-summary .sum-title { color: #64b5f6; }
  .doc-summary .sum-tag { background: #2a3a5a; color: #64b5f6; }
  .doc-summary .sum-text { border-top-color: #2a3a5a; color: #aaa; }
  .toc-container { background: #1a1a2e; border-color: #333; }
  .toc-title { color: #64b5f6; }
  .toc-list a { color: #64b5f6; }
  .doc-content { background: #16213e; border-color: #333; color: #e0e0e0; }
  .related-docs { background: #1a1a2e; border-color: #333; }
  .related-title { color: #64b5f6; }
  .related-list a { color: #64b5f6; }
  .related-list .rel-score { color: #666; }
  .page-nav { background: #1565c0; }
  .page-nav:hover { background: #1976d2; }
  .page-info { color: #888; }
  .footer { border-top-color: #333; color: #666; }
}
@media print {
  body { background: white; color: black; padding: 0.5in; }
  .nav-bar { border-bottom: 1px solid #ccc; }
  .doc-meta { background: #f5f5f5; border: 1px solid #ddd; }
  .doc-summary { background: #f5f5f5; border: 1px solid #ddd; }
  .toc-container { display: none; }
  .doc-content { background: white; border: 1px solid #ddd; }
  .related-docs { display: none; }
  .doc-meta .copy-btn, nav[aria-label="Pagination"], .doc-summary { display: none; }
  .footer { border-top: 1px solid #ccc; }
}
"""
    with open(os.path.join(assets_dir, "doc.css"), 'w', encoding='utf-8') as f:
        f.write(doc_css)

    # index.css — minimal shared styles for index_page.html
    index_css = """/* FolderKnowledgeSiteGeneratorForAI — Index Page Styles */
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
  background: #f8f9fa; color: #333; line-height: 1.6;
}
/* Minimal styles; most styling is inline in index_page.html template */
"""
    with open(os.path.join(assets_dir, "index.css"), 'w', encoding='utf-8') as f:
        f.write(index_css)