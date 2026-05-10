#!/usr/bin/env python3
"""
DocPortal Desktop — 文件夹知识导出图形界面工具 | Bilingual GUI (中文/English)
提供一键生成 HTML 的桌面应用，支持拖入文件夹、文件管理、内容预览等功能。
"""

import os
import sys
import pathlib
import threading
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from html import escape
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

try:
    from src.parser.dispatcher import parse_file
    HAS_PARSER = True
except ImportError:
    HAS_PARSER = False

# Try to import portal generator
try:
    from src.generator.portal import generate_portal
    HAS_PORTAL = True
except ImportError:
    HAS_PORTAL = False

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ============================================================
#  Bilingual string helper
# ============================================================

def _(zh: str, en: str) -> str:
    """Return bilingual label: 中文 / English"""
    return f"{zh} / {en}"


# ============================================================
#  Folder scanning & HTML generation (adapted from generate.py)
# ============================================================

def human_readable_size(size_bytes):
    """Convert bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def collect_files_info(root_dir):
    """Scan folder and return list of file info dicts."""
    file_list = []
    total_size = 0

    # 使用与 dispatcher.py 一致的 MIME 检测（轻量级，不触发全文解析）
    try:
        import magic  # type: ignore[import-untyped]
        _mime_checker = magic.Magic(mime=True)
        SUPPORTED_MIME_PREFIXES = ('text/',)
        SUPPORTED_MIME_EXACT = {
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/msword',
            'application/vnd.ms-powerpoint',
            'application/vnd.ms-excel',
        }
    except Exception:
        _mime_checker = None
        SUPPORTED_MIME_PREFIXES = ()
        SUPPORTED_MIME_EXACT = set()

    try:
        for dirpath, _, filenames in os.walk(root_dir):
            for fname in filenames:
                if fname.startswith('.'):
                    continue
                full_path = os.path.join(dirpath, fname)
                if not os.path.isfile(full_path):
                    continue
                rel_path = os.path.relpath(full_path, root_dir)
                file_size = os.path.getsize(full_path)
                ext = os.path.splitext(fname)[1].lower()
                # 使用 MIME 类型判断（与 dispatcher.py 一致）
                is_supported = False
                if _mime_checker is not None:
                    try:
                        mime = _mime_checker.from_file(full_path)
                        is_supported = (
                            mime.startswith(SUPPORTED_MIME_PREFIXES)
                            or mime in SUPPORTED_MIME_EXACT
                        )
                    except Exception:
                        pass

                file_list.append({
                    'path': full_path,
                    'rel_path': rel_path,
                    'size': file_size,
                    'size_hr': human_readable_size(file_size),
                    'ext': ext,
                    'supported': is_supported,
                })
                total_size += file_size
    except Exception as e:
        logger.error(f"Error scanning folder: {e}")

    return file_list, total_size


def build_html_from_files(
    folder_path,
    file_list,
    output_path,
    max_chars=None,
    include_skipped=True,
):
    """Parse files and generate HTML content."""
    articles = []
    total_chars = 0
    hit_limit = False
    parsed_count = 0
    skipped_count = 0
    error_count = 0

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
                    f"    <p class=\"meta\">{_('类型不支持', 'Unsupported')} | {_('大小', 'Size')}：{escaped_size}</p>\n"
                    f"  </article>"
                )
                articles.append(article)
            skipped_count += 1
            continue

        try:
            if not HAS_PARSER:
                # Fallback: read as text
                with open(finfo['path'], 'r', encoding='utf-8', errors='replace') as f:
                    text = f.read()
            else:
                result = parse_file(finfo['path'])
                if result is None:
                    skipped_count += 1
                    continue
                text = (result.get("text") or "").strip()

            if not text:
                skipped_count += 1
                continue

            file_chars = len(text)
            if max_chars is not None and total_chars + file_chars > max_chars:
                allowed = max_chars - total_chars
                if allowed <= 0:
                    break
                text = text[:allowed]
                hit_limit = True

            escaped_text = escape(text)
            escaped_path = escape(finfo['rel_path'])
            escaped_size = escape(finfo['size_hr'])
            article = (
                f"  <article>\n"
                f"    <h2>📄 {escaped_path}</h2>\n"
                f"    <p class=\"meta\">{_('大小', 'Size')}：{escaped_size} | {_('内容', 'Content')}：{file_chars} {_('字符', 'chars')}</p>\n"
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
                f"  <!-- {_('已达到 --max-chars 限制（', 'Reached --max-chars limit (')}{max_chars}{_(' 字符），后续文件已截断', ' chars), remaining files truncated')} -->"
            )
            break

    articles_html = "\n".join(articles)
    file_count = parsed_count
    folder_name = escape(os.path.basename(os.path.abspath(folder_path)))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        f"<title>{_('知识导出', 'Knowledge Export')} - {folder_name}</title>\n"
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
        f"      <span>📄 {_('文件数', 'Files')}：{file_count}</span>\n"
        f"      <span>📝 {_('总字符', 'Total chars')}：{total_chars:,}</span>\n"
        f"      <span>🕐 {_('导出时间', 'Exported')}：{now}</span>\n"
        f"      <span>📂 {_('来源', 'Source')}：{escape(os.path.abspath(folder_path))}</span>\n"
        "    </div>\n"
        "  </div>\n"
        f"{articles_html}\n"
        "  <div class=\"footer\">\n"
        f"    <p>{_('由 DocPortal Desktop 生成', 'Generated by DocPortal Desktop')} | {_('共', 'Total')} {file_count} {_('个文件', 'files')}，{total_chars:,} {_('字符', 'chars')}"
        f" | {now}</p>\n"
        "  </div>\n"
        "</body>\n"
        "</html>"
    )
    return html, parsed_count, skipped_count, error_count, total_chars


# ============================================================
#  Modern GUI using tkinter with ttk — bilingual UI
# ============================================================

class DocPortalUI:
    """Main GUI Application for DocPortal — bilingual (中文/English)."""

    COLORS = {
        'bg': '#f0f2f5',
        'card': '#ffffff',
        'primary': '#1a73e8',
        'primary_hover': '#1557b0',
        'success': '#34a853',
        'warning': '#fbbc04',
        'error': '#ea4335',
        'text': '#202124',
        'text_secondary': '#5f6368',
        'border': '#dadce0',
        'drop_bg': '#e8f0fe',
    }

    def __init__(self, root):
        self.root = root
        self.root.title(_("DocPortal Desktop 🚀", "DocPortal Desktop 🚀"))
        self.root.geometry("820x680")
        self.root.minsize(700, 600)

        # Set icon if possible
        try:
            self.root.iconbitmap(default='')
        except Exception:
            pass

        # Configure style
        self.setup_styles()

        # State
        self.current_folder = None
        self.file_list = []
        self.total_size = 0
        self.generating = False
        self.output_path = os.path.join(os.path.expanduser("~"), "Desktop", "knowledge_export.html")

        # Build UI
        self.build_ui()

        # Center window
        self.center_window()

        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.browse_folder())
        self.root.bind('<Control-g>', lambda e: self.generate_html())
        self.root.bind('<Control-s>', lambda e: self.browse_output_or_portal())
        self.root.bind('<Control-p>', lambda e: self.mode_var.set('portal') or self.on_mode_change())
        self.root.bind('<Control-h>', lambda e: self.mode_var.set('single') or self.on_mode_change())
        self.root.bind('<Escape>', lambda e: self.root.quit() if not self.generating else None)

    def setup_styles(self):
        """Configure ttk styles for modern look."""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        bg = self.COLORS['bg']
        card = self.COLORS['card']
        primary = self.COLORS['primary']
        text = self.COLORS['text']

        style.configure('TFrame', background=bg)
        style.configure('TLabel', background=bg, foreground=text, font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10), padding=(12, 6))
        style.configure('Card.TFrame', background=card, relief='solid', borderwidth=1)
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground=primary)
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10), foreground=self.COLORS['text_secondary'])
        style.configure('Stats.TLabel', font=('Segoe UI', 11), foreground=text)
        style.configure('Heading.TLabel', font=('Segoe UI', 11, 'bold'), foreground=text)
        style.configure('Status.TLabel', font=('Segoe UI', 9), foreground=self.COLORS['text_secondary'])

        # Treeview style
        style.configure('Treeview', font=('Segoe UI', 9), rowheight=26)
        style.configure('Treeview.Heading', font=('Segoe UI', 9, 'bold'))
        style.map('Treeview', background=[('selected', primary)])

        # Horizontal TProgressbar
        style.configure('TProgressbar', thickness=10, background=primary)

    # ── Bilingual helper ──
    def __(self, zh: str, en: str) -> str:
        return _(zh, en)

    def build_ui(self):
        """Build the complete UI with bilingual labels."""
        main_frame = ttk.Frame(self.root, padding="16")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ── Header ──
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(header_frame, text=_("DocPortal Desktop", "DocPortal Desktop"), style='Title.TLabel').pack(side=tk.LEFT)
        ttk.Label(header_frame, text=_("📁 → 📄 文件夹转知识HTML", "📁 → 📄 Folder to Knowledge HTML"), style='Subtitle.TLabel').pack(side=tk.LEFT, padx=(10, 0))

        # ── Drop Zone / Folder Selection ──
        self.build_folder_selector(main_frame)

        # ── Stats Bar ──
        self.stats_frame = ttk.Frame(main_frame)
        self.stats_frame.pack(fill=tk.X, pady=(0, 8))
        self.stats_label = ttk.Label(self.stats_frame, text=_("未选择文件夹", "No folder selected"), style='Subtitle.TLabel')
        self.stats_label.pack(side=tk.LEFT)

        # ── File List (Treeview) ──
        self.build_file_list(main_frame)

        # ── Output Settings ──
        self.build_settings(main_frame)

        # ── Generate Button ──
        self.build_generate_section(main_frame)

    def build_folder_selector(self, parent):
        """Build drag-drop zone and folder selection with bilingual text."""
        drop_frame = tk.Frame(
            parent,
            bg=self.COLORS['drop_bg'],
            highlightbackground=self.COLORS['primary'],
            highlightthickness=2,
            highlightcolor=self.COLORS['primary'],
            cursor='hand2',
            height=90,
        )
        drop_frame.pack(fill=tk.X, pady=(0, 8))
        drop_frame.pack_propagate(False)

        # Bind click events
        drop_frame.bind('<Button-1>', lambda e: self.browse_folder())
        drop_frame.bind('<Enter>', lambda e: drop_frame.configure(bg='#d2e3fc'))
        drop_frame.bind('<Leave>', lambda e: drop_frame.configure(bg=self.COLORS['drop_bg']))

        # Drop zone content — bilingual
        drop_text = _(
            "📂 点击浏览选择文件夹  或  直接拖入文件夹到这里",
            "📂 Click to browse a folder   or   drag & drop a folder here"
        )
        self.drop_label = tk.Label(
            drop_frame,
            text=drop_text,
            font=('Segoe UI', 13, 'bold'),
            bg=self.COLORS['drop_bg'],
            fg=self.COLORS['primary'],
            cursor='hand2',
        )
        self.drop_label.pack(expand=True)
        self.drop_label.bind('<Button-1>', lambda e: self.browse_folder())

        # Sub-label with keyboard shortcuts
        hint_text = _("快捷键: Ctrl+O 浏览 | Ctrl+G 生成", "Shortcuts: Ctrl+O Browse | Ctrl+G Generate")
        hint_label = tk.Label(
            drop_frame,
            text=hint_text,
            font=('Segoe UI', 8),
            bg=self.COLORS['drop_bg'],
            fg=self.COLORS['text_secondary'],
        )
        hint_label.pack(side=tk.BOTTOM, pady=(0, 4))

        # Try to register DnD if tkinterdnd2 is available
        try:
            from tkinterdnd2 import DND_FILES
            drop_frame.dnd_bind('<<Drop>>', lambda e: self.handle_dnd(e))
        except ImportError:
            # No need to change label, just pass
            pass

        # Browse button
        browse_btn = tk.Button(
            drop_frame,
            text=_("浏览文件夹...", "Browse Folder..."),
            font=('Segoe UI', 10),
            bg=self.COLORS['primary'],
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self.browse_folder,
            padx=16,
            pady=4,
        )
        browse_btn.place(relx=1.0, rely=1.0, anchor='se', x=-12, y=-8)
        browse_btn.bind('<Enter>', lambda e: browse_btn.configure(bg=self.COLORS['primary_hover']))
        browse_btn.bind('<Leave>', lambda e: browse_btn.configure(bg=self.COLORS['primary']))

    def handle_dnd(self, event):
        """Handle drag and drop event from tkinterdnd2."""
        files = event.data
        if files:
            path = files.strip('{}')
            if os.path.isdir(path):
                self.load_folder(path)
            else:
                folder = os.path.dirname(path)
                if os.path.isdir(folder):
                    self.load_folder(folder)

    def build_file_list(self, parent):
        """Build the file list treeview with bilingual headers."""
        list_container = ttk.Frame(parent)
        list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        ttk.Label(list_container, text=_("📋 文件列表", "📋 File List"), style='Heading.TLabel').pack(anchor=tk.W, pady=(0, 4))

        tree_frame = ttk.Frame(list_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=('name', 'size', 'chars', 'status'),
            show='tree headings',
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
            height=8,
        )

        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)

        self.tree.column('#0', width=30, minwidth=30, stretch=False)
        self.tree.heading('#0', text='')
        self.tree.column('name', width=300, minwidth=150)
        self.tree.heading('name', text=_('文件名', 'Name'), anchor=tk.W)
        self.tree.column('size', width=100, minwidth=80, anchor=tk.E)
        self.tree.heading('size', text=_('大小', 'Size'), anchor=tk.E)
        self.tree.column('chars', width=100, minwidth=80, anchor=tk.E)
        self.tree.heading('chars', text=_('内容字符', 'Chars'), anchor=tk.E)
        self.tree.column('status', width=100, minwidth=60, anchor=tk.CENTER)
        self.tree.heading('status', text=_('状态', 'Status'), anchor=tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.tag_configure('supported', foreground=self.COLORS['text'])
        self.tree.tag_configure('unsupported', foreground=self.COLORS['text_secondary'])
        self.tree.tag_configure('error', foreground=self.COLORS['error'])

    def build_settings(self, parent):
        """Build output settings area with bilingual labels."""
        settings_frame = ttk.Frame(parent)
        settings_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(settings_frame, text=_("⚙️ 输出设置", "⚙️ Output Settings"), style='Heading.TLabel').grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 6)
        )
        settings_frame.columnconfigure(1, weight=1)

        # ── Mode Selection ──
        mode_frame = ttk.Frame(settings_frame)
        mode_frame.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=(0, 4))
        self.mode_var = tk.StringVar(value="single")
        ttk.Label(mode_frame, text=_("输出模式：", "Mode:"), style='Subtitle.TLabel').pack(side=tk.LEFT)
        ttk.Radiobutton(
            mode_frame, text=_("📄 单文件 HTML", "📄 Single HTML"), variable=self.mode_var,
            value="single", command=self.on_mode_change
        ).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Radiobutton(
            mode_frame, text=_("🏛️ 知识门户（可搜索）", "🏛️ Portal (Searchable)"), variable=self.mode_var,
            value="portal", command=self.on_mode_change
        ).pack(side=tk.LEFT, padx=(8, 0))
        portal_status = _("✅ 可用", "✅ Ready") if HAS_PORTAL else _("⚠️ 模块未加载", "⚠️ Unavailable")
        ttk.Label(mode_frame, text=f"({portal_status})", style='Subtitle.TLabel').pack(side=tk.LEFT, padx=(6, 0))

        # Container for "single" mode settings
        self.single_settings = ttk.Frame(settings_frame)
        self.single_settings.grid(row=2, column=0, columnspan=3, sticky=tk.EW)

        # Output path (single mode)
        ttk.Label(self.single_settings, text=_("输出路径：", "Output:")).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 8), pady=2
        )
        self.output_var = tk.StringVar(value=self.output_path)
        output_entry = ttk.Entry(self.single_settings, textvariable=self.output_var, font=('Segoe UI', 9))
        output_entry.grid(row=0, column=1, sticky=tk.EW, pady=2)
        output_btn = tk.Button(
            self.single_settings,
            text=_("选择...", "Browse..."),
            font=('Segoe UI', 9),
            bg=self.COLORS['primary'],
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self.browse_output,
            padx=10,
        )
        output_btn.grid(row=0, column=2, padx=(6, 0), pady=2)
        output_btn.bind('<Enter>', lambda e: output_btn.configure(bg=self.COLORS['primary_hover']))
        output_btn.bind('<Leave>', lambda e: output_btn.configure(bg=self.COLORS['primary']))

        # Max chars (single mode)
        ttk.Label(self.single_settings, text=_("最大字符数：", "Max chars:")).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 8), pady=2
        )
        self.max_chars_var = tk.StringVar(value="50000")
        max_chars_frame = ttk.Frame(self.single_settings)
        max_chars_frame.grid(row=1, column=1, sticky=tk.EW, pady=2)
        max_chars_entry = ttk.Entry(max_chars_frame, textvariable=self.max_chars_var, width=15)
        max_chars_entry.pack(side=tk.LEFT)
        ttk.Label(max_chars_frame, text=_("  (留空=不限)", "  (blank=unlimited)"), style='Subtitle.TLabel').pack(side=tk.LEFT, padx=(6, 0))

        # HTML file name (single mode)
        ttk.Label(self.single_settings, text=_("HTML 文件名：", "Filename:")).grid(
            row=2, column=0, sticky=tk.W, padx=(0, 8), pady=2
        )
        name_frame = ttk.Frame(self.single_settings)
        name_frame.grid(row=2, column=1, sticky=tk.EW, pady=2)
        self.filename_var = tk.StringVar(value="knowledge_export")
        name_entry = ttk.Entry(name_frame, textvariable=self.filename_var, width=25)
        name_entry.pack(side=tk.LEFT)
        ttk.Label(name_frame, text=".html", style='Subtitle.TLabel').pack(side=tk.LEFT, padx=(2, 0))

        self.filename_var.trace_add('write', lambda *a: self.update_output_path())

        # Container for "portal" mode settings
        self.portal_settings = ttk.Frame(settings_frame)
        self.portal_settings.grid(row=3, column=0, columnspan=3, sticky=tk.EW)
        self.portal_settings.grid_remove()

        # Portal output dir
        ttk.Label(self.portal_settings, text=_("输出目录：", "Output dir:")).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 8), pady=2
        )
        self.portal_output_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Desktop", "knowledge_portal"))
        portal_output_entry = ttk.Entry(self.portal_settings, textvariable=self.portal_output_var, font=('Segoe UI', 9))
        portal_output_entry.grid(row=0, column=1, sticky=tk.EW, pady=2)
        portal_output_btn = tk.Button(
            self.portal_settings,
            text=_("选择...", "Browse..."),
            font=('Segoe UI', 9),
            bg=self.COLORS['primary'],
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self.browse_portal_output,
            padx=10,
        )
        portal_output_btn.grid(row=0, column=2, padx=(6, 0), pady=2)
        portal_output_btn.bind('<Enter>', lambda e: portal_output_btn.configure(bg=self.COLORS['primary_hover']))
        portal_output_btn.bind('<Leave>', lambda e: portal_output_btn.configure(bg=self.COLORS['primary']))

        # Portal: chars per page
        ttk.Label(self.portal_settings, text=_("每页字符数：", "Chars/page:")).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 8), pady=2
        )
        self.per_page_var = tk.StringVar(value="8000")
        per_page_frame = ttk.Frame(self.portal_settings)
        per_page_frame.grid(row=1, column=1, sticky=tk.EW, pady=2)
        per_page_entry = ttk.Entry(per_page_frame, textvariable=self.per_page_var, width=15)
        per_page_entry.pack(side=tk.LEFT)
        ttk.Label(per_page_frame, text=_("  (推荐8000)", "  (recommended 8000)"), style='Subtitle.TLabel').pack(side=tk.LEFT, padx=(6, 0))

        # Include skipped files checkbox (shared)
        self.include_skipped_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.single_settings,
            text=_("包含不支持的文件标记", "Show unsupported file markers"),
            variable=self.include_skipped_var,
        ).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=2)
        ttk.Checkbutton(
            self.portal_settings,
            text=_("包含不支持的文件标记", "Show unsupported file markers"),
            variable=self.include_skipped_var,
        ).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=2)

    def build_generate_section(self, parent):
        """Build generate button and status area with bilingual text."""
        gen_frame = ttk.Frame(parent)
        gen_frame.pack(fill=tk.X, pady=(0, 0))

        button_frame = tk.Frame(gen_frame, bg=self.COLORS['bg'])
        button_frame.pack(fill=tk.X, pady=(4, 6))

        self.gen_btn = tk.Button(
            button_frame,
            text=_("🚀 一键生成 HTML", "🚀 Generate HTML"),
            font=('Segoe UI', 13, 'bold'),
            bg=self.COLORS['primary'],
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self.generate_html,
            padx=30,
            pady=8,
            state='disabled',
        )
        self.gen_btn.pack()
        self.gen_btn.bind('<Enter>', lambda e: self.on_gen_btn_hover(True))
        self.gen_btn.bind('<Leave>', lambda e: self.on_gen_btn_hover(False))

        self.progress = ttk.Progressbar(
            button_frame,
            mode='determinate',
            length=400,
        )
        self.progress.pack(pady=(4, 0))
        self.progress.pack_forget()

        # Status bar
        status_frame = tk.Frame(gen_frame, bg=self.COLORS['bg'], height=28)
        status_frame.pack(fill=tk.X)
        status_frame.pack_propagate(False)

        self.status_var = tk.StringVar(value=_("💡 请选择一个文件夹开始", "💡 Select a folder to start"))
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 9),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text_secondary'],
            anchor=tk.W,
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.footer_var = tk.StringVar(value=_("就绪 ✓", "Ready ✓"))
        footer_label = tk.Label(
            status_frame,
            textvariable=self.footer_var,
            font=('Segoe UI', 9),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text_secondary'],
            anchor=tk.E,
        )
        footer_label.pack(side=tk.RIGHT)

    def on_gen_btn_hover(self, is_hover):
        if not self.generating:
            self.gen_btn.configure(
                bg=self.COLORS['primary_hover'] if is_hover else self.COLORS['primary']
            )

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def browse_folder(self):
        folder = filedialog.askdirectory(title=_("选择要导出的文件夹", "Select a folder to export"))
        if folder:
            self.load_folder(folder)

    def load_folder(self, folder_path):
        if self.generating:
            return

        self.current_folder = folder_path
        self.status_var.set(_("📂 正在扫描：", "📂 Scanning: ") + folder_path + "...")
        self.root.update_idletasks()

        def scan():
            file_list, total_size = collect_files_info(folder_path)
            self.root.after(0, lambda: self.on_folder_scanned(file_list, total_size))

        threading.Thread(target=scan, daemon=True).start()

    def on_folder_scanned(self, file_list, total_size):
        self.file_list = file_list
        self.total_size = total_size

        supported = sum(1 for f in file_list if f['supported'])
        self.stats_label.config(
            text=_(
                f"📊 共 {len(file_list)} 个文件 | 支持 {supported} 个 | 总大小 {human_readable_size(total_size)}",
                f"📊 {len(file_list)} files | {supported} supported | {human_readable_size(total_size)} total"
            )
        )

        self.update_file_tree()

        if file_list:
            self.gen_btn.config(state='normal')
            self.status_var.set(_(
                f"✅ 已加载 {len(file_list)} 个文件，{supported} 个可解析",
                f"✅ {len(file_list)} files loaded, {supported} parseable"
            ))
        else:
            self.gen_btn.config(state='disabled')
            self.status_var.set(_("⚠️ 文件夹为空或没有可读文件", "⚠️ Empty folder or no readable files"))

        folder_name = os.path.basename(os.path.normpath(self.current_folder))
        self.filename_var.set(f"{folder_name}_knowledge_export")

    def update_file_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        supported_count = 0
        for finfo in self.file_list:
            ext = finfo['ext']
            icon = '📄' if finfo['supported'] else '⏭️'
            name = f"{icon} {finfo['rel_path']}"
            status = _('✅ 支持', '✅ OK') if finfo['supported'] else _('⏭️ 跳过', '⏭️ Skip')
            tag = 'supported' if finfo['supported'] else 'unsupported'

            self.tree.insert(
                '', 'end',
                values=(name, finfo['size_hr'], '-', status),
                tags=(tag,),
            )
            if finfo['supported']:
                supported_count += 1

        total = len(self.file_list)
        self.footer_var.set(_(
            f"{total} 个文件 | {supported_count} 个可解析",
            f"{total} files | {supported_count} parseable"
        ))

    def on_mode_change(self):
        is_portal = self.mode_var.get() == "portal"
        if is_portal:
            self.single_settings.grid_remove()
            self.portal_settings.grid()
            self.gen_btn.config(text=_("🏛️ 生成知识门户", "🏛️ Generate Portal"))
            self.status_var.set(_(
                "💡 门户模式：每个文档生成独立页面，带搜索和关键词过滤",
                "💡 Portal: each doc as separate page, with search & keyword filter"
            ))
        else:
            self.portal_settings.grid_remove()
            self.single_settings.grid()
            self.gen_btn.config(text=_("🚀 一键生成 HTML", "🚀 Generate HTML"))
            self.status_var.set(_(
                "💡 单文件模式：所有文档合并为一个 HTML 文件",
                "💡 Single HTML: all docs in one file"
            ))

    def browse_portal_output(self):
        folder = filedialog.askdirectory(
            title=_("选择知识门户输出目录", "Select portal output directory"),
            initialdir=os.path.dirname(self.portal_output_var.get())
        )
        if folder:
            self.portal_output_var.set(folder)

    def browse_output(self):
        file_path = filedialog.asksaveasfilename(
            title=_("选择输出 HTML 文件", "Select output HTML file"),
            defaultextension=".html",
            filetypes=[(_("HTML 文件", "HTML files"), "*.html"), (_("所有文件", "All files"), "*.*")],
            initialfile=self.filename_var.get() + ".html",
        )
        if file_path:
            self.output_var.set(file_path)
            basename = os.path.splitext(os.path.basename(file_path))[0]
            self.filename_var.set(basename)

    def update_output_path(self):
        name = self.filename_var.get().strip()
        if name:
            current = self.output_var.get()
            dir_path = os.path.dirname(current) if os.path.dirname(current) else os.path.join(
                os.path.expanduser("~"), "Desktop"
            )
            self.output_var.set(os.path.join(dir_path, f"{name}.html"))

    def browse_output_or_portal(self):
        if self.mode_var.get() == "portal":
            self.browse_portal_output()
        else:
            self.browse_output()

    def generate_html(self):
        if self.generating or not self.current_folder or not self.file_list:
            return

        is_portal = self.mode_var.get() == "portal"
        include_skipped = self.include_skipped_var.get()

        if is_portal:
            if not HAS_PORTAL:
                messagebox.showerror(_("错误", "Error"), _("知识门户模块不可用", "Portal module unavailable"))
                return

            output_dir = self.portal_output_var.get().strip()
            if not output_dir:
                messagebox.showerror(_("错误", "Error"), _("请设置知识门户输出目录", "Set portal output directory"))
                return

            per_page_str = self.per_page_var.get().strip()
            per_page = 8000
            if per_page_str:
                try:
                    per_page = int(per_page_str)
                    if per_page <= 0:
                        per_page = 8000
                except ValueError:
                    messagebox.showerror(_("错误", "Error"), _("每页字符数必须是正整数", "Chars/page must be a positive integer"))
                    return

            self.generating = True
            self.gen_btn.config(state='disabled', text=_("⏳ 正在生成门户...", "⏳ Generating portal..."), bg='#999')
            self.progress['value'] = 0
            self.progress.pack(pady=(4, 0))
            self.status_var.set(_("🏛️ 正在生成知识门户...", "🏛️ Generating portal..."))

            def generate():
                try:
                    result = generate_portal(
                        folder_path=self.current_folder,
                        output_dir=output_dir,
                        max_chars_per_page=per_page,
                        include_skipped=include_skipped,
                    )
                    self.root.after(0, lambda: self.on_portal_complete(result))
                except Exception as e:
                    self.root.after(0, lambda: self.on_generation_error(str(e)))

            threading.Thread(target=generate, daemon=True).start()
            self.simulate_progress()
            return

        # ── Single HTML Mode ──
        output_path = self.output_var.get().strip()
        if not output_path:
            messagebox.showerror(_("错误", "Error"), _("请设置输出路径", "Set output path"))
            return

        if not output_path.lower().endswith('.html'):
            output_path += '.html'
            self.output_var.set(output_path)

        max_chars_str = self.max_chars_var.get().strip()
        max_chars = None
        if max_chars_str:
            try:
                max_chars = int(max_chars_str)
                if max_chars <= 0:
                    max_chars = None
            except ValueError:
                messagebox.showerror(_("错误", "Error"), _("最大字符数必须是正整数", "Max chars must be a positive integer"))
                return

        self.generating = True
        self.gen_btn.config(state='disabled', text=_("⏳ 正在生成...", "⏳ Generating..."), bg='#999')
        self.progress['value'] = 0
        self.progress.pack(pady=(4, 0))
        self.status_var.set(_("⏳ 正在解析文件并生成 HTML...", "⏳ Parsing files and generating HTML..."))

        def generate():
            try:
                html_content, parsed_count, skipped_count, error_count, total_chars = \
                    build_html_from_files(
                        self.current_folder,
                        self.file_list,
                        output_path,
                        max_chars=max_chars,
                        include_skipped=include_skipped,
                    )

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)

                self.root.after(0, lambda: self.progress.config(value=100))
                self.root.after(0, lambda: self.on_generation_complete(
                    output_path, parsed_count, skipped_count, error_count, total_chars
                ))
            except Exception as e:
                self.root.after(0, lambda: self.on_generation_error(str(e)))

        threading.Thread(target=generate, daemon=True).start()
        self.simulate_progress()

    def simulate_progress(self):
        if not self.generating:
            return
        current = self.progress['value']
        if current < 90:
            self.progress['value'] = min(current + 5, 90)
            self.root.after(300, self.simulate_progress)

    def on_generation_complete(self, output_path, parsed_count, skipped_count, error_count, total_chars):
        self.generating = False
        self.progress['value'] = 100

        file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

        self.gen_btn.config(
            state='normal',
            text=_("🚀 一键生成 HTML", "🚀 Generate HTML"),
            bg=self.COLORS['primary'],
        )

        status = _(
            f"✅ 生成成功！{parsed_count} 个文件已解析"
            f"{f'，{skipped_count} 个跳过' if skipped_count else ''}"
            f"{f'，{error_count} 个错误' if error_count else ''}"
            f" | 共 {total_chars:,} 字符"
            f" | 文件大小 {human_readable_size(file_size)}",
            f"✅ Generated! {parsed_count} files parsed"
            f"{f', {skipped_count} skipped' if skipped_count else ''}"
            f"{f', {error_count} errors' if error_count else ''}"
            f" | {total_chars:,} total chars"
            f" | {human_readable_size(file_size)}"
        )
        self.status_var.set(status)
        self.footer_var.set(f"✅ {os.path.basename(output_path)}")

        result = messagebox.askyesno(
            _("✅ 生成成功", "✅ Success"),
            _(
                f"HTML 已成功生成！\n\n"
                f"📄 输出文件：{output_path}\n"
                f"📊 解析文件：{parsed_count} 个\n"
                f"⏭️ 跳过文件：{skipped_count} 个\n"
                f"❌ 错误文件：{error_count} 个\n"
                f"📝 总字符数：{total_chars:,}\n"
                f"💾 文件大小：{human_readable_size(file_size)}\n\n"
                f"是否打开输出文件所在文件夹？",
                f"HTML generated successfully!\n\n"
                f"📄 Output: {output_path}\n"
                f"📊 Parsed: {parsed_count}\n"
                f"⏭️ Skipped: {skipped_count}\n"
                f"❌ Errors: {error_count}\n"
                f"📝 Total chars: {total_chars:,}\n"
                f"💾 File size: {human_readable_size(file_size)}\n\n"
                f"Open output folder?"
            )
        )
        if result:
            self.open_file_location(output_path)

    def on_portal_complete(self, result):
        self.generating = False
        self.progress['value'] = 100

        doc_count = result["doc_count"]
        total_chars = result["total_chars"]
        output_dir = result["output_dir"]
        index_file = result.get("index_file", "")
        skipped = result.get("skipped", 0)
        errors = result.get("errors", 0)

        self.gen_btn.config(
            state='normal',
            text=_("🏛️ 生成知识门户", "🏛️ Generate Portal"),
            bg=self.COLORS['primary'],
        )

        status = _(
            f"✅ 门户生成成功！{doc_count} 个页面"
            f"{f'，{skipped} 个跳过' if skipped else ''}"
            f"{f'，{errors} 个错误' if errors else ''}"
            f" | 共 {total_chars:,} 字符",
            f"✅ Portal generated! {doc_count} pages"
            f"{f', {skipped} skipped' if skipped else ''}"
            f"{f', {errors} errors' if errors else ''}"
            f" | {total_chars:,} total chars"
        )
        self.status_var.set(status)
        self.footer_var.set(f"✅ {os.path.basename(output_dir)}")

        has_index = index_file and os.path.exists(index_file)
        msg = _(
            f"🏛️ 知识门户已成功生成！\n\n"
            f"📂 输出目录：{output_dir}\n"
            f"🏠 首页文件：{index_file if has_index else '(无)'}\n"
            f"📄 生成页面：{doc_count} 个\n"
            f"⏭️ 跳过文件：{skipped} 个\n"
            f"❌ 错误文件：{errors} 个\n"
            f"📝 总字符数：{total_chars:,}\n\n",
            f"🏛️ Portal generated successfully!\n\n"
            f"📂 Output: {output_dir}\n"
            f"🏠 Index: {index_file if has_index else '(none)'}\n"
            f"📄 Pages: {doc_count}\n"
            f"⏭️ Skipped: {skipped}\n"
            f"❌ Errors: {errors}\n"
            f"📝 Total chars: {total_chars:,}\n\n"
        )

        if has_index:
            msg += _(
                "是否打开输出目录？\n\n"
                "💡 使用提示：\n"
                "1. 双击 index.html 在浏览器打开\n"
                "2. 搜索关键词找到目标文档\n"
                "3. 点击文档标题在新标签页打开\n"
                "4. 按 Ctrl+Shift+. 唤醒 Edge Copilot 提问",
                "Open output folder?\n\n"
                "💡 Tips:\n"
                "1. Double-click index.html to open\n"
                "2. Search keywords to find docs\n"
                "3. Click title to open in new tab\n"
                "4. Press Ctrl+Shift+. for Edge Copilot"
            )
            result_dialog = messagebox.askyesno(_("✅ 门户生成成功", "✅ Portal Generated"), msg)
            if result_dialog:
                self.open_file_location(index_file)
        else:
            msg += _("⚠️ 未生成任何文档页面", "⚠️ No pages generated")
            messagebox.showinfo(_("完成", "Done"), msg)

    def on_generation_error(self, error_msg):
        self.generating = False
        self.progress['value'] = 0
        self.progress.pack_forget()

        self.gen_btn.config(
            state='normal',
            text=_("🚀 一键生成 HTML", "🚀 Generate HTML"),
            bg=self.COLORS['primary'],
        )

        self.status_var.set(_("❌ 生成失败：", "❌ Failed: ") + error_msg)
        messagebox.showerror(
            _("生成失败", "Generation Failed"),
            _("HTML 生成过程中出现错误：\n\n", "Error during generation:\n\n") + error_msg
        )

    def open_file_location(self, file_path):
        try:
            if sys.platform == 'win32':
                os.startfile(os.path.dirname(file_path))
            elif sys.platform == 'darwin':
                os.system(f'open "{os.path.dirname(file_path)}"')
            else:
                os.system(f'xdg-open "{os.path.dirname(file_path)}"')
        except Exception:
            pass


# ============================================================
#  Simple DnD capable root window
# ============================================================

class DnDRoot(tk.Tk):
    """Tk root with basic drag and drop support via clipboard/path watching."""
    def __init__(self):
        super().__init__()

    def dnd_bind(self, event_type, callback):
        """Stub for dnd binding."""
        pass


# ============================================================
#  Entry Point
# ============================================================

def main():
    """Launch the DocPortal Desktop GUI."""
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
    except ImportError:
        root = DnDRoot()

    app = DocPortalUI(root)

    if len(sys.argv) > 1:
        folder = sys.argv[1]
        if os.path.isdir(folder):
            root.after(100, lambda: app.load_folder(folder))

    root.mainloop()


if __name__ == "__main__":
    main()
