#!/usr/bin/env python3
"""
FolderKnowledgeSiteGeneratorForAI — Folder to Knowledge HTML / Portal Generator

Usage:
    # 传统模式：生成单个大 HTML 文件
    python generate.py <folder_path> -o <output.html>
    python generate.py <folder_path> -o <output.html> --max-chars 50000

    # 门户模式：生成可搜索的单页知识门户
    python generate.py <folder_path> --portal -o <output_dir/>

Scans all files in a folder, parses documents (PDF, DOCX, PPTX, XLSX, TXT, etc.),
and generates:
  - 传统模式：一个结构化 HTML 文件，适合直接喂给 LLM
  - 门户模式：一个可搜索、可折叠的单页知识门户，适合 AI 完整消费
"""

import os
import sys
import pathlib
import argparse
import logging
import io

# Fix console encoding for Windows (防止中文乱码)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ensure the project root is on sys.path so the src package is always findable
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from src.gui_scanner import build_text_from_files, collect_files_info

# Import shared filter rules from constants
try:
    from src.constants import FILTER_DIRS as _FILTER_DIRS, should_filter_file as _should_filter_file
except ImportError:
    _FILTER_DIRS = frozenset()
    _should_filter_file = lambda rel_path: False

# Try to import portal generator
try:
    from src.generator.portal import generate_portal
    HAS_PORTAL = True
except ImportError:
    HAS_PORTAL = False

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def collect_files(root_dir):
    """Walk through root_dir and yield all regular file paths (relative)."""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [
            d for d in dirnames
            if d not in _FILTER_DIRS and not d.startswith('.')
        ]
        for fname in filenames:
            full_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(full_path, root_dir)
            if _should_filter_file(rel_path):
                continue
            if os.path.isfile(full_path):
                yield full_path, rel_path


def build_text_content(folder_path, max_chars=None):
    """Parse all files under folder_path and return text content."""
    file_list, _ = collect_files_info(folder_path)
    text, parsed, skipped, errors, chars = build_text_from_files(
        folder_path, file_list, max_chars=max_chars, include_skipped=True
    )
    return text, parsed, skipped, errors, chars


def main():
    parser = argparse.ArgumentParser(
        description="FolderKnowledgeSiteGeneratorForAI - 将文件夹中的文档解析为结构化 HTML 或分页知识门户"
    )
    parser.add_argument("folder", help="要扫描的文件夹路径")
    parser.add_argument("-o", "--output", required=True, help="输出路径（文件或目录）")
    parser.add_argument(
        "--max-chars",
        type=int,
        default=None,
        help="[传统模式] 输出总字符数上限（默认不限）",
    )
    parser.add_argument(
        "--portal",
        action="store_true",
        help="[门户模式] 生成可搜索的单页知识门户（推荐 AI 使用）",
    )
    parser.add_argument(
        "--no-skipped",
        action="store_true",
        help="[门户模式] 不在首页中显示不支持的文档标记",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print("错误：路径不是有效的文件夹：%s" % args.folder, file=sys.stderr)
        sys.exit(1)

    if args.portal:
        # -- 门户模式 --
        if not HAS_PORTAL:
            print("错误：门户模块不可用（src/generator/portal.py 未找到）", file=sys.stderr)
            sys.exit(1)

        output_dir = args.output
        print("[FolderKnowledgeSiteGeneratorForAI] 正在生成知识门户到: %s" % output_dir)
        print()

        result = generate_portal(
            folder_path=args.folder,
            output_dir=output_dir,
            include_skipped=not args.no_skipped,
        )

        index_file = result.get("index_file")
        if index_file and os.path.exists(index_file):
            print("OK - 知识门户生成成功！")
            print("   [输出目录] %s" % result['output_dir'])
            print("   [首页入口] %s" % index_file)
            print("   [文档数量] %d" % result['doc_count'])
            print("   [总字符数] %s" % f"{result['total_chars']:,}")
            if result['skipped']:
                print("   [跳过文件] %d" % result['skipped'])
            if result['errors']:
                print("   [错误文件] %d" % result['errors'])
            print()
            print("[使用提示]")
            print("   1. 双击 index.html 在浏览器中打开")
            print("   2. 搜索关键词找到目标文档")
            print("   3. 点击文档标题在新标签页打开")
            print("   4. 按 Ctrl+Shift+. 唤醒 Edge Copilot 提问")
        else:
            print("警告：未生成任何文档（文件夹为空或所有文件都无法解析）", file=sys.stderr)
            sys.exit(1)
    else:
        # -- 传统模式 (TXT generation) --
        text, parsed, skipped, errors, chars = build_text_content(
            args.folder, max_chars=args.max_chars
        )

        # Ensure .txt extension
        output_path = args.output
        if not output_path.lower().endswith('.txt'):
            output_path += '.txt'

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        file_count_text = text.count('=' * 60) - 1  # Subtract the header separator
        print("OK - 已生成知识文件: %s" % output_path)
        print("    共包含 %d 个文件内容, %d 总字符" % (parsed, chars))
        if skipped:
            print("    %d 个文件被跳过" % skipped)
        if errors:
            print("    %d 个文件解析出错" % errors)
        print()
        print("提示：用 --portal 参数生成分页知识门户，可搜索且 Edge Copilot 友好")
        print("提示：生成的 .txt 文件可直接上传到 DeepSeek/ChatGPT/Claude")


if __name__ == "__main__":
    main()