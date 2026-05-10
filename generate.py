#!/usr/bin/env python3
"""
FolderRAG — Folder to Knowledge HTML Generator

Usage:
    python generate.py <folder_path> -o <output.html>
    python generate.py <folder_path> -o <output.html> --max-chars 50000

Scans all files in a folder, parses documents (PDF, DOCX, PPTX, XLSX, TXT, etc.),
and generates a single structured HTML file suitable for feeding to LLMs / AI tools.
"""

import os
import sys
import pathlib
import argparse
import logging
from html import escape

# Ensure the project root is on sys.path so the src package is always findable
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from src.parser.dispatcher import parse_file

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def collect_files(root_dir):
    """Walk through root_dir and yield all regular file paths (relative)."""
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.startswith('.'):
                continue
            full_path = os.path.join(dirpath, fname)
            if os.path.isfile(full_path):
                rel_path = os.path.relpath(full_path, root_dir)
                yield full_path, rel_path


def build_html(folder_path, max_chars=None):
    """Parse all files under folder_path and return a complete HTML string."""
    articles = []
    total_chars = 0
    hit_limit = False

    for full_path, rel_path in collect_files(folder_path):
        if hit_limit:
            break

        logger.info("Parsing: %s", rel_path)

        try:
            result = parse_file(full_path)
        except Exception:
            logger.exception("Error parsing %s", rel_path)
            continue

        if result is None:
            logger.info("  -> Skipped (unsupported type)")
            continue

        text = (result.get("text") or "").strip()
        if not text:
            logger.info("  -> Skipped (empty content)")
            continue

        # Truncate individual file content if needed
        file_chars = len(text)
        if max_chars is not None and total_chars + file_chars > max_chars:
            allowed = max_chars - total_chars
            if allowed <= 0:
                break
            text = text[:allowed]
            hit_limit = True

        escaped_text = escape(text)
        escaped_path = escape(rel_path)
        article = (
            f"  <article>\n"
            f"    <h2>来源：{escaped_path}</h2>\n"
            f"    <p>{escaped_text}</p>\n"
            f"  </article>"
        )
        articles.append(article)
        total_chars += len(text)

        if hit_limit:
            articles.append(
                f"  <!-- 已达到 --max-chars 限制（{max_chars} 字符），后续文件已截断 -->"
            )
            break

    # Build articles section and count actual file articles
    articles_html = chr(10).join(articles)
    file_count = articles_html.count('<article>')

    html = (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        "<title>Knowledge Export</title>\n"
        "<style>\n"
        "  body { font-family: sans-serif; max-width: 960px; margin: 0 auto; padding: 20px; }\n"
        "  article { border: 1px solid #ddd; border-radius: 6px; padding: 16px; margin-bottom: 16px; }\n"
        "  h2 { font-size: 1.1em; color: #2c3e50; margin-top: 0; word-break: break-all; }\n"
        "  p { white-space: pre-wrap; word-break: break-word; font-size: 0.95em; line-height: 1.6; }\n"
        "</style>\n"
        "</head>\n"
        "<body>\n"
        f"  <h1>文件夹知识导出</h1>\n"
        f"  <p>来源：{escape(os.path.abspath(folder_path))}</p>\n"
        f"  <p>共 {file_count} 个文件，{total_chars} 字符</p>\n"
        f"  <hr>\n"
        f"{articles_html}\n"
        "</body>\n"
        "</html>"
    )
    return html


def main():
    parser = argparse.ArgumentParser(
        description="FolderRAG — 将文件夹中的文档解析为结构化 HTML"
    )
    parser.add_argument("folder", help="要扫描的文件夹路径")
    parser.add_argument("-o", "--output", required=True, help="输出 HTML 文件路径")
    parser.add_argument(
        "--max-chars",
        type=int,
        default=None,
        help="输出总字符数上限（默认不限）",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print(f"错误：路径不是有效的文件夹：{args.folder}", file=sys.stderr)
        sys.exit(1)

    html = build_html(args.folder, max_chars=args.max_chars)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"OK - 已生成知识文件: {args.output}")
    print(f"    共包含 {html.count('<article>')} 个文件内容")


if __name__ == "__main__":
    main()
