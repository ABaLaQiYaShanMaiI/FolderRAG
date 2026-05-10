"""
FolderRAG Portal - 智能分页知识门户生成器

将文件夹中的文档解析为「可搜索的知识门户」：
- 每个文档生成一个独立 HTML 页面（控制在 ~8000 字符以内）
- 超大文档自动拆分为多个页面，带「上一页/下一页」导航
- 不支持的文档类型生成占位页面，内容为「该文件类型不支持解析」
- index.html 作为总入口，带搜索框、关键词云、文档卡片
- 适合在 Edge Copilot 中打开，让 AI 完整读取每个页面
"""

import os
import re
import logging
from datetime import datetime
from collections import Counter

from src.parser.dispatcher import parse_file
from src.generator.templates import wrap_doc_html, wrap_index_html, wrap_skipped_html

logger = logging.getLogger(__name__)


# ============================================================
#  Utility functions
# ============================================================

def make_safe_filename(filepath: str, base_dir: str) -> str:
    """
    根据文件路径生成安全的 HTML 文件名。
    例如：'技术文档/需求说明书.pdf' -> '技术文档_需求说明书_pdf.html'
    """
    # Get relative path
    rel = os.path.relpath(filepath, base_dir)
    # Remove extension
    name, _ = os.path.splitext(rel)
    # Replace unsafe chars
    safe = re.sub(r'[<>:"/\\\\|?*]', '_', name)
    safe = re.sub(r'[. ]+', '_', safe)
    safe = safe.strip('_')
    if not safe:
        safe = "document"
    return f"{safe}.html"


def human_readable_size(size_bytes: int) -> str:
    """将字节数转换为人类可读格式。"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def extract_keywords(text: str, max_words: int = 8) -> list:
    """
    从文本中提取关键词标签。
    使用简单的频率统计 + 长度过滤 + 停用词过滤。
    """
    # Chinese + English word pattern
    chinese_chars = re.findall(r'[\u4e00-\u9fff]{2,6}', text)
    english_words = re.findall(r'\b[a-zA-Z]{3,15}\b', text.lower())

    # Comprehensive stop words list (Chinese + English)
    stop_words = {
        # English common words
        'the', 'and', 'for', 'that', 'this', 'with', 'from', 'have',
        'are', 'was', 'were', 'been', 'being', 'has', 'had', 'does',
        'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'about', 'into', 'over', 'after', 'before', 'between',
        'under', 'above', 'such', 'only', 'other', 'than', 'then',
        'also', 'very', 'just', 'more', 'some', 'these', 'those',
        'html', 'class', 'span', 'div', 'style', 'width', 'height',
        'which', 'what', 'when', 'where', 'there', 'their', 'they',
        'them', 'than', 'then', 'like', 'here', 'each', 'both',
        'most', 'many', 'much', 'must', 'your', 'its', 'can', 'see',
        'way', 'use', 'make', 'new', 'one', 'two', 'how', 'all',
        'any', 'not', 'but', 'who', 'out', 'down', 'now', 'even',
        'back', 'still', 'well', 'too', 'own', 'while', 'because',
        'ever', 'every', 'same', 'through', 'thing', 'things',
        'number', 'part', 'place', 'long', 'time', 'work', 'year',
        'used', 'using', 'based', 'also', 'called', 'without',
        'within', 'across', 'along', 'among', 'around',
        'first', 'second', 'last', 'next', 'many', 'much',
        'data', 'text', 'file', 'files', 'code', 'type',
        'string', 'value', 'name', 'key', 'page', 'list',
        'line', 'lines', 'word', 'words', 'char', 'chars',
        'info', 'information', 'description', 'default',
        # Chinese common stop words
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
        '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
        '你', '会', '着', '没有', '看', '好', '自己', '这', '他', '她',
        '它', '们', '来', '与', '及', '或', '以', '而', '但', '又',
        '被', '让', '对', '从', '把', '向', '为', '为', '比', '等',
        '能', '可', '所', '如', '之', '其', '中', '将', '还', '做',
        '做', '给', '用', '更', '最', '并', '过', '开', '只', '有',
        '学', '年', '月', '日', '时', '间', '后', '前', '时', '下',
        '此', '因', '如', '何', '道', '种', '些', '几', '那', '哪',
        '两', '多', '少', '个', '些', '每', '既', '除了', '虽然',
        '因为', '所以', '但是', '如果', '可以', '应该', '需要',
        '已经', '没有', '这些', '那些', '关于', '由于', '而且',
        '或者', '不是', '就是', '而是', '还是', '并且', '从而',
        '因此', '其中', '之一', '之间', '方面', '部分', '而且',
        '同时', '之后', '之前', '今天', '明天', '昨天', '现在',
        '然后', '比如', '比较', '非常', '一定', '可能', '全部',
        '最后', '开始', '继续', '以及', '不过', '只是', '为了',
        '那里', '这里', '怎么', '什么', '如果', '否则', '另外',
        '帮助', '关于', '使用', '提供', '通过', '进行', '包括',
        '还有', '以及', '其他', '其中', '由于', '因此', '所有',
        '功能', '支持', '方法', '方式', '配置', '设置', '参数',
    }

    # Count frequency
    counter = Counter()

    for word in chinese_chars:
        if word not in stop_words:
            counter[word] += 1

    for word in english_words:
        if word not in stop_words and not word.isdigit() and len(word) >= 3:
            counter[word] += 1

    # Return most common words (ensure they have actual meaning)
    keywords = []
    for word, count in counter.most_common(max_words * 2):
        # Skip pure number strings
        if re.match(r'^\d+$', word):
            continue
        keywords.append(word)
        if len(keywords) >= max_words:
            break

    return keywords


def split_large_text(text: str, max_chars: int = 8000) -> list:
    """
    将大文本拆分为多个片段，每个片段不超过 max_chars 字符。
    返回 [(part1, part1_title), (part2, part2_title), ...]
    part1_title 对第一部分为 None，其余部分为章节标题或 "Part N"
    """
    if len(text) <= max_chars:
        return [(text, None)]

    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    parts = []
    current_part = []
    current_len = 0
    part_num = 1

    # Find sections from markdown headings
    section_titles = []
    for line in text.split('\n'):
        m = re.match(r'^#{1,4}\s+(.+)$', line.strip())
        if m:
            section_titles.append(m.group(1).strip())

    for para in paragraphs:
        para_len = len(para)
        if current_len + para_len > max_chars and current_part:
            # Save current part
            combined = '\n\n'.join(current_part)
            # Generate part title
            subtitle = ""
            if part_num <= len(section_titles):
                subtitle = " - %s" % section_titles[part_num - 1]
            part_title = "Part %d%s" % (part_num, subtitle)
            parts.append((combined, part_title))
            current_part = [para]
            current_len = para_len
            part_num += 1
        else:
            current_part.append(para)
            current_len += para_len

    # Last part - if it's the only part after splitting, no special title
    if current_part:
        combined = '\n\n'.join(current_part)
        parts.append((combined, None))

    return parts


# ============================================================
#  Main portal generation
# ============================================================

def generate_portal(
    folder_path: str,
    output_dir: str,
    max_chars_per_page: int = 8000,
    include_skipped: bool = True,
    show_progress: bool = True,
) -> dict:
    """
    将文件夹解析为可分页的知识门户。

    参数：
        folder_path: 要扫描的文件夹路径
        output_dir: 输出目录路径
        max_chars_per_page: 每个文档页面的最大字符数（默认8000）
        include_skipped: 是否在首页中包含不支持的文档标记
        show_progress: 是否在 CLI 中显示进度

    返回：
        dict: {
            "doc_count": 解析的文档数,
            "total_chars": 总字符数,
            "output_dir": 输出目录,
            "index_file": index.html 路径,
            "errors": 错误数,
        }
    """
    if not os.path.isdir(folder_path):
        raise ValueError("路径不是有效的文件夹：%s" % folder_path)

    # 输出目录冲突检查
    if os.path.exists(output_dir):
        existing_items = os.listdir(output_dir)
        non_hidden_items = [i for i in existing_items if not i.startswith('.')]
        if non_hidden_items:
            print("[注意] 输出目录已存在且非空：%s" % output_dir)
            print("       已有内容：%d 个项目" % len(non_hidden_items))
            print("       将覆盖其中同名文件，未改动文件会保留")
            print()

    # Create output directory structure
    docs_dir = os.path.join(output_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    # Scan and parse all files
    docs_meta = []
    total_chars = 0
    parsed_count = 0
    skipped_count = 0
    error_count = 0
    folder_name = os.path.basename(os.path.abspath(folder_path))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # First pass: collect all files to show progress
    all_files = []
    for dirpath, _, filenames in os.walk(folder_path):
        for fname in filenames:
            if fname.startswith('.'):
                continue
            full_path = os.path.join(dirpath, fname)
            if os.path.isfile(full_path):
                all_files.append(full_path)

    total_files = len(all_files)
    if show_progress:
        print("  [扫描] 发现 %d 个文件，开始解析..." % total_files)

    # Walk through folder
    for file_idx, full_path in enumerate(all_files):
        rel_path = os.path.relpath(full_path, folder_path)
        file_size = os.path.getsize(full_path)
        size_hr = human_readable_size(file_size)

        # 进度显示
        if show_progress:
            progress_pct = (file_idx + 1) / total_files * 100
            bar_len = 30
            filled = int(bar_len * (file_idx + 1) / total_files)
            bar = '#' * filled + '.' * (bar_len - filled)
            print("\r  [%s] %d/%d (%.0f%%) - %s" % (bar, file_idx + 1, total_files, progress_pct, rel_path[:50]), end='', flush=True)

        try:
            result = parse_file(full_path)
        except Exception as e:
            logger.exception("Error parsing %s: %s", rel_path, e)
            if show_progress:
                print("\n  [错误] %s - %s" % (rel_path, e))
            error_count += 1
            continue

        # Get file timestamps for metadata
        try:
            mtime = os.path.getmtime(full_path)
            ctime = os.path.getctime(full_path)
            mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            ctime_str = datetime.fromtimestamp(ctime).strftime("%Y-%m-%d %H:%M")
        except Exception:
            mtime_str = ""
            ctime_str = ""

        if result is None:
            if show_progress:
                print("\n  [跳过] %s (不支持的格式)" % rel_path)

            if include_skipped:
                # Generate a placeholder HTML page for skipped files
                skipped_safe_name = make_safe_filename(full_path, folder_path)
                # Use "skipped_" prefix to differentiate from parsed files
                skipped_file_name = "skipped_" + skipped_safe_name
                skipped_path = os.path.join(docs_dir, skipped_file_name)

                skipped_html = wrap_skipped_html(
                    title=rel_path,
                    folder_name=folder_name,
                    file_size_hr=size_hr,
                    filepath=full_path,
                    index_link="../index.html",
                    mtime=mtime_str,
                    ctime=ctime_str,
                )

                with open(skipped_path, 'w', encoding='utf-8') as f:
                    f.write(skipped_html)

                docs_meta.append({
                    "title": rel_path,
                    "file": "docs/%s" % skipped_file_name,
                    "size": 0,
                    "size_hr": size_hr,
                    "preview": "⏭️ 该文件类型不支持解析，已自动跳过",
                    "tags": ["已跳过"],
                    "skipped": True,
                    "mtime": mtime_str,
                    "ctime": ctime_str,
                })
            else:
                # Only show marker on card, no detail page
                docs_meta.append({
                    "title": rel_path,
                    "file": None,
                    "size": 0,
                    "size_hr": size_hr,
                    "preview": "[不支持的格式，已跳过]",
                    "tags": ["已跳过"],
                    "skipped": True,
                    "mtime": mtime_str,
                    "ctime": ctime_str,
                })
            skipped_count += 1
            continue

        text = (result.get("text") or "").strip()
        if not text:
            skipped_count += 1
            continue

        # Handle large documents by splitting
        text_parts = split_large_text(text, max_chars_per_page)

        # Generate safe base filename
        safe_base = make_safe_filename(full_path, folder_path)
        base_name, base_ext = os.path.splitext(safe_base)

        # Pre-compute all filenames for this document
        part_filenames = []
        for part_idx in range(len(text_parts)):
            if part_idx == 0:
                fname = safe_base
            else:
                fname = "%s_part%d%s" % (base_name, part_idx + 1, base_ext)
            part_filenames.append(fname)

        # Generate each part with pagination navigation
        for part_idx, (part_text, part_title) in enumerate(text_parts):
            char_count = len(part_text)
            total_chars += char_count

            safe_name = part_filenames[part_idx]

            # Build doc title
            doc_title = rel_path
            if part_title:
                doc_title = "%s - %s" % (rel_path, part_title)

            # Compute pagination links
            total_parts = len(text_parts)
            prev_page = None
            next_page = None
            page_info = None

            if total_parts > 1:
                page_info = "第 %d 页，共 %d 页" % (part_idx + 1, total_parts)
                if part_idx > 0:
                    prev_page = "docs/%s" % part_filenames[part_idx - 1]
                if part_idx < total_parts - 1:
                    next_page = "docs/%s" % part_filenames[part_idx + 1]

            # Generate individual HTML page
            page_html = wrap_doc_html(
                title=doc_title,
                text=part_text,
                folder_name=folder_name,
                char_count=char_count,
                file_size_hr=size_hr,
                index_link="../index.html",
                mtime=mtime_str,
                ctime=ctime_str,
                prev_page=prev_page,
                next_page=next_page,
                page_info=page_info,
            )

            # Write to file
            doc_file_path = os.path.join(docs_dir, safe_name)
            with open(doc_file_path, 'w', encoding='utf-8') as f:
                f.write(page_html)

            # Extract keywords from content
            keywords = extract_keywords(part_text)

            # Preview (first 200 chars)
            preview = part_text[:200].replace('\n', ' ').strip()

            # Build display title with page suffix if multi-page
            display_title = doc_title
            if total_parts > 1 and part_idx == 0:
                display_title = "%s (第1页，共%d页)" % (rel_path, total_parts)
            elif total_parts > 1:
                display_title = "%s (第%d页)" % (rel_path, part_idx + 1)

            # Add to metadata (only first part for index, or each part if multi-page)
            docs_meta.append({
                "title": display_title,
                "file": "docs/%s" % safe_name,
                "size": char_count,
                "size_hr": size_hr,
                "preview": preview,
                "tags": keywords[:5],  # Limit to 5 tags per doc
                "skipped": False,
                "mtime": mtime_str,
                "ctime": ctime_str,
            })
            parsed_count += 1

        if len(text_parts) > 1:
            if show_progress:
                print("\n  [拆分] %s -> 拆分为 %d 页（带导航链接）" % (rel_path, len(text_parts)))

    # Newline after progress bar
    if show_progress:
        print()

    # 文档排序：按文件名（相对路径）排序
    docs_meta.sort(key=lambda d: d.get("title", "").lower())

    # Generate index.html
    if docs_meta:
        index_html = wrap_index_html(
            docs_meta=docs_meta,
            folder_name=folder_name,
            folder_path=os.path.abspath(folder_path),
            total_chars=total_chars,
            generated_at=now,
        )

        index_path = os.path.join(output_dir, "index.html")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_html)

        logger.info("Portal index: %s", index_path)
    else:
        index_path = None
        logger.warning("No documents were parsed!")

    return {
        "doc_count": parsed_count,
        "total_chars": total_chars,
        "skipped": skipped_count,
        "errors": error_count,
        "output_dir": output_dir,
        "index_file": index_path,
        "folder_name": folder_name,
    }
