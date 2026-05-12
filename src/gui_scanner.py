"""
FolderKnowledgeSiteGeneratorForAI — GUI Scanning & HTML Building Logic
Extracted from gui.py for better separation of concerns.
Provides folder scanning, file info collection, and single-HTML generation.
"""

import os
import sys
import pathlib
import logging
from html import escape
from datetime import datetime

from src.utils import human_readable_size

# Add project root to path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

try:
    from src.parser.dispatcher import parse_file
    HAS_PARSER = True
except ImportError:
    HAS_PARSER = False

logger = logging.getLogger(__name__)

# Module-level cache for MIME checker
_mime_checker_cache = None


def _label(zh: str, en: str) -> str:
    """Return English label for HTML output (defaults to en)."""
    return en


# ── Import shared filter rules from constants ──
try:
    from src.constants import SUPPORTED_TEXT_EXTS, should_filter_dir, should_filter_file
    FALLBACK_EXTS = SUPPORTED_TEXT_EXTS
except ImportError:
    # Minimal fallback when constants module is unavailable
    FALLBACK_EXTS = {
        '.txt', '.md', '.html', '.htm', '.json', '.xml', '.csv',
        '.yaml', '.yml', '.toml', '.ini', '.log', '.cfg', '.conf',
        '.py', '.pyw', '.js', '.jsx', '.ts', '.tsx', '.css', '.scss', '.less',
        '.sh', '.bash', '.zsh', '.fish', '.bat', '.cmd', '.ps1', '.psm1', '.psd1',
        '.rb', '.java', '.c', '.cpp', '.h', '.hpp', '.cc', '.cxx', '.hh', '.hxx',
        '.rs', '.go', '.php', '.swift', '.kt', '.kts', '.scala',
        '.cs', '.fs', '.vb', '.dart', '.lua', '.r', '.R', '.m', '.mm',
        '.hs', '.erl', '.hrl', '.ex', '.exs', '.elm', '.clj', '.cljs',
        '.sql', '.ddl', '.dml', '.pl', '.pm', '.tcl',
        '.markdown', '.rst', '.text', '.tsv',
        '.pdf',
        '.docx', '.pptx', '.xlsx',
        '.prototxt', '.pbtxt', '.solver', '.trainval', '.test',
        '.cfg',
        '.csproj', '.fsproj', '.vbproj',
        '.sln', '.user', '.vsconfig',
        '.xaml', '.axaml',
    }

    def should_filter_dir(dirname: str) -> bool:
        """Fallback: skip dot-prefixed directories."""
        return dirname.startswith('.')

    def should_filter_file(rel_path: str) -> bool:
        """Fallback: skip dot-prefixed files."""
        return os.path.basename(rel_path).startswith('.')


def _get_mime_checker():
    """
    Initialize MIME type checker with fallback extensions (cached).
    Returns (checker, prefixes, exact_set, fallback_exts) tuple.
    """
    global _mime_checker_cache
    if _mime_checker_cache is not None:
        return _mime_checker_cache

    try:
        import magic
        checker = magic.Magic(mime=True)
        prefixes = ('text/',)
        exact = {
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/msword',
            'application/vnd.ms-powerpoint',
            'application/vnd.ms-excel',
        }
        _mime_checker_cache = (checker, prefixes, exact, FALLBACK_EXTS)
        return _mime_checker_cache
    except Exception:
        _mime_checker_cache = (None, (), set(), FALLBACK_EXTS)
        return _mime_checker_cache


def is_file_supported(full_path: str, ext: str) -> bool:
    """
    Check if a file is supported using MIME type (with extension fallback).
    """
    checker, prefixes, exact, fallback_exts = _get_mime_checker()
    if checker is not None:
        try:
            mime = checker.from_file(full_path)
            if mime.startswith(prefixes) or mime in exact:
                return True
        except Exception:
            pass
    return ext in fallback_exts


def collect_files_info(root_dir: str) -> tuple:
    """
    Scan folder and return (file_list, total_size).
    Each file info dict contains: path, rel_path, size, size_hr, ext, supported.

    Applies the same filter rules as portal mode:
    - Skips hidden/cache dirs (FILTER_DIRS, dot-prefixed dirs)
    - Skips hidden/cache files (FILTER_FILES, FILTER_EXTS, dot-prefixed files)
    """
    file_list = []
    total_size = 0

    try:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Filter directories in-place to avoid descending into cache/hidden dirs
            dirnames[:] = [d for d in dirnames if not should_filter_dir(d)]

            for fname in filenames:
                full_path = os.path.join(dirpath, fname)
                if not os.path.isfile(full_path):
                    continue
                rel_path = os.path.relpath(full_path, root_dir)
                # Apply file-level filter (same rules as portal._should_filter_file)
                if should_filter_file(rel_path):
                    continue
                file_size = os.path.getsize(full_path)
                ext = os.path.splitext(fname)[1].lower()
                supported = is_file_supported(full_path, ext)

                file_list.append({
                    'path': full_path,
                    'rel_path': rel_path,
                    'size': file_size,
                    'size_hr': human_readable_size(file_size),
                    'ext': ext,
                    'supported': supported,
                })
                total_size += file_size
    except Exception as e:
        logger.error(f"Error scanning folder: {e}")

    return file_list, total_size


def build_html_from_files(
    folder_path: str,
    file_list: list,
    output_path: str,
    max_chars: int = None,
    include_skipped: bool = True,
    language: str = "en",
) -> tuple:
    """
    Parse files and generate HTML content.
    Returns (html_string, parsed_count, skipped_count, error_count, total_chars).
    """
    articles = []
    total_chars = 0
    hit_limit = False
    parsed_count = 0
    skipped_count = 0
    error_count = 0
    # Track skip reasons for console output
    skip_by_reason: dict[str, int] = {}

    for finfo in file_list:
        if hit_limit:
            break

        if not finfo['supported']:
            if include_skipped:
                escaped_path = escape(finfo['rel_path'])
                escaped_size = escape(finfo['size_hr'])
                article = (
                    f"  <article class=\"skipped\">\n"
                    f"    <h2>⏭️ {escaped_path}</h2>\n"
                    f"    <p class=\"meta\">{_label('类型不支持', 'Unsupported')} | {_label('大小', 'Size')}: {escaped_size}</p>\n"
                    f"  </article>"
                )
                articles.append(article)
            skipped_count += 1
            skip_by_reason['unsupported format'] = skip_by_reason.get('unsupported format', 0) + 1
            continue

        try:
            if not HAS_PARSER:
                with open(finfo['path'], 'r', encoding='utf-8', errors='replace') as f:
                    text = f.read()
            else:
                result = parse_file(finfo['path'])
                if result is None:
                    skipped_count += 1
                    skip_by_reason['parser returned no content'] = skip_by_reason.get('parser returned no content', 0) + 1
                    continue
                text = (result.get("text") or "").strip()

            if not text:
                skipped_count += 1
                skip_by_reason['empty content after parsing'] = skip_by_reason.get('empty content after parsing', 0) + 1
                continue

            file_chars = len(text)
            if max_chars is not None and total_chars + file_chars > max_chars:
                allowed = max_chars - total_chars
                if allowed <= 0:
                    articles.append(
                        f"  <!-- {_label('已达到 --max-chars 限制（', 'Reached --max-chars limit (')}{max_chars}{_label(' 字符），后续文件已截断', ' chars), remaining files truncated')} -->"
                    )
                    break
                text = text[:allowed]
                hit_limit = True

            escaped_text = escape(text)
            escaped_path = escape(finfo['rel_path'])
            escaped_size = escape(finfo['size_hr'])
            article = (
                f"  <article>\n"
                f"    <h2>📄 {escaped_path}</h2>\n"
                f"    <p class=\"meta\">{_label('大小', 'Size')}: {escaped_size} | {_label('内容', 'Content')}: {file_chars} {_label('字符', 'chars')}</p>\n"
                f"    <p>{escaped_text}</p>\n"
                f"  </article>"
            )
            articles.append(article)
            total_chars += len(text)
            parsed_count += 1

        except Exception:
            error_count += 1
            continue

        if hit_limit:
            articles.append(
                f"  <!-- {_label('已达到 --max-chars 限制（', 'Reached --max-chars limit (')}{max_chars}{_label(' 字符），后续文件已截断', ' chars), remaining files truncated')} -->"
            )
            break

    # Print skip reasons to console
    if skip_by_reason:
        print(f"[Skip Summary] {skipped_count} files skipped:")
        for reason, count in sorted(skip_by_reason.items(), key=lambda x: -x[1]):
            print(f"  - {count} file(s): {reason}")
    if error_count:
        print(f"[Error Summary] {error_count} file(s) failed to parse")

    articles_html = "\n".join(articles)
    file_count = parsed_count
    folder_name = escape(os.path.basename(os.path.abspath(folder_path)))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Use language parameter to determine HTML lang attribute
    html_lang = "en" if language != "zh" else "zh-CN"

    html = (
        "<!DOCTYPE html>\n"
        f'<html lang="{html_lang}">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        f"<title>{_label('知识导出', 'Knowledge Export')} - {folder_name}</title>\n"
        "<style>\n"
        "  * { margin: 0; padding: 0; box-sizing: border-box; }\n"
        "  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; "
        "max-width: 960px; margin: 0 auto; padding: 20px; background: #f8f9fa; color: #333; }\n"
        "  .header { background: #fff; border-radius: 12px; padding: 24px; margin-bottom: 20px; "
        "box-shadow: 0 2px 8px rgba(0,0,0,0.08); }\n"
        "  .header h1 { font-size: 1.5em; color: #1a73e8; margin-bottom: 8px; }\n"
        "  .header .meta { color: #666; font-size: 0.9em; line-height: 1.8; }\n"
        "  .header .meta span { display: inline-block; margin-right: 16px; }\n"
        "  article { background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; "
        "padding: 16px; margin-bottom: 12px; transition: box-shadow 0.2s; }\n"
        "  article:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.1); }\n"
        "  article.skipped { opacity: 0.6; background: #f5f5f5; }\n"
        "  h2 { font-size: 1em; color: #1a73e8; margin-bottom: 6px; word-break: break-all; }\n"
        "  .meta { color: #888; font-size: 0.82em; margin-bottom: 8px; }\n"
        "  p { white-space: pre-wrap; word-break: break-word; font-size: 0.93em; line-height: 1.7; }\n"
        "  hr { border: none; border-top: 1px solid #e0e0e0; margin: 16px 0; }\n"
        "  .footer { text-align: center; color: #999; font-size: 0.85em; padding: 20px; }\n"
        "</style>\n"
        "</head>\n"
        "<body>\n"
        "  <div class=\"header\">\n"
        f"    <h1>📁 {folder_name}</h1>\n"
        "    <div class=\"meta\">\n"
        f"      <span>📄 {_label('文件数', 'Files')}: {file_count}</span>\n"
        f"      <span>📝 {_label('总字符', 'Total chars')}: {total_chars:,}</span>\n"
        f"      <span>🕐 {_label('导出时间', 'Exported')}: {now}</span>\n"
        f"      <span>📂 {_label('来源', 'Source')}: {escape(os.path.abspath(folder_path))}</span>\n"
        "    </div>\n"
        "  </div>\n"
        f"{articles_html}\n"
        "  <div class=\"footer\">\n"
        f"    <p>{_label('由 FolderKnowledgeSiteGeneratorForAI Desktop 生成', 'Generated by FolderKnowledgeSiteGeneratorForAI Desktop')} | {_label('共', 'Total')} {file_count} {_label('个文件', 'files')}, {total_chars:,} {_label('字符', 'chars')}"
        f" | {now}</p>\n"
        "  </div>\n"
        "</body>\n"
        "</html>"
    )
    return html, parsed_count, skipped_count, error_count, total_chars


def build_text_from_files(
    folder_path: str,
    file_list: list,
    max_chars: int = None,
    include_skipped: bool = False,
) -> tuple:
    """Generate plain text output, each file wrapped with metadata separator + content.

    Returns (text, parsed_count, skipped_count, error_count, total_chars).
    """
    parts = []
    total_chars = 0
    parsed_count = 0
    skipped_count = 0
    error_count = 0
    hit_limit = False
    separator = "=" * 60  # separator between files

    for file_idx, finfo in enumerate(file_list):
        if hit_limit:
            break

        if not finfo['supported']:
            skipped_count += 1
            if include_skipped:
                parts.append(
                    f"{separator}\n"
                    f"[SKIPPED] {finfo['rel_path']} "
                    f"(Size: {finfo['size_hr']})\n"
                    f"{separator}\n"
                )
            continue

        try:
            if HAS_PARSER:
                result = parse_file(finfo['path'])
                if result is None:
                    skipped_count += 1
                    continue
                text = (result.get("text") or "").strip()
            else:
                with open(finfo['path'], 'r', encoding='utf-8', errors='replace') as f:
                    text = f.read()

            if not text:
                skipped_count += 1
                continue

            # Length truncation (consistent with HTML version logic)
            file_chars = len(text)
            if max_chars is not None and total_chars + file_chars > max_chars:
                allowed = max_chars - total_chars
                if allowed <= 0:
                    # Already at or over limit: add truncation marker and stop
                    remaining = len(file_list) - parsed_count - skipped_count - error_count
                    parts.append(
                        f"{separator}\n"
                        f"[SKIPPED] {finfo['rel_path']} "
                        f"(exceeds remaining char limit)\n"
                        f"{separator}\n"
                    )
                    if remaining > 0:
                        parts.append(
                            f"\n... [Truncated at {max_chars:,} characters, "
                            f"{remaining} remaining file(s) not included] ...\n"
                        )
                    else:
                        parts.append(
                            f"\n... [Truncated at {max_chars:,} characters] ...\n"
                        )
                    break
                text = text[:allowed]
                hit_limit = True
            else:
                hit_limit = False

            # Build file block
            file_info = (
                f"{separator}\n"
                f"File: {finfo['rel_path']}\n"
                f"Size: {finfo['size_hr']}\n"
                f"Characters: {file_chars:,}\n"
                f"Type: {os.path.splitext(finfo['rel_path'])[1] or 'plain'}\n"
                f"{separator}\n"
                f"{text}\n\n"
            )
            parts.append(file_info)
            total_chars += len(text)
            parsed_count += 1

            if hit_limit and max_chars:
                remaining = len(file_list) - parsed_count - skipped_count - error_count - 1  # -1 for current file
                if remaining > 0:
                    parts.append(
                        f"\n... [Truncated at {max_chars:,} characters, "
                        f"{remaining} remaining file(s) not included] ...\n"
                    )
                else:
                    parts.append(
                        f"\n... [Truncated at {max_chars:,} characters] ...\n"
                    )
                break

        except Exception:
            error_count += 1

    # Header info
    header = (
        f"Folder Knowledge Export\n"
        f"Source: {os.path.abspath(folder_path)}\n"
        f"Parsed files: {parsed_count}\n"
        f"Skipped files: {skipped_count}\n"
        f"Errors: {error_count}\n"
        f"Total characters: {total_chars:,}\n"
        f"{'=' * 60}\n\n"
    )
    return header + ''.join(parts), parsed_count, skipped_count, error_count, total_chars