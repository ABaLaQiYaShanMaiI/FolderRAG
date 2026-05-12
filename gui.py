#!/usr/bin/env python3
"""
FolderKnowledgeSiteGeneratorForAI Desktop — Knowledge Portal Generator
"""

import os
import sys
import pathlib
import threading
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from functools import partial

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

try:
    from src.generator.portal import generate_portal, generate_portal_split
    HAS_PORTAL = True
except ImportError:
    HAS_PORTAL = False

from src.gui_scanner import collect_files_info, build_text_from_files
from src.utils import human_readable_size

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class FolderKnowledgeSiteGeneratorForAIUI:

    CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".folderknowledge_settings.json")

    COLORS = {
        'bg': '#f0f2f5', 'card': '#ffffff', 'primary': '#1a73e8',
        'primary_hover': '#1557b0', 'success': '#34a853', 'warning': '#fbbc04',
        'error': '#ea4335', 'text': '#202124', 'text_secondary': '#5f6368',
        'border': '#dadce0', 'drop_bg': '#e8f0fe', 'drop_bg_hover': '#d2e3fc',
    }

    L = {
        'en': {
            'title': 'FolderKnowledgeSiteGeneratorForAI',
            'subtitle': 'Folder → Knowledge Portal',
            'drop': 'Click or drop a folder here',
            'hint': 'Ctrl+O Browse  |  Ctrl+G Generate',
            'browse': 'Browse',
            'paste_btn': 'Paste',
            'paste_done': 'Folder pasted from clipboard',
            'clip_empty': 'Clipboard empty or not a folder path',
            'scanning': 'Scanning...',
            'no_folder': 'No folder selected',
            'empty': 'Empty folder or no readable files',
            'file_list': 'Files',
            'mode_label': 'Mode:',
            'single': 'Single TXT',
            'chunked_mode': 'Split TXT',
            'portal_mode': 'Portal',
            'ready': 'Ready',
            'unavail': 'Unavailable',
            'output': 'Output:',
            'unlimited': '(blank=unlimited)',
            'fname': 'Name:',
            'show_skip': 'Show unsupported',
            'out_dir': 'Output dir:',
            'gen_btn': 'Generate TXT',
            'gen_chunked_btn': 'Generate Split TXT',
            'gen_portal_btn': 'Generate Portal',
            'start_hint': 'Select a folder to start',
            'status_ready': 'Ready',
            'files': 'files',
            'supported': 'supported',
            'parseable': 'parseable',
            'gen_done': 'TXT generated!',
            'portal_done': 'Portal generated!',
            'chunked_done': 'Split TXT generated!',
            'open_folder': 'Open output folder?',
            'server_start': 'Start Server',
            'server_stop': 'Stop Server',
            'server_running': 'Server running at',
            'server_ask': 'Start local server for AI/Copilot reading?',
            'copy_url': 'Copy URL',
            'port_label': 'Port:',
            'total': 'Total',
            'chunk_out_dir': 'Output dir:',
            'chunk_size_label': 'Chunk size:',
            'chunk_chars': 'chars',
            'force_split': 'Force split oversized files',
            'chunked_mode_desc': 'Split TXT: break large output into multiple part_*.txt files',
            'chunked_mode_desc_en': 'Split TXT: break large output into multiple part_*.txt files',
        },
        'zh': {
            'title': 'FolderKnowledgeSiteGeneratorForAI',
            'subtitle': '文件夹 → 知识门户',
            'drop': '点击选择或将文件夹拖入此处',
            'hint': 'Ctrl+O 浏览  |  Ctrl+G 生成',
            'browse': '浏览',
            'paste_btn': '粘贴',
            'paste_done': '已从剪贴板粘贴路径',
            'clip_empty': '剪贴板为空或非文件夹路径',
            'scanning': '正在扫描...',
            'no_folder': '未选择文件夹',
            'empty': '文件夹为空或没有可读文件',
            'file_list': '文件列表',
            'mode_label': '模式：',
            'single': '单文件 TXT',
            'chunked_mode': '分片 TXT',
            'portal_mode': '门户',
            'ready': '就绪',
            'unavail': '不可用',
            'output': '输出：',
            'max_chars': '最大字符：',
            'unlimited': '(留空=不限)',
            'fname': '文件名：',
            'show_skip': '显示不支持标记',
            'out_dir': '输出目录：',
            'gen_btn': '生成 TXT',
            'gen_chunked_btn': '生成分片 TXT',
            'gen_portal_btn': '生成门户',
            'start_hint': '请选择文件夹开始',
            'status_ready': '就绪',
            'files': '个文件',
            'supported': '个支持',
            'parseable': '个可解析',
            'gen_done': 'TXT 生成成功！',
            'portal_done': '门户生成成功！',
            'chunked_done': '分片 TXT 生成成功！',
            'open_folder': '打开输出文件夹？',
            'server_start': '启动服务器',
            'server_stop': '停止服务器',
            'server_running': '服务器运行中：',
            'server_ask': '是否启动本地服务器供 AI 读取？',
            'copy_url': '复制地址',
            'port_label': '端口：',
            'total': '总计',
            'chunk_out_dir': '输出目录：',
            'chunk_size_label': '分片大小：',
            'chunk_chars': '字符',
            'force_split': '强制切分超大文件',
            'chunked_mode_desc': '分片模式：将大输出拆分为多个 part_*.txt 文件',
            'chunked_mode_desc_en': 'Split TXT: break large output into multiple part_*.txt files',
        },
    }

    def __init__(self, root):
        self.root = root
        self._lang = 'en'
        self.current_folder = None
        self.file_list = []
        self.total_size = 0
        self.generating = False
        self.output_path = os.path.join(os.path.expanduser("~"), "Desktop", "knowledge_export.txt")
        # NOTE: max_chars per-file truncation has been REMOVED.
        # TXT mode always outputs complete content.
        # For size-controlled splitting, use --split-chunks CLI mode.

        # --- HTTP server state ---
        self._server_thread = None
        self._httpd = None
        self._server_port = 8080
        self._server_root = None

        self._load_settings()

        self.root.title("FolderKnowledgeSiteGeneratorForAI")
        self.root.geometry("820x720")
        self.root.minsize(700, 600)
        self.setup_styles()
        self.build_all()
        self.center_window()
        self.bind_shortcuts()

        # Bind window close to auto-stop server
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def tr(self, key):
        return self.L[self._lang][key]

    def set_lang(self, lang):
        if lang != self._lang:
            saved_mode = self.mode_var.get() if hasattr(self, 'mode_var') else 'single'
            saved_skip = self.skip_var.get() if hasattr(self, 'skip_var') else True
            saved_fname = self.fname_var.get() if hasattr(self, 'fname_var') else 'knowledge_export'
            saved_output = self.out_var.get() if hasattr(self, 'out_var') else self.output_path
            saved_pout = self.pout_var.get() if hasattr(self, 'pout_var') else os.path.join(os.path.expanduser("~"), "Desktop", "knowledge_portal")

            self._lang = lang
            self._save_settings()
            self.build_all()

            self.mode_var.set(saved_mode)
            self.skip_var.set(saved_skip)
            self.fname_var.set(saved_fname)
            self.out_var.set(saved_output)
            self.pout_var.set(saved_pout)
            self.on_mode_change()

    def _save_settings(self):
        import json
        try:
            data = {"language": self._lang, "server_port": self._server_port}
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning("Failed to save settings: %s", e)

    def _load_settings(self):
        import json
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                lang = data.get("language", "en")
                if lang in self.L:
                    self._lang = lang
                self._server_port = data.get("server_port", 8080)
        except Exception as e:
            logger.warning("Failed to load settings: %s", e)

    def _on_close(self):
        """Cleanup on window close: stop HTTP server."""
        self._stop_server()
        self.root.destroy()

    def _start_server(self, directory, port=8080, max_attempts=10):
        """Start HTTP server in a daemon thread."""
        import http.server
        import socketserver
        import webbrowser

        if self._httpd is not None:
            return True

        actual_port = port
        socketserver.TCPServer.allow_reuse_address = True
        for attempt in range(max_attempts):
            try:
                handler = partial(http.server.SimpleHTTPRequestHandler, directory=directory)
                self._httpd = socketserver.TCPServer(("", actual_port), handler)
                break
            except OSError as e:
                if "Address already in use" in str(e) or "10048" in str(e) or "only one usage" in str(e).lower():
                    actual_port += 1
                    continue
                else:
                    logger.error("Failed to start server: %s", e)
                    return False
            except Exception as e:
                logger.error("Failed to start server: %s", e)
                return False
        else:
            logger.error("Could not find free port after %d attempts", max_attempts)
            return False

        self._server_port = actual_port
        self._server_root = directory
        self._server_thread = threading.Thread(
            target=self._httpd.serve_forever,
            daemon=True,
            name="HTTPServer"
        )
        self._server_thread.start()
        self._save_settings()

        # Update status bar
        self._update_server_ui()

        # Open browser
        webbrowser.open(f"http://localhost:{actual_port}/index.html")
        return True

    def _stop_server(self):
        """Stop the HTTP server."""
        if self._httpd:
            try:
                self._httpd.shutdown()
                self._httpd.server_close()
            except Exception:
                pass
            self._httpd = None
            self._server_thread = None
            self._server_root = None
        self._update_server_ui()

    def _update_server_ui(self):
        """Update server status display in UI."""
        is_running = self._httpd is not None

        if hasattr(self, 'server_status_lbl'):
            if is_running:
                url = f"http://localhost:{self._server_port}"
                self.server_status_lbl.config(
                    text=f"🟢 {self.tr('server_running')} {url}",
                    fg=self.COLORS['success']
                )
                self.server_start_btn.pack_forget()
                self.server_stop_btn.pack(side=tk.LEFT, padx=2)
                self.server_copy_btn.pack(side=tk.LEFT, padx=2)
            else:
                self.server_status_lbl.config(
                    text=self.tr('status_ready'),
                    fg=self.COLORS['text_secondary']
                )
                self.server_stop_btn.pack_forget()
                self.server_copy_btn.pack_forget()
                self.server_start_btn.pack(side=tk.LEFT, padx=2)

    def _copy_server_url(self):
        """Copy server URL to clipboard."""
        if self._httpd:
            url = f"http://localhost:{self._server_port}"
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            self.status_var.set(f"URL copied: {url}")

    def setup_styles(self):
        style = ttk.Style(); style.theme_use('clam')
        c = self.COLORS
        style.configure('TFrame', background=c['bg'])
        style.configure('TLabel', background=c['bg'], foreground=c['text'], font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10), padding=(12, 6))
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground=c['primary'])
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10), foreground=c['text_secondary'])
        style.configure('Heading.TLabel', font=('Segoe UI', 11, 'bold'), foreground=c['text'])
        style.configure('Treeview', font=('Segoe UI', 9), rowheight=26)
        style.configure('Treeview.Heading', font=('Segoe UI', 9, 'bold'))
        style.map('Treeview', background=[('selected', c['primary'])])
        style.configure('TProgressbar', thickness=10, background=c['primary'])

    def build_all(self):
        for w in self.root.winfo_children():
            w.destroy()

        self.main = ttk.Frame(self.root, padding="10")
        self.main.pack(fill=tk.BOTH, expand=True)

        # ── Header bar ──
        hdr = tk.Frame(self.main, bg=self.COLORS['bg'])
        hdr.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(hdr, text=self.tr('title'), style='Title.TLabel').pack(side=tk.LEFT)
        ttk.Label(hdr, text=self.tr('subtitle'), style='Subtitle.TLabel').pack(side=tk.LEFT, padx=(8, 0))

        # Language toggle
        lang_f = tk.Frame(hdr, bg=self.COLORS['bg'])
        lang_f.pack(side=tk.RIGHT)
        for lcode, ltxt in [('en', 'EN'), ('zh', '中文')]:
            bg = self.COLORS['primary'] if self._lang == lcode else '#ccc'
            fg = 'white' if self._lang == lcode else '#333'
            btn = tk.Button(lang_f, text=ltxt, font=('Segoe UI', 9, 'bold'),
                            bg=bg, fg=fg, relief='flat', padx=8, pady=2,
                            cursor='hand2', command=lambda c=lcode: self.set_lang(c))
            btn.pack(side=tk.LEFT, padx=1)

        # ── Folder row: entry + browse + paste ──
        self.build_folder_row()

        # ── File list ──
        self.build_file_list()

        # ── Settings panel ──
        self.build_settings()

        # ── Server control bar ──
        self.build_server_controls()

        # ── Generate button + status ──
        self.build_gen_section()

    def build_folder_row(self):
        folder_f = tk.Frame(self.main, bg=self.COLORS['card'],
                            highlightbackground=self.COLORS['primary'],
                            highlightthickness=2, padx=10, pady=8, cursor='hand2')
        folder_f.pack(fill=tk.X, pady=(0, 6))
        self.folder_drop_frame = folder_f

        try:
            from tkinterdnd2 import DND_FILES
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self._on_drop)
        except Exception as e:
            print("TkinterDnD not available:", e)

        folder_f.bind('<Enter>', lambda e: folder_f.configure(bg=self.COLORS['drop_bg_hover']))
        folder_f.bind('<Leave>', lambda e: folder_f.configure(bg=self.COLORS['card']))
        folder_f.bind('<Button-1>', lambda e: self.browse_folder())

        tk.Label(folder_f, text=self.tr('drop'), font=('Segoe UI', 11, 'bold'),
                 bg=self.COLORS['card'], fg=self.COLORS['primary'], cursor='hand2').pack()

        tk.Label(folder_f, text=self.tr('hint'), font=('Segoe UI', 8),
                 bg=self.COLORS['card'], fg=self.COLORS['text_secondary']).pack(pady=(2, 6))

        row = tk.Frame(folder_f, bg=self.COLORS['card'])
        row.pack(fill=tk.X)

        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(row, textvariable=self.path_var, font=('Segoe UI', 10))
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        path_entry.bind('<Return>', lambda e: self.load_from_path())

        def make_btn(text, command, bg_color):
            btn = tk.Button(row, text=text, font=('Segoe UI', 10),
                            bg=bg_color, fg='white', relief='flat',
                            cursor='hand2', command=command, padx=14, pady=3)
            btn._normal_bg = bg_color
            btn._hover_bg = '#1557b0' if text != 'Clear' else '#d32f2f'
            btn.pack(side=tk.LEFT, padx=2)
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=b._hover_bg))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=b._normal_bg))
            return btn

        make_btn(self.tr('browse'), self.browse_folder, self.COLORS['primary'])
        make_btn(self.tr('paste_btn'), self.paste_folder, self.COLORS['primary'])
        make_btn('Clear', self.clear_folder, self.COLORS['error'])

    def _on_drop(self, event):
        """Handle file/folder drag-and-drop.
        
        In Windows, event.data may contain multiple paths wrapped in { } { }.
        Extracts the first valid folder path and loads it.
        """
        raw = event.data or ""
        if not raw:
            return
        
        # Split multiple paths (Windows format: "{path1}" "{path2}")
        # Handle both with and without curly brace wrapping
        import re as _re
        candidates = _re.findall(r'\{([^}]+)\}|"([^"]+)"|(\S+)', raw)
        paths = [p for group in candidates for p in group if p]
        
        for candidate in paths:
            path = candidate.strip().strip('"').strip("'")
            if os.path.isdir(path):
                self.path_var.set(path)
                self.load_folder(path)
                return
            folder = os.path.dirname(path)
            if os.path.isdir(folder):
                self.path_var.set(folder)
                self.load_folder(folder)
                return
        
        # Fallback: treat entire data as a single path
        path = raw.strip('{}').strip('"')
        if os.path.isdir(path):
            self.path_var.set(path)
            self.load_folder(path)
        else:
            folder = os.path.dirname(path)
            if os.path.isdir(folder):
                self.path_var.set(folder)
                self.load_folder(folder)

    def build_file_list(self):
        # Card-style frame with background color and border for the file tree
        flist_card = tk.Frame(self.main, bg=self.COLORS['card'],
                              highlightbackground=self.COLORS['border'],
                              highlightthickness=1, padx=10, pady=8)
        flist_card.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        hdr_f = tk.Frame(flist_card, bg=self.COLORS['card'])
        hdr_f.pack(fill=tk.X, pady=(0, 3))
        tk.Label(hdr_f, text=self.tr('file_list'), font=('Segoe UI', 11, 'bold'),
                 bg=self.COLORS['card'], fg=self.COLORS['text']).pack(side=tk.LEFT)
        self.stats_lbl = tk.Label(hdr_f, text=self.tr('no_folder'),
                                  font=('Segoe UI', 9),
                                  bg=self.COLORS['card'], fg=self.COLORS['text_secondary'])
        self.stats_lbl.pack(side=tk.RIGHT)

        # ── Search bar for code content search ──
        search_row = tk.Frame(flist_card, bg=self.COLORS['card'])
        search_row.pack(fill=tk.X, pady=(0, 3))

        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *a: self._filter_file_tree())
        search_entry = ttk.Entry(search_row, textvariable=self.search_var,
                                 font=('Segoe UI', 10))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        search_entry.bind('<KeyRelease>', lambda e: self._filter_file_tree())

        search_clear_btn = tk.Button(search_row, text='✕', font=('Segoe UI', 9),
                                     bg=self.COLORS['text_secondary'], fg='white',
                                     relief='flat', width=3, cursor='hand2',
                                     command=lambda: self.search_var.set(''))
        search_clear_btn.pack(side=tk.LEFT, padx=1)
        search_clear_btn.bind('<Enter>', lambda e: search_clear_btn.configure(bg='#999'))
        search_clear_btn.bind('<Leave>', lambda e: search_clear_btn.configure(bg=self.COLORS['text_secondary']))

        # Search mode toggle: file name only / full code content
        self.search_mode_var = tk.StringVar(value='name')
        name_rb = tk.Radiobutton(search_row, text='Name', variable=self.search_mode_var,
                                 value='name', font=('Segoe UI', 8),
                                 bg=self.COLORS['card'], selectcolor=self.COLORS['card'],
                                 command=self._filter_file_tree)
        name_rb.pack(side=tk.LEFT, padx=(2, 0))
        code_rb = tk.Radiobutton(search_row, text='Code', variable=self.search_mode_var,
                                 value='code', font=('Segoe UI', 8),
                                 bg=self.COLORS['card'], selectcolor=self.COLORS['card'],
                                 command=self._filter_file_tree)
        code_rb.pack(side=tk.LEFT, padx=(0, 2))

        # ── Spacer pushes hints to the right ──
        spacer = tk.Frame(search_row, bg=self.COLORS['card'])
        spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Search mode hint on the right side (文件结构右边)
        self.search_hint_lbl = tk.Label(search_row, text='', font=('Segoe UI', 7),
                                        bg=self.COLORS['card'], fg=self.COLORS['text_secondary'])
        self.search_hint_lbl.pack(side=tk.RIGHT, padx=(0, 6))

        # Keyboard shortcut hint (最右边)
        if self._lang == 'zh':
            shortcut_text = '双击打开  |  Esc退出'
        else:
            shortcut_text = 'Double-click open  |  Esc quit'
        shortcut_lbl = tk.Label(search_row, text=shortcut_text, font=('Segoe UI', 7),
                                bg=self.COLORS['card'], fg=self.COLORS['text_secondary'])
        shortcut_lbl.pack(side=tk.RIGHT, padx=(0, 2))

        tree_f = tk.Frame(flist_card, bg=self.COLORS['card'])
        tree_f.pack(fill=tk.BOTH, expand=True)

        vs = ttk.Scrollbar(tree_f, orient=tk.VERTICAL)
        hs = ttk.Scrollbar(tree_f, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(tree_f, columns=('name','size','chars','status'),
                                 show='tree headings',
                                 yscrollcommand=vs.set, xscrollcommand=hs.set, height=6)
        vs.config(command=self.tree.yview)
        hs.config(command=self.tree.xview)

        self.tree.column('#0', width=0, stretch=False)
        self.tree.column('name', width=350, minwidth=150)
        self.tree.column('size', width=80, minwidth=60, anchor=tk.E)
        self.tree.column('chars', width=60, minwidth=50, anchor=tk.E)
        self.tree.column('status', width=70, minwidth=60, anchor=tk.CENTER)
        for col, txt in [('name','Name'),('size','Size'),('chars','Chars'),('status','Status')]:
            self.tree.heading(col, text=txt, anchor=tk.W if col=='name' else tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vs.pack(side=tk.RIGHT, fill=tk.Y)
        hs.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.tag_configure('ok', foreground=self.COLORS['text'])
        self.tree.tag_configure('skip', foreground=self.COLORS['text_secondary'])
        self.tree.tag_configure('even', background='#fafafa')
        self.tree.tag_configure('odd', background='#ffffff')
        self.tree.tag_configure('matched', background='#fff3cd')  # highlight matches in yellow

        # Double-click to open file in system editor
        self.tree.bind('<Double-1>', self._on_tree_double_click)
        # Also bind Enter key on selection
        self.tree.bind('<Return>', self._on_tree_double_click)
        # Update hint when mode changes
        self._update_search_hint()

    def build_settings(self):
        self.set_f = tk.Frame(self.main, bg=self.COLORS['card'],
                              highlightbackground=self.COLORS['border'],
                              highlightthickness=1, padx=10, pady=8)
        self.set_f.pack(fill=tk.X, pady=(0, 6))

        # Mode row
        mode_f = tk.Frame(self.set_f, bg=self.COLORS['card'])
        mode_f.pack(fill=tk.X, pady=(0, 4))
        tk.Label(mode_f, text=self.tr('mode_label'), font=('Segoe UI', 10),
                 bg=self.COLORS['card'], fg=self.COLORS['text']).pack(side=tk.LEFT)

        self.mode_var = tk.StringVar(value='single')

        for val, txt in [('single', self.tr('single')), ('chunked', self.tr('chunked_mode')), ('portal', self.tr('portal_mode'))]:
            rb = tk.Radiobutton(mode_f, text=txt, variable=self.mode_var, value=val,
                                command=self.on_mode_change, font=('Segoe UI', 10),
                                bg=self.COLORS['card'], selectcolor=self.COLORS['card'])
            rb.pack(side=tk.LEFT, padx=(8, 0))

        ps = self.tr('ready') if HAS_PORTAL else self.tr('unavail')
        pc = self.COLORS['success'] if HAS_PORTAL else self.COLORS['warning']
        tk.Label(mode_f, text=f"({ps})", font=('Segoe UI', 9),
                 bg=self.COLORS['card'], fg=pc).pack(side=tk.LEFT, padx=(6, 0))

        sep = tk.Frame(self.set_f, bg=self.COLORS['border'], height=1)
        sep.pack(fill=tk.X, pady=(4, 6))

        # Single-mode settings
        self.single_f = tk.Frame(self.set_f, bg=self.COLORS['card'])
        self.single_f.pack(fill=tk.X)

        r1 = tk.Frame(self.single_f, bg=self.COLORS['card'])
        r1.pack(fill=tk.X, pady=1)
        tk.Label(r1, text=self.tr('output'), font=('Segoe UI', 10),
                 bg=self.COLORS['card'], fg=self.COLORS['text']).pack(side=tk.LEFT)
        self.out_var = tk.StringVar(value=self.output_path)
        ttk.Entry(r1, textvariable=self.out_var, font=('Segoe UI', 9)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))
        out_btn = tk.Button(r1, text=self.tr('browse'), font=('Segoe UI', 9),
                            bg=self.COLORS['primary'], fg='white', relief='flat',
                            cursor='hand2', command=self.browse_txt_output, padx=10)
        out_btn.pack(side=tk.LEFT)
        out_btn.bind('<Enter>', lambda e: out_btn.configure(bg=self.COLORS['primary_hover']))
        out_btn.bind('<Leave>', lambda e: out_btn.configure(bg=self.COLORS['primary']))

        r2 = tk.Frame(self.single_f, bg=self.COLORS['card'])
        r2.pack(fill=tk.X, pady=1)

        # Note: max_chars per-file truncation has been REMOVED in traditional TXT mode.
        # For size-controlled splitting, use the --split-chunks CLI mode.

        tk.Label(r2, text=self.tr('fname'), font=('Segoe UI', 10),
                 bg=self.COLORS['card'], fg=self.COLORS['text']).pack(side=tk.LEFT)
        self.fname_var = tk.StringVar(value='knowledge_export')
        ttk.Entry(r2, textvariable=self.fname_var, width=16).pack(side=tk.LEFT, padx=(4, 2))
        tk.Label(r2, text='.txt', font=('Segoe UI', 10, 'bold'),
                 bg=self.COLORS['card'], fg=self.COLORS['primary']).pack(side=tk.LEFT)
        self.fname_var.trace_add('write', lambda *a: self.update_out_path())

        self.skip_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.single_f, text=self.tr('show_skip'),
                       variable=self.skip_var, font=('Segoe UI', 10),
                       bg=self.COLORS['card'], selectcolor=self.COLORS['card']).pack(anchor=tk.W, pady=(2, 0))

        # Chunked mode settings (hidden by default)
        self.chunked_f = tk.Frame(self.set_f, bg=self.COLORS['card'])
        cr1 = tk.Frame(self.chunked_f, bg=self.COLORS['card'])
        cr1.pack(fill=tk.X, pady=1)
        tk.Label(cr1, text=self.tr('out_dir'), font=('Segoe UI', 10),
                 bg=self.COLORS['card'], fg=self.COLORS['text']).pack(side=tk.LEFT)
        self.chunk_out_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Desktop", "knowledge_chunked"))
        ttk.Entry(cr1, textvariable=self.chunk_out_var, font=('Segoe UI', 9)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))
        chunk_out_btn = tk.Button(cr1, text=self.tr('browse'), font=('Segoe UI', 9),
                                  bg=self.COLORS['primary'], fg='white', relief='flat',
                                  cursor='hand2', command=self.browse_chunked_out, padx=10)
        chunk_out_btn.pack(side=tk.LEFT)
        chunk_out_btn.bind('<Enter>', lambda e: chunk_out_btn.configure(bg=self.COLORS['primary_hover']))
        chunk_out_btn.bind('<Leave>', lambda e: chunk_out_btn.configure(bg=self.COLORS['primary']))

        cr2 = tk.Frame(self.chunked_f, bg=self.COLORS['card'])
        cr2.pack(fill=tk.X, pady=1)
        tk.Label(cr2, text=self.tr('chunk_size_label'), font=('Segoe UI', 10),
                 bg=self.COLORS['card'], fg=self.COLORS['text']).pack(side=tk.LEFT)
        self.chunk_size_var = tk.StringVar(value='500000')
        ttk.Entry(cr2, textvariable=self.chunk_size_var, width=12).pack(side=tk.LEFT, padx=(4, 8))
        tk.Label(cr2, text=self.tr('chunk_chars'), font=('Segoe UI', 10),
                 bg=self.COLORS['card'], fg=self.COLORS['text_secondary']).pack(side=tk.LEFT)

        self.force_split_var = tk.BooleanVar(value=False)
        tk.Checkbutton(self.chunked_f, text=self.tr('force_split'),
                       variable=self.force_split_var, font=('Segoe UI', 10),
                       bg=self.COLORS['card'], selectcolor=self.COLORS['card']).pack(anchor=tk.W, pady=(2, 0))

        # Portal settings (hidden by default)
        # Only output dir + port — no pagination settings
        self.portal_f = tk.Frame(self.set_f, bg=self.COLORS['card'])
        pr1 = tk.Frame(self.portal_f, bg=self.COLORS['card'])
        pr1.pack(fill=tk.X, pady=1)
        tk.Label(pr1, text=self.tr('out_dir'), font=('Segoe UI', 10),
                 bg=self.COLORS['card'], fg=self.COLORS['text']).pack(side=tk.LEFT)
        self.pout_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Desktop", "knowledge_portal"))
        ttk.Entry(pr1, textvariable=self.pout_var, font=('Segoe UI', 9)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))
        pout_btn = tk.Button(pr1, text=self.tr('browse'), font=('Segoe UI', 9),
                             bg=self.COLORS['primary'], fg='white', relief='flat',
                             cursor='hand2', command=self.browse_portal_out, padx=10)
        pout_btn.pack(side=tk.LEFT)
        pout_btn.bind('<Enter>', lambda e: pout_btn.configure(bg=self.COLORS['primary_hover']))
        pout_btn.bind('<Leave>', lambda e: pout_btn.configure(bg=self.COLORS['primary']))

        pr2 = tk.Frame(self.portal_f, bg=self.COLORS['card'])
        pr2.pack(fill=tk.X, pady=1)

        # Port input only
        tk.Label(pr2, text=self.tr('port_label'), font=('Segoe UI', 10),
                 bg=self.COLORS['card'], fg=self.COLORS['text']).pack(side=tk.LEFT)
        self.port_var = tk.StringVar(value=str(self._server_port))
        port_entry = ttk.Entry(pr2, textvariable=self.port_var, width=8)
        port_entry.pack(side=tk.LEFT, padx=(4, 8))
        port_entry.bind('<FocusOut>', lambda e: self._save_port())

        tk.Checkbutton(self.portal_f, text=self.tr('show_skip'),
                       variable=self.skip_var, font=('Segoe UI', 10),
                       bg=self.COLORS['card'], selectcolor=self.COLORS['card']).pack(anchor=tk.W, pady=(2, 0))

    def browse_output(self):
        fp = filedialog.asksaveasfilename(title="Save TXT", defaultextension=".txt",
                                           filetypes=[("Text files","*.txt"),("All files","*.*")],
                                           initialfile=self.fname_var.get()+".txt")
        if fp:
            self.out_var.set(fp)
            self.fname_var.set(os.path.splitext(os.path.basename(fp))[0])

    def browse_txt_output(self):
        fp = filedialog.asksaveasfilename(title="Save TXT", defaultextension=".txt",
                                           filetypes=[("Text files","*.txt"),("All files","*.*")],
                                           initialfile=self.fname_var.get()+".txt")
        if fp:
            self.out_var.set(fp)
            self.fname_var.set(os.path.splitext(os.path.basename(fp))[0])

    def _save_port(self):
        """Save port from entry widget."""
        try:
            self._server_port = int(self.port_var.get().strip())
        except (ValueError, AttributeError):
            pass

    def build_server_controls(self):
        """Build HTTP server control bar (hidden until portal generated)."""
        self.server_f = tk.Frame(self.main, bg=self.COLORS['card'],
                                 highlightbackground=self.COLORS['border'],
                                 highlightthickness=1, padx=10, pady=6)
        self.server_f.pack(fill=tk.X, pady=(0, 6))

        self.server_status_lbl = tk.Label(
            self.server_f,
            text=self.tr('status_ready'),
            font=('Segoe UI', 10),
            bg=self.COLORS['card'],
            fg=self.COLORS['text_secondary']
        )
        self.server_status_lbl.pack(side=tk.LEFT, padx=(0, 8))

        self.server_start_btn = tk.Button(
            self.server_f,
            text=f"▶ {self.tr('server_start')}",
            font=('Segoe UI', 9),
            bg=self.COLORS['primary'],
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self._on_server_start,
            padx=10, pady=2
        )
        self.server_start_btn.pack(side=tk.LEFT, padx=2)
        self.server_start_btn.bind('<Enter>', lambda e: self.server_start_btn.configure(bg=self.COLORS['primary_hover']))
        self.server_start_btn.bind('<Leave>', lambda e: self.server_start_btn.configure(bg=self.COLORS['primary']))

        self.server_stop_btn = tk.Button(
            self.server_f,
            text=f"⏹ {self.tr('server_stop')}",
            font=('Segoe UI', 9),
            bg=self.COLORS['error'],
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self._stop_server,
            padx=10, pady=2
        )
        self.server_stop_btn.pack_forget()
        self.server_stop_btn.bind('<Enter>', lambda e: self.server_stop_btn.configure(bg='#d32f2f'))
        self.server_stop_btn.bind('<Leave>', lambda e: self.server_stop_btn.configure(bg=self.COLORS['error']))

        self.server_copy_btn = tk.Button(
            self.server_f,
            text=f"📋 {self.tr('copy_url')}",
            font=('Segoe UI', 9),
            bg=self.COLORS['primary'],
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self._copy_server_url,
            padx=10, pady=2
        )
        self.server_copy_btn.pack_forget()
        self.server_copy_btn.bind('<Enter>', lambda e: self.server_copy_btn.configure(bg=self.COLORS['primary_hover']))
        self.server_copy_btn.bind('<Leave>', lambda e: self.server_copy_btn.configure(bg=self.COLORS['primary']))

        self._update_server_ui()

    def _on_server_start(self):
        """Handle start server button click."""
        if not self._server_root or not os.path.isdir(self._server_root):
            self.status_var.set("No portal output directory to serve. Generate a portal first.")
            return
        self._save_port()
        if self._start_server(self._server_root, port=self._server_port):
            self.status_var.set(f"🟢 Server started at http://localhost:{self._server_port}")
        else:
            self.status_var.set("❌ Failed to start server")

    def build_gen_section(self):
        gen_f = tk.Frame(self.main, bg=self.COLORS['bg'])
        gen_f.pack(fill=tk.X)

        self.gen_btn = tk.Button(gen_f, text=self.tr('gen_btn'),
                                 font=('Segoe UI', 14, 'bold'),
                                 bg=self.COLORS['primary'], fg='white', relief='flat',
                                 cursor='hand2', command=self.generate, padx=40, pady=10,
                                 state='disabled')
        self.gen_btn.pack(pady=(0, 4))
        self.gen_btn.bind('<Enter>', lambda e: self._btn_hover(True))
        self.gen_btn.bind('<Leave>', lambda e: self._btn_hover(False))

        self.prog = ttk.Progressbar(gen_f, mode='determinate', length=400)
        self.prog.pack_forget()

        # Status bar
        st_f = tk.Frame(self.main, bg=self.COLORS['bg'], height=24)
        st_f.pack(fill=tk.X)
        st_f.pack_propagate(False)

        self.dot = tk.Canvas(st_f, width=8, height=8, bg=self.COLORS['bg'], highlightthickness=0)
        self.dot.pack(side=tk.LEFT, padx=(0, 4))
        self.dot.create_oval(0, 0, 8, 8, fill=self.COLORS['text_secondary'], outline='')

        self.status_var = tk.StringVar(value=self.tr('start_hint'))
        tk.Label(st_f, textvariable=self.status_var, font=('Segoe UI', 9),
                 bg=self.COLORS['bg'], fg=self.COLORS['text_secondary'],
                 anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.footer_var = tk.StringVar(value=self.tr('status_ready'))
        tk.Label(st_f, textvariable=self.footer_var, font=('Segoe UI', 9),
                 bg=self.COLORS['bg'], fg=self.COLORS['text_secondary'],
                 anchor=tk.E).pack(side=tk.RIGHT)

    def _btn_hover(self, enter):
        if not self.generating:
            self.gen_btn.configure(bg=self.COLORS['primary_hover'] if enter else self.COLORS['primary'])

    def bind_shortcuts(self):
        self.root.bind('<Control-o>', lambda e: self.browse_folder())
        self.root.bind('<Control-g>', lambda e: self.generate())
        self.root.bind('<Control-v>', lambda e: self.paste_folder())
        self.root.bind('<Escape>', lambda e: self.root.quit() if not self.generating else None)

    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ── Folder operations ──

    def load_from_path(self):
        path = self.path_var.get().strip().strip('"')
        if os.path.isdir(path):
            self.load_folder(path)
        else:
            self.status_var.set(f"Invalid path: {path}")

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select a folder")
        if folder:
            self.path_var.set(folder)
            self.load_folder(folder)

    def clear_folder(self):
        self.current_folder = None
        self.file_list = []
        self.total_size = 0
        self.path_var.set('')
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.gen_btn.config(state='disabled')
        self.stats_lbl.config(text=self.tr('no_folder'))
        self.status_var.set(self.tr('start_hint'))
        self.footer_var.set(self.tr('status_ready'))
        self.dot.delete('all')
        self.dot.create_oval(0, 0, 8, 8, fill=self.COLORS['text_secondary'], outline='')
        self.fname_var.set('knowledge_export')

    def paste_folder(self):
        try:
            path = self.root.clipboard_get().strip().strip('"')
            if os.path.isdir(path):
                self.path_var.set(path)
                self.load_folder(path)
                self.status_var.set(self.tr('paste_done'))
            else:
                self.status_var.set(self.tr('clip_empty'))
        except Exception:
            self.status_var.set(self.tr('clip_empty'))

    def load_folder(self, folder_path):
        if self.generating:
            return
        self.current_folder = folder_path
        self.status_var.set(f"{self.tr('scanning')} {folder_path}")
        self.root.update_idletasks()

        def scan():
            fl, ts = collect_files_info(folder_path)
            self.root.after(0, lambda: self._on_scanned(fl, ts))
        threading.Thread(target=scan, daemon=True).start()

    def _on_scanned(self, file_list, total_size):
        self.file_list = file_list
        self.total_size = total_size
        supported = sum(1 for f in file_list if f['supported'])
        self.stats_lbl.config(text=f"{len(file_list)} {self.tr('files')} | {supported} {self.tr('supported')} | {human_readable_size(total_size)}")
        self._update_tree()

        if file_list:
            self.gen_btn.config(state='normal')
            self.status_var.set(f"{len(file_list)} {self.tr('files')}, {supported} {self.tr('parseable')}")
            self.dot.delete('all')
            self.dot.create_oval(0, 0, 8, 8, fill=self.COLORS['success'], outline='')
        else:
            self.gen_btn.config(state='disabled')
            self.status_var.set(self.tr('empty'))
            self.dot.delete('all')
            self.dot.create_oval(0, 0, 8, 8, fill=self.COLORS['warning'], outline='')

        self.fname_var.set(f"{os.path.basename(os.path.normpath(self.current_folder))}_export")

    def _update_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        sc = 0
        for i, f in enumerate(self.file_list):
            icon = '\U0001f4c4' if f['supported'] else '\u23ed\ufe0f'
            status = 'OK' if f['supported'] else 'Skip'
            tag = ('ok' if f['supported'] else 'skip', 'even' if i % 2 == 0 else 'odd')
            self.tree.insert('', 'end', values=(f"{icon} {f['rel_path']}", f['size_hr'], '-', status), tags=tag)
            if f['supported']:
                sc += 1
        self.footer_var.set(f"{len(self.file_list)} {self.tr('files')} | {sc} {self.tr('parseable')}")

    def on_mode_change(self):
        mode = self.mode_var.get()
        is_portal = mode == 'portal'
        is_chunked = mode == 'chunked'
        self.single_f.pack_forget()
        self.portal_f.pack_forget()
        self.chunked_f.pack_forget()
        if is_portal:
            self.portal_f.pack(fill=tk.X)
            self.gen_btn.config(text=self.tr('gen_portal_btn'))
            self.status_var.set("Portal: split mode — each file gets its own HTML subpage, index page with tree + search" if self._lang == 'en' else "门户模式：拆分模式 — 每个文件独立子页面，索引页显示文件树和搜索")
        elif is_chunked:
            self.chunked_f.pack(fill=tk.X)
            self.gen_btn.config(text='Generate Split TXT')
            self.status_var.set("Split TXT: break large output into multiple part_*.txt files" if self._lang == 'en' else "分片模式：将大输出拆分为多个 part_*.txt 文件")
        else:
            self.single_f.pack(fill=tk.X)
            self.gen_btn.config(text=self.tr('gen_btn'))
            self.status_var.set("Single TXT: all in one file" if self._lang == 'en' else "单文件 TXT 模式：所有文档合并为一个文件")

    def browse_portal_out(self):
        f = filedialog.askdirectory(title="Output directory")
        if f:
            self.pout_var.set(f)

    def browse_chunked_out(self):
        f = filedialog.askdirectory(title="Output directory for chunked files")
        if f:
            self.chunk_out_var.set(f)

    def update_out_path(self):
        name = self.fname_var.get().strip()
        if name:
            cur = self.out_var.get()
            d = os.path.dirname(cur) if os.path.dirname(cur) else os.path.join(os.path.expanduser("~"), "Desktop")
            self.out_var.set(os.path.join(d, f"{name}.txt"))

    def generate(self):
        if self.generating or not self.current_folder or not self.file_list:
            return

        # Save port before generation starts
        self._save_port()

        mode = self.mode_var.get()
        is_portal = mode == 'portal'
        is_chunked = mode == 'chunked'
        skip = self.skip_var.get()

        if is_chunked:
            # ---- Chunked/Split TXT mode ----
            try:
                from src.chunker import write_chunks, DEFAULT_CHUNK_SIZE
            except ImportError:
                messagebox.showerror("Error", "Chunked output module (src/chunker) not available")
                return

            out_dir = self.chunk_out_var.get().strip()
            if not out_dir:
                messagebox.showerror("Error", "Set output directory for chunked files")
                return

            try:
                chunk_size = int(self.chunk_size_var.get().strip())
                if chunk_size < 10000:
                    messagebox.showerror("Error", "Chunk size must be at least 10,000")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid chunk size")
                return

            force_split = self.force_split_var.get()

            self._start_gen("Generating split TXT files..." if self._lang == 'en' else "正在生成分片 TXT...")

            def task():
                try:
                    result = write_chunks(
                        folder_path=self.current_folder,
                        output_dir=out_dir,
                        chunk_size=chunk_size,
                        force_split=force_split,
                    )
                    self.root.after(0, lambda: self._chunked_done(result))
                except Exception as e:
                    self.root.after(0, lambda e=e: self._gen_err(str(e)))

            threading.Thread(target=task, daemon=True).start()
            self._sim_progress()
            return

        if is_portal:
            if not HAS_PORTAL:
                messagebox.showerror("Error", "Portal module unavailable")
                return
            out_dir = self.pout_var.get().strip()
            if not out_dir:
                messagebox.showerror("Error", "Set output directory")
                return
            self._start_gen("Generating portal..." if self._lang == 'en' else "正在生成门户...")

            def task():
                try:
                    r = generate_portal_split(
                        folder_path=self.current_folder,
                        output_dir=out_dir,
                        include_skipped=skip,
                        language=self._lang,
                    )
                    self._server_root = r.get("output_dir", out_dir)
                    self.root.after(0, lambda: self._portal_done(r))
                except Exception as e2:
                    self.root.after(0, lambda e2=e2: self._gen_err(str(e2)))

            threading.Thread(target=task, daemon=True).start()
            self._sim_progress()
            return

        # ---- Single TXT mode ----
        out = self.out_var.get().strip()
        if not out:
            messagebox.showerror("Error", "Set output path")
            return
        # Ensure .txt extension
        if not out.lower().endswith('.txt'):
            out += '.txt'
            self.out_var.set(out)
        # NOTE: max_chars truncation has been REMOVED.
        # TXT mode always outputs complete file content.
        # For size-controlled splitting, use the --split-chunks CLI option.
        self._start_gen("Generating TXT..." if self._lang == 'en' else "正在生成 TXT...")

        def task():
            try:
                # Note: build_text_from_files no longer supports max_chars truncation.
                # For size-controlled splitting, use --split-chunks CLI mode.
                text, parsed, skipped, errors, chars = build_text_from_files(
                    self.current_folder, self.file_list,
                    include_skipped=skip)
                with open(out, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.root.after(0, lambda: self.prog.config(value=100))
                self.root.after(0, lambda: self._gen_done(out, parsed, skipped, errors, chars))
            except Exception as e2:
                self.root.after(0, lambda e2=e2: self._gen_err(str(e2)))

        threading.Thread(target=task, daemon=True).start()
        self._sim_progress()

    def _start_gen(self, msg):
        self.generating = True
        self.gen_btn.config(state='disabled', text=msg, bg='#999')
        self.prog['value'] = 0
        self.prog.pack(pady=(4, 0))
        self.status_var.set(msg)
        self.dot.delete('all')
        self.dot.create_oval(0, 0, 8, 8, fill=self.COLORS['warning'], outline='')

    def _sim_progress(self):
        if self.generating:
            v = self.prog['value']
            if v < 90:
                self.prog['value'] = min(v + 5, 90)
                self.root.after(300, self._sim_progress)

    def _gen_done(self, out_path, parsed, skipped, errors, chars):
        self.generating = False
        self.prog['value'] = 100
        fs = os.path.getsize(out_path) if os.path.exists(out_path) else 0
        self.gen_btn.config(state='normal', text=self.tr('gen_btn'), bg=self.COLORS['primary'])
        st = (f"{self.tr('gen_done')} {parsed} files" + (f", {skipped} skipped" if skipped else "") +
              (f", {errors} errors" if errors else "") + f" | {chars:,} chars | {human_readable_size(fs)}")
        self.status_var.set(st)
        # Print hint about --split-chunks for large folders
        print(f"[Hint] Single TXT file generated. If this file is too large for AI context, use:\n"
              f"       python generate.py \"{self.current_folder}\" --split-chunks --chunk-size 500000 -o <output_dir>\n")
        self.footer_var.set(f"OK {os.path.basename(out_path)}")
        self.dot.delete('all')
        self.dot.create_oval(0, 0, 8, 8, fill=self.COLORS['success'], outline='')
        if messagebox.askyesno("Success", f"TXT generated!\n\nOutput: {out_path}\nParsed: {parsed}\nSkipped: {skipped}\nErrors: {errors}\nChars: {chars:,}\nSize: {human_readable_size(fs)}\n\n{self.tr('open_folder')}"):
            self._open_folder(out_path)

    def _chunked_done(self, result):
        self.generating = False
        self.prog['value'] = 100
        cc = result["chunks_count"]
        tc = result["total_chars"]
        tf = result["total_files"]
        od = result["output_dir"]
        idx = result.get("index_file", "")
        self.gen_btn.config(state='normal', text='Generate Split TXT', bg=self.COLORS['primary'])
        st = f"Split TXT generated: {cc} chunks, {tf} files, {tc:,} chars"
        self.status_var.set(st)
        self.footer_var.set(f"OK {cc} chunks")
        self.dot.delete('all')
        self.dot.create_oval(0, 0, 8, 8, fill=self.COLORS['success'], outline='')
        msg = (
            f"Split TXT generated successfully!\n\n"
            f"Output: {od}\n"
            f"Chunks: {cc}\n"
            f"Files: {tf}\n"
            f"Total chars: {tc:,}\n\n"
        )
        if messagebox.askyesno("Success", msg + "Open output folder?"):
            try:
                if sys.platform == 'win32':
                    os.startfile(od)
            except:
                pass

    def _portal_done(self, result):
        self.generating = False
        self.prog['value'] = 100
        dc, tc = result["doc_count"], result["total_chars"]
        od, idx = result["output_dir"], result.get("index_file", "")
        sk, er = result.get("skipped", 0), result.get("errors", 0)
        self.gen_btn.config(state='normal', text=self.tr('gen_portal_btn'), bg=self.COLORS['primary'])
        st = (f"{self.tr('portal_done')} {dc} files" + (f", {sk} skipped" if sk else "") +
              (f", {er} errors" if er else "") + f" | {tc:,} chars")
        self.status_var.set(st)
        self.footer_var.set(f"OK {os.path.basename(od)}")
        self.dot.delete('all')
        self.dot.create_oval(0, 0, 8, 8, fill=self.COLORS['success'], outline='')
        hi = idx and os.path.exists(idx)
        msg = f"Portal generated!\n\nOutput: {od}\nFiles: {dc}\nSkipped: {sk}\nErrors: {er}\nChars: {tc:,}\n\n"

        if hi:
            ask_msg = msg + self.tr('server_ask')
            if messagebox.askyesno("Success", ask_msg):
                if self._start_server(od, port=self._server_port):
                    self.status_var.set(f"🟢 {self.tr('server_running')} http://localhost:{self._server_port}")
                else:
                    self.status_var.set("❌ Failed to start server")
            else:
                if messagebox.askyesno("Success", msg + self.tr('open_folder')):
                    self._open_folder(idx)
        else:
            messagebox.showinfo("Done", msg + "No pages generated")

    # ── File tree search and open ──

    def _update_search_hint(self):
        """Update the search mode hint label."""
        mode = self.search_mode_var.get()
        if self._lang == 'zh':
            hint = '搜索文件名' if mode == 'name' else '搜索代码内容'
        else:
            hint = 'Search file names' if mode == 'name' else 'Search code content'
        self.search_hint_lbl.config(text=hint)

    def _build_content_search_index(self):
        """Build a dict mapping file index -> lowercase content for code searching."""
        idx = {}
        for i, f in enumerate(self.file_list):
            if not f['supported']:
                continue
            try:
                from src.parser.dispatcher import parse_file
                result = parse_file(f['path'])
                if result:
                    text = (result.get("text") or "").strip()
                    if text:
                        idx[i] = text.lower()
            except Exception:
                pass
        return idx

    _content_search_index = {}  # Class-level cache for content search

    def _filter_file_tree(self):
        """Filter the file tree based on search query."""
        query = self.search_var.get().strip().lower()
        mode = self.search_mode_var.get()

        # No items in tree
        if not self.tree.get_children():
            return

        if not query:
            # Show all items
            total = 0
            for item in self.tree.get_children():
                self.tree.item(item, tags=())  # Remove matched tag
                total += 1
            self.footer_var.set(f"{total} {self.tr('files')}")
            self.stats_lbl.config(text=f"{len(self.file_list)} {self.tr('files')} | {sum(1 for f in self.file_list if f['supported'])} {self.tr('supported')} | {human_readable_size(self.total_size)}")
            return

        if mode == 'code' and not self._content_search_index:
            # Build content search index in background
            self.status_var.set("Building content search index..." if self._lang == 'en' else "正在构建内容搜索索引...")
            self.root.update_idletasks()
            self._content_search_index = self._build_content_search_index()
            self.status_var.set("Search ready" if self._lang == 'en' else "搜索就绪")

        matched_count = 0
        for i, item in enumerate(self.tree.get_children()):
            values = self.tree.item(item, 'values')
            if not values:
                continue
            file_name = values[0] if values else ''
            # Remove icon prefix for matching
            clean_name = file_name.replace('\U0001f4c4', '').replace('\u23ed\ufe0f', '').strip()

            if mode == 'name':
                # Match file name only
                match = query in clean_name.lower()
            else:
                # Match file name OR content
                match = query in clean_name.lower()
                if not match and i in self._content_search_index:
                    match = query in self._content_search_index[i]

            if match:
                self.tree.item(item, tags=('matched',))
                self.tree.move(item, '', len(self.tree.get_children()) - len(self.tree.selection()))  # keep order
                matched_count += 1
            else:
                self.tree.item(item, tags=())

        # Update footer with match count
        self.footer_var.set(f"{matched_count}/{len(self.tree.get_children())} matched")
        if self._lang == 'zh':
            st = f"找到 {matched_count} 个匹配文件"
        else:
            st = f"Found {matched_count} matching files"
        self.status_var.set(st)

    def _on_tree_double_click(self, event):
        """Handle double-click or Enter on a tree item: open file in system editor."""
        selection = self.tree.selection()
        if not selection:
            return
        item = selection[0]
        values = self.tree.item(item, 'values')
        if not values:
            return
        file_name = values[0] if values else ''
        # Remove icon prefix
        clean_name = file_name.replace('\U0001f4c4', '').replace('\u23ed\ufe0f', '').strip()

        # Find the matching file in file_list
        for f in self.file_list:
            if f['rel_path'] == clean_name:
                full_path = f['path']
                if os.path.isfile(full_path):
                    try:
                        if sys.platform == 'win32':
                            os.startfile(full_path)
                        elif sys.platform == 'darwin':
                            import subprocess
                            subprocess.run(['open', full_path])
                        else:
                            import subprocess
                            subprocess.run(['xdg-open', full_path])
                        return
                    except Exception as e:
                        logger.warning("Failed to open file: %s", e)
                        messagebox.showerror("Error", f"Failed to open: {clean_name}\n{e}")
                        return

        # File not found in list (shouldn't happen)
        messagebox.showerror("Error", f"File not found: {clean_name}")

    def _gen_err(self, msg):
        self.generating = False
        self.prog['value'] = 0
        self.prog.pack_forget()
        self.gen_btn.config(state='normal', text=self.tr('gen_btn'), bg=self.COLORS['primary'])
        self.status_var.set("Failed: " + msg)
        self.dot.delete('all')
        self.dot.create_oval(0, 0, 8, 8, fill=self.COLORS['error'], outline='')
        messagebox.showerror("Error", msg)

    def _open_folder(self, path):
        try:
            if sys.platform == 'win32':
                os.startfile(os.path.dirname(path))
        except:
            pass


def main():
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
    except ImportError:
        root = tk.Tk()
    app = FolderKnowledgeSiteGeneratorForAIUI(root)
    if len(sys.argv) > 1:
        f = sys.argv[1]
        if os.path.isdir(f):
            root.after(100, lambda: app.load_folder(f))
    root.mainloop()


if __name__ == "__main__":
    main()