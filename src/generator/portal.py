"""
FolderKnowledgeSiteGeneratorForAI Portal — Single-page knowledge portal generator

Parses a folder into a single searchable HTML page with:
- File tree (collapsible folder structure)
- Document cards (with search, tag cloud)
- All file contents as collapsible <details> blocks (default collapsed)
- "Expand All (AI Mode)" button for AI to read all code at once
- Per-file expand/collapse for human readers

Design decisions:
- Single HTML file, no pagination (AI lacks cross-page reasoning)
- All file contents embedded in DOM (AI can read them when expanded)
- Default collapsed for fast loading
"""

import os
import re
import logging
from datetime import datetime
from collections import Counter

from src.parser.dispatcher import parse_file
from src.generator.templates import (
    wrap_index_html,
    build_file_content_blocks,
    _get_file_type,
)

logger = logging.getLogger(__name__)

# Max characters per file before truncation.
# Prevents a single huge file (e.g. 2MB SQL dump) from bloating the page and
# exceeding AI context windows.
MAX_CHARS_PER_FILE = 50_000


# ============================================================
#  Utility functions
# ============================================================

def human_readable_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    if size_bytes == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def make_safe_filename(rel_path: str, base_dir: str) -> str:
    """Sanitize a relative file path into a safe HTML filename."""
    # Normalize separators
    rel = rel_path.replace('\\', '/').strip('/')
    # Remove drive letters (e.g., C:)
    rel = re.sub(r'^[A-Za-z]:', '', rel)
    # Replace unsafe filename characters with underscores
    safe = re.sub(r'[<>:"/\\|?*]', '_', rel)
    # Collapse multiple underscores
    safe = re.sub(r'_+', '_', safe)
    # Remove leading/trailing underscores and dots
    safe = safe.strip('_. ')
    if not safe:
        safe = 'untitled'
    # Ensure .html extension
    if not safe.endswith('.html'):
        safe += '.html'
    return safe


def split_large_text(text: str, max_chars: int = 8000) -> list:
    """Split large text into multiple parts, preferring splits at headings/paragraphs.
    
    Returns list of (chunk_text, heading_or_None) tuples.
    """
    if len(text) <= max_chars:
        return [(text, None)]
    
    parts = []
    # Try to split at markdown headings first
    lines = text.split('\n')
    current_chunk = []
    current_size = 0
    current_heading = None
    
    for line in lines:
        line_len = len(line) + 1  # +1 for newline
        
        # Check if this is a heading
        heading_match = re.match(r'^(#{1,6}\s+.*)$', line)
        
        if current_size + line_len > max_chars and current_chunk:
            # Flush current chunk
            parts.append(('\n'.join(current_chunk), current_heading))
            current_chunk = []
            current_size = 0
            current_heading = None
        
        # If this is a heading, set it as the heading for the next chunk
        if heading_match:
            current_heading = heading_match.group(1)
        
        current_chunk.append(line)
        current_size += line_len
    
    # Flush remaining
    if current_chunk:
        parts.append(('\n'.join(current_chunk), current_heading))
    
    # Edge case: if a single line exceeds max_chars, force split
    if not parts:
        # Force split at max_chars
        for i in range(0, len(text), max_chars):
            chunk = text[i:i + max_chars]
            parts.append((chunk, None))
    
    return parts


def extract_keywords(text: str, max_words: int = 8) -> list:
    """Extract keywords from text using frequency + stop word filtering."""
    chinese_chars = re.findall(r'[\u4e00-\u9fff]{2,6}', text)
    english_words = re.findall(r'\b[a-zA-Z]{3,15}\b', text.lower())

    stop_words = {
        'the', 'and', 'for', 'that', 'this', 'with', 'from', 'have', 'are', 'was', 'were',
        'been', 'being', 'has', 'had', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'about', 'into', 'over', 'after', 'before', 'between', 'under',
        'above', 'such', 'only', 'other', 'than', 'then', 'also', 'very', 'just', 'more',
        'some', 'these', 'those', 'html', 'class', 'span', 'div', 'style', 'width',
        'height', 'which', 'what', 'when', 'where', 'there', 'their', 'they', 'them',
        'like', 'here', 'each', 'both', 'most', 'many', 'much', 'must', 'your', 'its',
        'can', 'see', 'way', 'use', 'make', 'new', 'one', 'two', 'how', 'all', 'any',
        'not', 'but', 'who', 'out', 'down', 'now', 'even', 'back', 'still', 'well', 'too',
        'own', 'while', 'because', 'ever', 'every', 'same', 'through', 'thing', 'things',
        'number', 'part', 'place', 'long', 'time', 'work', 'year', 'used', 'using',
        'based', 'also', 'called', 'without', 'within', 'across', 'along', 'among',
        'around', 'first', 'second', 'last', 'next', 'data', 'text', 'file', 'files',
        'code', 'type', 'string', 'value', 'name', 'key', 'page', 'list', 'line', 'lines',
        'word', 'words', 'char', 'chars', 'info', 'information', 'description', 'default',
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上',
        '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己',
        '这', '他', '她', '它', '们', '来', '与', '及', '或', '以', '而', '但', '又', '被',
        '让', '对', '从', '把', '向', '为', '比', '等', '能', '可', '所', '如', '之', '其',
        '中', '将', '还', '做', '做', '给', '用', '更', '最', '并', '过', '开', '只', '有',
        '学', '年', '月', '日', '时', '间', '后', '前', '下', '此', '因', '如', '何', '道',
        '种', '些', '几', '那', '哪', '两', '多', '少', '个', '每', '既', '除了', '虽然',
        '因为', '所以', '但是', '如果', '可以', '应该', '需要', '已经', '没有', '这些',
        '那些', '关于', '由于', '而且', '或者', '不是', '就是', '而是', '还是', '并且',
        '从而', '因此', '其中', '之一', '之间', '方面', '部分', '同时', '之后', '之前',
        '今天', '明天', '昨天', '现在', '然后', '比如', '比较', '非常', '一定', '可能',
        '全部', '最后', '开始', '继续', '以及', '不过', '只是', '为了', '那里', '这里',
        '怎么', '什么', '如果', '否则', '另外', '帮助', '关于', '使用', '提供', '通过',
        '进行', '包括', '还有', '以及', '其他', '其中', '由于', '因此', '所有', '功能',
        '支持', '方法', '方式', '配置', '设置', '参数',
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


# ============================================================
#  Filter rules: files to exclude from portal
# ============================================================

_FILTER_EXTS = frozenset({
    '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib',
    '.obj', '.o', '.a', '.lib', '.exe', '.msi',
    '.class', '.jar', '.war',
    '.min.js', '.min.css', '.min.css.map', '.min.js.map',
    '.log', '.lock', '.tmp', '.swp', '.swo', '.bak', '.old',
    '.svg',
    '.DS_Store', '.directory', '.lst',
})
_FILTER_DIRS = frozenset({
    '.git', '.svn', '.hg', '__pycache__', '.mypy_cache',
    '.pytest_cache', '.venv', 'venv', 'env', 'node_modules',
    'bower_components', '.idea', '.vscode', '.vs',
    '.sass-cache', '.tox', '.eggs', 'eggs',
    '.ruff_cache', '.mypy_cache',
})
_FILTER_FILES = frozenset({
    '.gitignore', '.gitattributes', '.gitmodules',
    '.gitkeep', '.gitlab-ci.yml', '.travis.yml',
    'LICENSE', 'COPYING', 'AUTHORS',
    'thumbs.db', 'desktop.ini',
})


def _should_filter_file(rel_path: str) -> bool:
    """Return True if a file should be excluded from the portal."""
    parts = rel_path.replace('\\', '/').split('/')
    for part in parts[:-1]:
        if part in _FILTER_DIRS or part.startswith('.'):
            return True
    fname = parts[-1]
    if fname.startswith('.'):
        return True
    if fname in _FILTER_FILES:
        return True
    for ext in _FILTER_EXTS:
        if fname.endswith(ext):
            return True
    return False


def _is_readme_file(rel_path: str) -> bool:
    """Return True if the file is a README."""
    fname = os.path.basename(rel_path).lower()
    return fname in (
        'readme.md', 'readme.txt', 'readme', 'readme.rst', 'readme.markdown',
        'readme.org', 'readme.adoc', 'readme.asciidoc',
    )


# ============================================================
#  HTMl escaping
# ============================================================

def escape_html(s: str) -> str:
    """Minimal HTML escape for safe attribute insertion."""
    from html import escape as _he
    return _he(s)


# ============================================================
#  File tree builder
# ============================================================

def build_file_tree_html(folder_path: str) -> str:
    """Build an ASCII-tree diagram of the folder structure."""
    lines = []
    _walk_and_render(folder_path, folder_path, lines, prefix="")
    return '\n'.join(lines)


def _walk_and_render(root: str, dirpath: str, lines: list, prefix: str):
    """Recursively walk directory and append tree lines."""
    items = []
    try:
        names = sorted(os.listdir(dirpath), key=str.lower)
    except PermissionError:
        return

    for name in names:
        full_path = os.path.join(dirpath, name)
        rel_path = os.path.relpath(full_path, root)

        if os.path.isdir(full_path):
            if name in _FILTER_DIRS or name.startswith('.'):
                continue
            items.append(('dir', name, full_path, rel_path))
        else:
            if _should_filter_file(rel_path):
                continue
            items.append(('file', name, full_path, rel_path))

    dirs = [(n, f, r) for t, n, f, r in items if t == 'dir']
    files = [(n, f, r) for t, n, f, r in items if t == 'file']
    all_items = dirs + files

    for idx, (name, full_path, rel_path) in enumerate(all_items):
        is_last = (idx == len(all_items) - 1)
        connector = '└──' if is_last else '├──'
        child_prefix = prefix + ('    ' if is_last else '│   ')

        if os.path.isdir(full_path):
            lines.append(
                f'<li class="tree-folder">'
                f'<span class="tree-prefix">{prefix}{connector}</span>'
                f'<span class="tree-folder-name">📁 {name}</span>'
                f'</li>'
            )
            _walk_and_render(root, full_path, lines, child_prefix)
        else:
            size = os.path.getsize(full_path)
            size_hr = human_readable_size(size)
            is_readme = _is_readme_file(rel_path)

            css_class = 'tree-file'
            if is_readme:
                css_class += ' tree-readme'

            safe_filename = escape_html(rel_path.replace('\\', '/'))
            link_html = f'<a onclick="jumpToFile(\'{safe_filename}\')">📄 {name}</a>'

            lines.append(
                f'<li class="{css_class}">'
                f'<span class="tree-prefix">{prefix}{connector}</span>'
                f'{link_html}'
                f'<span class="tree-size"> {size_hr}</span>'
                f'</li>'
            )


# ============================================================
#  Main portal generation
# ============================================================

def generate_portal(
    folder_path: str,
    output_dir: str,
    include_skipped: bool = True,
    show_progress: bool = True,
    language: str = "en",
) -> dict:
    """Generate single-page knowledge portal with all file contents."""
    if not os.path.isdir(folder_path):
        raise ValueError("Not a valid folder: %s" % folder_path)

    os.makedirs(output_dir, exist_ok=True)

    all_files = []
    for dirpath, dirnames, filenames in os.walk(folder_path):
        dirnames[:] = [
            d for d in dirnames
            if d not in _FILTER_DIRS and not d.startswith('.')
        ]
        for fname in filenames:
            full_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(full_path, folder_path)
            if _should_filter_file(rel_path):
                continue
            if os.path.isfile(full_path):
                all_files.append((full_path, rel_path))

    total_files = len(all_files)
    folder_name = os.path.basename(os.path.abspath(folder_path))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    docs_meta = []
    docs_texts = []
    total_chars = 0
    parsed_count = 0
    skipped_count = 0
    error_count = 0
    skip_by_reason: dict[str, int] = {}

    if show_progress:
        print("  [Scan] Found %d files, parsing..." % total_files)

    for file_idx, (full_path, rel_path) in enumerate(all_files):
        file_size = os.path.getsize(full_path)
        size_hr = human_readable_size(file_size)

        if show_progress:
            pct = (file_idx + 1) / total_files * 100
            bar_len = 30
            filled = int(bar_len * (file_idx + 1) / total_files)
            bar = '#' * filled + '.' * (bar_len - filled)
            print("\r  [%s] %d/%d (%.0f%%) - %s" % (
                bar, file_idx + 1, total_files, pct, rel_path[:60]),
                end='', flush=True)

        try:
            result = parse_file(full_path)
        except Exception as e:
            logger.exception("Error parsing %s: %s", rel_path, e)
            if show_progress:
                print("\n  [Error] %s - %s" % (rel_path, e))
            error_count += 1
            continue

        try:
            mtime = os.path.getmtime(full_path)
            mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        except Exception:
            mtime_str = ""

        if result is None:
            skipped_count += 1
            skip_by_reason['parser returned no content'] = skip_by_reason.get('parser returned no content', 0) + 1
            continue

        text = (result.get("text") or "").strip()
        if not text:
            skipped_count += 1
            skip_by_reason['empty content after parsing'] = skip_by_reason.get('empty content after parsing', 0) + 1
            continue

        char_count = len(text)
        # Truncate extremely large files to prevent page bloat
        # Use line-based truncation to preserve code structure
        if MAX_CHARS_PER_FILE and char_count > MAX_CHARS_PER_FILE:
            # Find the last line boundary before MAX_CHARS_PER_FILE
            truncated = text[:MAX_CHARS_PER_FILE]
            last_newline = truncated.rfind('\n')
            if last_newline > MAX_CHARS_PER_FILE * 0.5:  # Only use line boundary if reasonable
                text = truncated[:last_newline]
            else:
                text = truncated
            text += (
                f"\n\n... [截断：原文 {char_count:,} 字符，仅展示前 {MAX_CHARS_PER_FILE:,} 字符] ...\n"
                f"... [Truncated: original {char_count:,} chars, showing first {MAX_CHARS_PER_FILE:,} chars] ..."
            )
            char_count = len(text)

        total_chars += char_count

        keywords = extract_keywords(text)
        preview = text[:200].replace('\n', ' ').strip()

        docs_meta.append({
            "title": rel_path,
            "file": rel_path,
            "size": char_count,
            "size_hr": size_hr,
            "preview": preview,
            "tags": keywords[:5],
            "skipped": False,
            "mtime": mtime_str,
        })
        docs_texts.append({
            "title": rel_path,
            "text": text,
            "size": char_count,
            "file_type": _get_file_type(rel_path),
            "size_hr": size_hr,
            "tags": keywords[:5],
        })
        parsed_count += 1

    if show_progress:
        print()

    docs_meta.sort(key=lambda d: d.get("title", "").lower())
    docs_texts.sort(key=lambda d: d.get("title", "").lower())

    # Print skip reasons to console
    if skip_by_reason:
        print(f"  [Skip Summary] {skipped_count} files skipped:")
        for reason, count in sorted(skip_by_reason.items(), key=lambda x: -x[1]):
            print(f"    - {count} file(s): {reason}")
    if error_count:
        print(f"  [Error Summary] {error_count} file(s) failed to parse")

    file_tree_html = build_file_tree_html(folder_path) if include_skipped else ""
    file_contents_html = build_file_content_blocks(docs_texts)

    if docs_meta or file_tree_html:
        index_html = wrap_index_html(
            docs_meta=docs_meta,
            folder_name=folder_name,
            folder_path=os.path.abspath(folder_path),
            total_chars=total_chars,
            generated_at=now,
            file_tree_html=file_tree_html,
            file_contents_html=file_contents_html,
            language=language,
        )
        index_path = os.path.join(output_dir, "index.html")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_html)
        logger.info("Portal index: %s", index_path)
    else:
        index_path = None
        logger.warning("No documents parsed!")

    return {
        "doc_count": parsed_count,
        "total_chars": total_chars,
        "skipped": skipped_count,
        "errors": error_count,
        "output_dir": output_dir,
        "index_file": index_path,
        "folder_name": folder_name,
    }