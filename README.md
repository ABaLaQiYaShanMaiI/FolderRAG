> ⚠️ **重要提示 / Important Note**  
> **此项目为所有 AI 场景设计 —— 无论是粘贴到对话窗口，还是让网页 AI 直接读取**  
> **This project is designed for all AI scenarios — paste into chat windows or let browser AI read natively**  
>
> - **TXT 模式**：纯文本输出，可直接粘贴到 Claude、ChatGPT、DeepSeek 等任意对话窗口  
> - **Portal 模式**：单页 HTML，Edge Copilot、ChatGPT Web 等浏览器 AI 可直接读取和分析  
> 无需插件、文件上传或 API 调用。  
>  
> - **TXT Mode**: Plain text output, ready to paste into any LLM chat (Claude, ChatGPT, DeepSeek, etc.)  
> - **Portal Mode**: Single-page HTML, directly readable by browser-based AI (Edge Copilot, ChatGPT Web, etc.)  
> No plugins, file uploads, or API calls required.

---

# FolderKnowledgeSiteGeneratorForAI 📁 → 🌐

[![PyPI Version](https://img.shields.io/badge/pypi-v2.0.0-blue)](https://pypi.org/project/FolderKnowledgeSiteGeneratorForAI/)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-129%20passed-brightgreen)](tests/)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-7B3F00)](pyproject.toml)

> **将任意文件夹一键变为 AI 可读的知识门户（单页 HTML 或纯文本），无需服务器与 API。**

---

## 🧠 核心理念 / Core Philosophy

**零依赖 · 零后端 · 零模型** —— 不运行 AI 模型、不调用 API、不启动后台服务。

**两种消费方式 / Two Consumption Modes：**

| 模式 | 输出 | 适用场景 |
|------|------|----------|
| 🗂️ **TXT 模式** | 纯文本（`.txt`） | 直接粘贴到 ChatGPT、DeepSeek、Claude 等对话窗口 |
| 🏛️ **Portal 模式** | 单页 HTML（`.html`） | 浏览器本地打开，Edge Copilot / ChatGPT Web 等直接读取 |

---

## 🚀 快速开始 / Quick Start

### 环境要求 / Requirements

- Python **3.8** 及以上

### 安装依赖 / Install Dependencies

```bash
pip install -r requirements.txt
```

### 一行命令启动 / One-command Launch

```bash
# 🖥️ 图形界面（推荐 Windows）/ GUI (recommended for Windows)
python gui.py [文件夹路径]

# ⌨️ 命令行 / CLI
python generate.py my_folder -o out.txt                # TXT 导出
python generate.py my_folder --portal -o out_dir       # 门户模式
```

> 🪟 **Windows 用户**：也可直接双击 `start.cmd` 一键启动图形界面。  
> 🐧 **Linux/macOS 用户**：运行 `bash start.sh`。

---

## 📊 输出模式对比表 / Output Mode Comparison

| 模式 | 命令参数 | 输出格式 | 适用场景 |
|------|---------|---------|----------|
| 🗂️ **TXT 导出** | 默认（`-o out.txt`） | 纯文本，每个文件用分隔线隔开 | 复制到 ChatGPT、DeepSeek 等对话 |
| 🏛️ **知识门户** | `--portal -o out_dir` | 单页 HTML（含搜索、文件树、可折叠代码块） | Edge Copilot 等浏览器 AI 直接阅读 |

---

## 🏛️ 门户 HTML 功能详解 / Portal HTML Features

| 功能 | 说明 |
|------|------|
| 📄 **可折叠文件块** | 每个文件一个块，默认折叠，点击头部或 ▶ 展开/收起 |
| 🤖 **Expand All (AI Mode)** | 一键展开所有文件内容，方便 AI 一次性读取 |
| 📁 **Collapse All** | 一键收起所有文件块，快速恢复默认状态 |
| 🔍 **实时搜索** | 搜索文件名、标签、代码内容，文件树同步高亮 |
| 🗂️ **文件树导航** | ASCII 风格连接线，点击文件名自动跳转并展开对应块 |
| 🏷️ **关键词云** | 自动提取关键词，点击标签快速过滤文件 |
| 🌐 **中英双语** | 页面右上角切换，语言偏好保存到 localStorage |
| 🌙 **暗黑模式** | 自动跟随系统颜色方案 |
| 🖨️ **打印友好** | 打印时自动展开所有内容 |
| 🖱️ **搜索高亮** | 文件树中匹配的文件保持高亮，不匹配的半透明显示 |

---

## 🖥️ 图形界面 (GUI) / Graphical Interface

| 功能 | 说明 |
|------|------|
| 📂 **文件夹选择** | 浏览、粘贴或拖拽选择文件夹，快捷键 `Ctrl+O` |
| 🔄 **模式切换** | 传统模式 / 门户模式，切换时自动调整 UI 设置项 |
| 🚀 **一键生成** | 点击生成按钮，进度条实时反馈，快捷键 `Ctrl+G` |
| 🌐 **中英双语** | 界面右上角 EN/中文 按钮即时切换，偏好自动保存 |
| 📋 **实时文件列表** | 扫描后显示所有文件及其大小、状态（支持/跳过） |
| 🧹 **Clear 按钮** | 一键清空当前文件夹加载状态 |
| ▶️ **HTTP 服务器** | 门户生成后可直接启动本地服务器供 AI 读取 |
| 📂 **拖拽支持** | 支持文件夹拖入 GUI（需 tkinterdnd2） |

---

## 📦 支持的格式 / Supported Formats

| 类别 | 格式 | 解析方式 |
|------|------|---------|
| 纯文本 / 标记 | `.txt`, `.md`, `.html`, `.json`, `.xml`, `.csv`, `.yaml`, `.toml`, `.ini`, `.cfg` 等 | 自动编码检测（UTF-8/GBK/Latin-1） |
| Office 文档 | `.docx`, `.pptx`, `.xlsx` | `python-docx`, `python-pptx`, `openpyxl` |
| PDF | `.pdf` | `pdfminer.six` |
| 代码文件 | `.py`, `.js`, `.ts`, `.java`, `.cs`, `.swift`, `.kt`, `.rs`, `.cpp`, `.h`, `.go`, `.rb` 等 50+ 种 | 文本读取，依靠 `python-magic` + 扩展名回退 |
| 自动跳过 | `.exe`, `.dll`, `.zip`, `.jpg`, `.png`, `.mp4`, `.log`, `.lock`, `__pycache__` 等 | 内置过滤规则，无需手动排除 |

> **旧版 Office 格式（.doc / .ppt / .xls）**：请先用 Office 或 WPS 另存为 `.docx` / `.pptx` / `.xlsx`。

---

## ⌨️ 完整 CLI 参数说明 / Full CLI Reference

```
usage: python generate.py [-h] -o OUTPUT [--max-chars MAX_CHARS]
                          [--portal] [--no-skipped]
                          [--max-chars-per-file MAX_CHARS_PER_FILE]
                          [--lang LANG] folder
```

| 参数 | 说明 |
|------|------|
| `folder` | 要扫描的文件夹路径（位置参数） |
| `-o, --output` | TXT 模式：输出路径；门户模式：输出目录 |
| `--max-chars` | TXT 模式总字符上限（默认不限） |
| `--portal` | 开启门户模式 |
| `--no-skipped` | 不在文件树显示跳过文件 |
| `--max-chars-per-file` | 单个文件最大字符数（默认 50k，0 为不限） |
| `--lang` | 语言（`en` / `zh`，默认 `en`） |

---

## ✨ 高级特性与最新改进 (v1.4.x) / Advanced Features & Latest Improvements

| 改进 | 说明 |
|------|------|
| 🔄 **过滤规则统一** | TXT 与 Portal 共享相同的文件/目录过滤逻辑，来自 `src/constants.py` |
| 🔒 **安全的 CSS 选择器** | 文件名特殊字符通过 `CSS.escape()` polyfill 处理 |
| ✂️ **大文件截断** | 在换行边界安全分割，避免破坏多字节字符（如中文） |
| 🛡️ **更强的 parser 容错** | `python-magic` 加载失败时自动回退到扩展名检测 |
| 📋 **清晰的 skip 报告** | 生成结束后打印被跳过文件的分类原因 |
| 🧰 **`src/utils.py` 抽取** | `human_readable_size` 等工具函数集中管理 |
| 📝 **模板变量化** | `index_page.html` 使用 `$placeholder` 标准占位符，而非硬编码字符串替换 |
| 🚫 **LICENSE / .log / .lock 已移除** | 避免 TXT 中出现日志和配置文件 |

---

## 📂 项目结构 / Project Structure

```
FolderKnowledgeSiteGeneratorForAI/
├── generate.py              # CLI 入口
├── gui.py                   # 桌面 GUI
├── start.cmd                # Windows 一键启动
├── start.sh                 # Linux/macOS 一键启动
│
├── src/
│   ├── constants.py         # 统一的常量、过滤函数
│   ├── gui_scanner.py       # 文件夹扫描与 TXT/HTML 构建
│   ├── utils.py             # 公共工具（human_readable_size 等）
│   │
│   ├── parser/              # 多格式解析器
│   │   ├── dispatcher.py    # MIME 类型判断 & 分派器
│   │   ├── text_parser.py   # 文本文件解析
│   │   ├── pdf_parser.py    # PDF 解析
│   │   └── office_parser.py # DOCX/PPTX/XLSX 解析
│   │
│   └── generator/           # 门户生成器与模板
│       ├── portal.py        # 单页门户生成器
│       ├── templates.py     # HTML 模板构建
│       └── templates/
│           └── index_page.html    # 首页模板（搜索 + 树 + 折叠块）
│
├── tests/                   # pytest 测试
│   ├── test_cli.py          # CLI 入口测试
│   ├── test_parser.py       # 解析器测试
│   └── test_portal.py       # 门户生成器测试
│
├── test_data/               # 测试用例
├── requirements.txt
├── pyproject.toml
└── LICENSE
```

---

## 💡 使用场景与工作流 / Use Cases & Workflows

| 场景 | 操作 |
|------|------|
| 📚 **代码库知识门户** | 用 Portal 模式生成，Edge 侧边栏提问分析 |
| 📝 **项目文档分析** | 用 TXT 模式导出，粘贴到 ChatGPT 分析 |
| 🔄 **CI/CD 文档快照** | 配合 GitHub Actions 生成文档快照 |

### 在 Edge Copilot 中使用 / Use with Edge Copilot

```
1. 门户模式生成知识门户
2. 在 Edge 浏览器中双击打开 index.html
3. 点击 "🤖 Expand All (AI Mode)" 展开所有内容
4. 按 Ctrl+Shift+. 唤醒 Edge Copilot
5. Copilot 自动读取当前页面全部内容，直接提问
```

---

## 🧪 测试 / Testing

```bash
# 运行全部测试
pytest tests/ -v

# 测试覆盖：parser、CLI、portal generator
# 包含 129 项测试，全部通过
```

---

## 🤝 贡献指南 / Contributing

1. **代码风格**：使用 [Ruff](https://docs.astral.sh/ruff/) 检查 — `ruff check src/ tests/`
2. **测试**：确保所有测试通过 — `pytest tests/ -v`
3. **提交规范**：遵循分支提交流程（feature branch → PR → main）

---

## ❓ 常见问题 (FAQ) / Frequently Asked Questions

| 问题 | 解答 |
|------|------|
| **为什么 TXT 比 HTML 小？** | 过滤规则已统一，大小取决于实际解析内容 |
| **为什么有些文件没被导出？** | 查看 `src/constants.py` 中的 `FILTER_EXTS` 和 `FILTER_FILES` |
| **如何自定义过滤规则？** | 修改 `src/constants.py` |
| **能否生成旧版多页门户？** | 可以自行修改模板，但 AI 不推荐（缺乏跨页推理能力） |

---

## 📄 许可证与致谢 / License & Acknowledgements

本项目基于 **MIT License** 开源 — 详见 [LICENSE](LICENSE) 文件。

---

<p align="center">
  <sub>Made with ❤️ by <a href="https://github.com/ABaLaQiYaShanMaiI">ABaLaQiYaShanMaiI</a></sub>
  <br>
  <sub>⭐ Star on <a href="https://github.com/ABaLaQiYaShanMaiI/FolderKnowledgeSiteGeneratorForAI">GitHub</a> if you find this useful!</sub>
</p>