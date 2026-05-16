"""
FolderKnowledgeSiteGeneratorForAI — GUI Scanning & HTML Building Logic
Extracted from gui.py for better separation of concerns.
Provides folder scanning, file info collection, and single-HTML generation.

NOTE: Truncation by max_chars has been REMOVED. Output is always complete.
      For size-controlled splitting, use --split-chunks (src/chunker/).
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
        # Legacy Office and WPS formats (handled by office_parser with conversion)
        '.doc', '.ppt', '.xls',
        '.wps', '.et', '.dps',
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
    include_skipped: bool = True,
    language: str = "en",
) -> tuple:
    """
    Parse files and generate complete HTML content (no truncation).

    Returns (html_string, parsed_count, skipped_count, error_count, total_chars).
    """
    articles = []
    total_chars = 0
    parsed_count = 0
    skipped_count = 0
    error_count = 0
    # Track skip reasons for console output
    skip_by_reason: dict[str, int] = {}

    for finfo in file_list:
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
    include_skipped: bool = False,
) -> tuple:
    """Generate plain text output, each file wrapped with metadata separator + content.

    NOTE: No truncation — always returns complete output.
    For size-controlled splitting, use --split-chunks (src/chunker/).

    Returns (text, parsed_count, skipped_count, error_count, total_chars).
    """
    parts = []
    total_chars = 0
    parsed_count = 0
    skipped_count = 0
    error_count = 0
    separator = "=" * 60  # separator between files

    for file_idx, finfo in enumerate(file_list):
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

            # Build file block (no truncation)
            file_info = (
                f"{separator}\n"
                f"File: {finfo['rel_path']}\n"
                f"Size: {finfo['size_hr']}\n"
                f"Characters: {len(text):,}\n"
                f"Type: {os.path.splitext(finfo['rel_path'])[1] or 'plain'}\n"
                f"{separator}\n"
                f"{text}\n\n"
            )
            parts.append(file_info)
            total_chars += len(text)
            parsed_count += 1

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


def build_markdown_from_files(
    folder_path: str,
    file_list: list,
    include_skipped: bool = False,
    language: str = "en",
) -> tuple:
    """Generate Markdown output from parsed files.
    
    Each file is wrapped in a Markdown section with metadata.
    Suitable for AI reading and Obsidian integration.

    Returns (md_string, parsed_count, skipped_count, error_count, total_chars).
    """
    sections = []
    total_chars = 0
    parsed_count = 0
    skipped_count = 0
    error_count = 0
    skip_by_reason: dict[str, int] = {}

    # Language-specific labels
    if language == "zh":
        label_size = "文件大小"
        label_chars = "字符数"
        label_format = "格式"
        label_unsupported = "不支持的格式"
        label_skipped = "已跳过"
        label_source = "文件夹名"
        label_files = "解析文件数"
        label_total_chars = "总字符数"
    else:
        label_size = "File size"
        label_chars = "Characters"
        label_format = "Format"
        label_unsupported = "Unsupported format"
        label_skipped = "Skipped"
        label_source = "Source folder"
        label_files = "Files parsed"
        label_total_chars = "Total characters"

    for finfo in file_list:
        if not finfo['supported']:
            skipped_count += 1
            skip_by_reason['unsupported format'] = skip_by_reason.get('unsupported format', 0) + 1
            if include_skipped:
                rel_path = finfo['rel_path'].replace('\\', '/')
                section = (
                    f"---\n\n"
                    f"## ⏭️ {rel_path}\n\n"
                    f"**{label_unsupported}** | **{label_size}**: {finfo['size_hr']}\n\n"
                    f"> *This file format is not supported.*\n"
                )
                sections.append(section)
            continue

        try:
            if HAS_PARSER:
                result = parse_file(finfo['path'])
                if result is None:
                    skipped_count += 1
                    skip_by_reason['parser returned no content'] = skip_by_reason.get('parser returned no content', 0) + 1
                    continue
                text = (result.get("text") or "").strip()
            else:
                with open(finfo['path'], 'r', encoding='utf-8', errors='replace') as f:
                    text = f.read()

            if not text:
                skipped_count += 1
                skip_by_reason['empty content after parsing'] = skip_by_reason.get('empty content after parsing', 0) + 1
                continue

            file_chars = len(text)
            rel_path = finfo['rel_path'].replace('\\', '/')
            ext = os.path.splitext(finfo['rel_path'])[1].lower()

            # Determine language tag for code block
            lang_tag = _get_md_lang_tag(ext)

            section = (
                f"---\n\n"
                f"## 📄 {rel_path}\n\n"
                f"**{label_size}**: {finfo['size_hr']}  \n"
                f"**{label_chars}**: {file_chars:,}\n\n"
                f"```{lang_tag}\n"
                f"{text}\n"
                f"```\n"
            )
            sections.append(section)
            total_chars += len(text)
            parsed_count += 1

        except Exception:
            error_count += 1
            continue

    # Print skip reasons to console
    if skip_by_reason:
        print(f"[Skip Summary] {skipped_count} files skipped:")
        for reason, count in sorted(skip_by_reason.items(), key=lambda x: -x[1]):
            print(f"  - {count} file(s): {reason}")
    if error_count:
        print(f"[Error Summary] {error_count} file(s) failed to parse")

    folder_name = os.path.basename(os.path.abspath(folder_path))

    # Header
    header = (
        f"# {label_source}：{folder_name}\n\n"
        f"**{label_files}**：{parsed_count}，**{label_total_chars}**：{total_chars:,}\n\n"
        f"---\n\n"
    )

    return header + ''.join(sections), parsed_count, skipped_count, error_count, total_chars


def _get_md_lang_tag(ext: str) -> str:
    """Map file extension to Markdown code block language tag."""
    lang_map = {
        '.py': 'python', '.pyw': 'python',
        '.js': 'javascript', '.jsx': 'jsx',
        '.ts': 'typescript', '.tsx': 'tsx',
        '.html': 'html', '.htm': 'html',
        '.css': 'css', '.scss': 'scss', '.less': 'less',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml', '.yml': 'yaml',
        '.toml': 'toml',
        '.md': 'markdown',
        '.rst': 'rst',
        '.sh': 'bash', '.bash': 'bash', '.zsh': 'bash', '.fish': 'fish',
        '.bat': 'batch', '.cmd': 'batch',
        '.ps1': 'powershell', '.psm1': 'powershell', '.psd1': 'powershell',
        '.c': 'c', '.cpp': 'cpp', '.h': 'c', '.hpp': 'cpp',
        '.cs': 'csharp',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin', '.kts': 'kotlin',
        '.sql': 'sql',
        '.lua': 'lua',
        '.r': 'r', '.R': 'r',
        '.dart': 'dart',
        '.scala': 'scala',
        '.pl': 'perl', '.pm': 'perl',
        '.tex': 'latex',
        '.cfg': 'ini', '.ini': 'ini', '.conf': 'ini',
    }
    return lang_map.get(ext, '')