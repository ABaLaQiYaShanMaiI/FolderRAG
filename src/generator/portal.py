"""
FolderRAG Portal — 智能分页知识门户生成器

将文件夹中的文档解析为「可搜索的知识门户」：
- 每个文档生成一个独立 HTML 页面（控制在 ~8000 字符以内）
- index.html 作为总入口，带搜索框、关键词云、文档卡片
- 适合在 Edge Copilot 中打开，让 AI 完整读取每个页面
"""

import os
import re
import logging
from datetime import datetime
from collections import Counter

from src.parser.dispatcher import parse_file
from src.generator.templates import wrap_doc_html, wrap_index_html

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
    safe = re.sub(r'[<>:"/\\|?*]', '_', name)
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
    使用简单的频率统计 + 长度过滤。
    """
    # Chinese + English word pattern
    chinese_chars = re.findall(r'[\u4e00-\u9fff]{2,6}', text)
    english_words = re.findall(r'\b[a-zA-Z]{3,15}\b', text.lower())

    # Filter common stop words
    stop_words = {
        'the', 'and', 'for', 'that', 'this', 'with', 'from', 'have',
        'are', 'was', 'were', 'been', 'being', 'has', 'had', 'does',
        'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'about', 'into', 'over', 'after', 'before', 'between',
        'under', 'above', 'such', 'only', 'other', 'than', 'then',
        'also', 'very', 'just', 'more', 'some', 'these', 'those',
        'html', 'class', 'span', 'div', 'style', 'width', 'height',
    }

    # Count frequency
    counter = Counter()

    for word in chinese_chars:
        counter[word] += 1

    for word in english_words:
        if word not in stop_words and not word.isdigit():
            counter[word] += 1

    # Return most common words
    keywords = [word for word, _ in counter.most_common(max_words)]
    return keywords


def split_large_text(text: str, max_chars: int = 8000) -> list:
    """
    将大文本拆分为多个片段，每个片段不超过 max_chars 字符。
    返回 [(part1, part1_title), (part2, part2_title), ...]
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
            title_suffix = f"（第{part_num}部分）" if part_num > 1 else ""
            # Try to find section title nearby
            subtitle = f" — {section_titles[part_num-1]}" if part_num <= len(section_titles) else ""
            parts.append((combined, f"Part {part_num}{subtitle}{title_suffix}" if part_num > 1 else None))
            current_part = [para]
            current_len = para_len
            part_num += 1
        else:
            current_part.append(para)
            current_len += para_len

    # Last part
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
) -> dict:
    """
    将文件夹解析为可分页的知识门户。

    参数：
        folder_path: 要扫描的文件夹路径
        output_dir: 输出目录路径
        max_chars_per_page: 每个文档页面的最大字符数（默认8000）
        include_skipped: 是否在首页中包含不支持的文档标记

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
        raise ValueError(f"路径不是有效的文件夹：{folder_path}")

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

    # Walk through folder
    for dirpath, _, filenames in os.walk(folder_path):
        for fname in filenames:
            if fname.startswith('.'):
                continue
            full_path = os.path.join(dirpath, fname)
            if not os.path.isfile(full_path):
                continue

            rel_path = os.path.relpath(full_path, folder_path)
            file_size = os.path.getsize(full_path)
            size_hr = human_readable_size(file_size)

            logger.info("Parsing: %s", rel_path)

            try:
                result = parse_file(full_path)
            except Exception as e:
                logger.exception("Error parsing %s: %s", rel_path, e)
                error_count += 1
                continue

            if result is None:
                logger.info("  -> Skipped (unsupported type)")
                if include_skipped:
                    # Still add a placeholder entry
                    docs_meta.append({
                        "title": rel_path,
                        "file": None,
                        "size": 0,
                        "size_hr": size_hr,
                        "preview": "[不支持的格式，已跳过]",
                        "tags": ["⏭️ 跳过"],
                        "skipped": True,
                    })
                skipped_count += 1
                continue

            text = (result.get("text") or "").strip()
            if not text:
                logger.info("  -> Skipped (empty content)")
                skipped_count += 1
                continue

            # Handle large documents by splitting
            text_parts = split_large_text(text, max_chars_per_page)

            for part_idx, (part_text, part_title) in enumerate(text_parts):
                char_count = len(part_text)
                total_chars += char_count

                # Build safe filename
                safe_name = make_safe_filename(full_path, folder_path)
                if part_idx > 0:
                    # Append part number to filename
                    base, ext = os.path.splitext(safe_name)
                    safe_name = f"{base}_part{part_idx + 1}{ext}"

                doc_title = rel_path
                if part_title:
                    doc_title = f"{rel_path} — {part_title}"

                # Generate individual HTML page
                page_html = wrap_doc_html(
                    title=doc_title,
                    text=part_text,
                    folder_name=folder_name,
                    char_count=char_count,
                    file_size_hr=size_hr,
                    index_link="../index.html",
                )

                # Write to file
                doc_file_path = os.path.join(docs_dir, safe_name)
                with open(doc_file_path, 'w', encoding='utf-8') as f:
                    f.write(page_html)

                # Extract keywords from content
                keywords = extract_keywords(part_text)

                # Preview (first 200 chars)
                preview = part_text[:200].replace('\n', ' ').strip()

                # Add to metadata
                docs_meta.append({
                    "title": doc_title,
                    "file": f"docs/{safe_name}",
                    "size": char_count,
                    "size_hr": size_hr,
                    "preview": preview,
                    "tags": keywords[:5],  # Limit to 5 tags per doc
                    "skipped": False,
                })
                parsed_count += 1

            if len(text_parts) > 1:
                logger.info("  -> Split into %d pages (~%d chars each)",
                           len(text_parts), max_chars_per_page)

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
