"""
FolderKnowledgeSiteGeneratorForAI Portal — Intelligent paginated knowledge portal generator

Parses a folder into a searchable knowledge portal:
- Each parsed document → independent HTML page (~8000 chars)
- Large documents → multi-page with prev/next navigation
- Unsupported files → shown only in the folder structure tree (no card)
- index.html with search, tag cloud, document cards, and file tree
"""

import os
import re
import logging
from datetime import datetime
from collections import Counter

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
    # We collect all heading positions and titles
    heading_matches = list(re.finditer(r'^(#{1,4})\s+(.+)$', text, re.MULTILINE))

    # If we have enough headings to make meaningful splits, use them
    if heading_matches:
        # Estimate: we want each chunk to be around max_chars
        # Group headings into chunks
        chunks = []
        current_chunk_start = 0

        for i, match in enumerate(heading_matches):
            heading_pos = match.start()
            heading_title = match.group(2).strip()

            # If this heading is far enough from the start of the current chunk,
            # and we're not at the first heading, create a split point
            if (heading_pos - current_chunk_start > max_chars * 0.8
                    and current_chunk_start > 0):
                # End this chunk at the previous heading
                chunks.append((text[current_chunk_start:heading_pos].strip(),
                               heading_title))
                current_chunk_start = heading_pos

        # Add remaining text as final chunk
        remaining = text[current_chunk_start:].strip()
        if remaining:
            last_title = heading_matches[-1].group(2).strip() if heading_matches else ""
            chunks.append((remaining, last_title))

        # If we got 2+ chunks from heading-based splitting, use them
        if len(chunks) >= 2:
            # Check if any chunk is still too large and needs further splitting
            final_chunks = []
            for chunk_text, chunk_title in chunks:
                if len(chunk_text) > max_chars * 1.5:
                    # Need to sub-split this chunk by paragraphs
                    sub_chunks = _split_by_paragraphs(chunk_text, max_chars, chunk_title)
                    final_chunks.extend(sub_chunks)
                else:
                    final_chunks.append((chunk_text, chunk_title))
            return final_chunks

    # Fall back to paragraph-based splitting
    return _split_by_paragraphs(text, max_chars)


def _split_by_paragraphs(text: str, max_chars: int, base_title: str = None) -> list:
    """Split text by paragraphs, falling back when heading-based split isn't sufficient."""
    paragraphs = text.split('\n\n')
    parts = []
    current_part = []
    current_len = 0
    part_num = 1

    # Collect section titles for naming
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
    os.makedirs(docs_dir, exist_ok=True)

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

        # First pass: collect all metadata (without related docs)
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
            page_entries.append({
                "part_idx": part_idx,
                "part_fname": part_filenames[part_idx],
                "doc_title": doc_title,
                "part_text": part_text,
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

    # Second pass: render HTML pages with complete docs_meta (for related docs)
    for entry in page_entries:
        page_html = wrap_doc_html(
            title=entry["doc_title"],
            text=entry["part_text"],
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
        )
        doc_path = os.path.join(docs_dir, entry["part_fname"])
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(page_html)

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