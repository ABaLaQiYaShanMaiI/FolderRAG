> ⚠️ **重要提示 / Important Note**  
> **此项目专门针对有页面读取功能的网页版 AI（如 Edge Copilot、Claude、ChatGPT 等）设计**  
> **This project is specifically designed for browser-based AI with page reading capabilities (e.g., Edge Copilot, Claude, ChatGPT, etc.)**  
>
> 生成的所有 HTML 页面均可被网页版 AI 直接读取和分析，无需任何插件、文件上传或 API 调用。  
> All generated HTML pages can be directly read and analyzed by browser-based AI — no plugins, file uploads, or API calls required.

---

# FolderKnowledgeSiteGeneratorForAI 📁 → 🌐

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-129%20passed-brightgreen)](tests/)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-7B3F00)](pyproject.toml)

> **Zero server · Zero API · Zero model — Turn folders into lightweight, offline knowledge portals for browser-based AI.**

FolderKnowledgeSiteGeneratorForAI 是一个极致轻量的本地知识库工具——不运行 AI 模型、不调用 API、不启动后台服务，只需一条命令即可将整个文件夹（PDF、Word、PPT、Excel、文本等）解析并打包成一个带搜索、关键词云、可折叠文件块的静态知识网站，专供网页版 AI 直接读取。

FolderKnowledgeSiteGeneratorForAI is an ultra-lightweight local knowledge base tool — it runs no AI models, calls no APIs, and starts no background servers. With a single command, it turns any folder into a static knowledge site with full-text search, keyword cloud, and collapsible file blocks, designed specifically for browser-based AI to read natively.

---

## 📋 目录 / Table of Contents

- [快速开始](#-快速开始--quick-start)
- [使用指南](#-使用指南--usage-guide)
- [核心功能](#-核心功能--core-features)
- [支持的格式](#-支持的格式--supported-formats)
- [项目结构](#-项目结构--project-structure)
- [测试](#-测试--testing)
- [版本历史](#-版本历史--release-notes)
- [许可证](#-许可证--license)

---

## 🚀 快速开始 / Quick Start

### 环境要求 / Requirements

- Python **3.8** 及以上 / or later

### 安装 / Install

```bash
# 📦 方式一：通过 pip 安装（从源码）
pip install git+https://github.com/ABaLaQiYaShanMaiI/FolderKnowledgeSiteGeneratorForAI.git

# 🛠️ 方式二：本地开发安装
git clone https://github.com/ABaLaQiYaShanMaiI/FolderKnowledgeSiteGeneratorForAI.git
cd FolderKnowledgeSiteGeneratorForAI

# 创建并激活虚拟环境（推荐）/ Create and activate virtual environment (recommended)
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS / Linux:
# source venv/bin/activate

# 安装依赖 / Install dependencies
pip install -r requirements.txt
```

> **💡 Linux/macOS 用户**：`python-magic` 依赖系统库 `libmagic`，需额外安装 `brew install libmagic`（macOS）或 `sudo apt install libmagic1`（Ubuntu）。Windows 无需额外操作。

### 一行命令启动 / One-command Launch

```bash
# 🖥️ 图形界面（推荐 Win10/Win11）/ GUI (recommended for Windows)
python gui.py [文件夹路径]

# ⌨️ 命令行 / CLI
python generate.py ./文档 -o knowledge.txt               # 纯文本模式 / Text mode
python generate.py ./文档 --portal -o ./portal_output    # 门户模式（推荐）/ Portal mode (recommended)
```

> 🪟 **Windows 用户**：也可直接双击 `start.cmd` 一键启动图形界面。

---

## 📖 使用指南 / Usage Guide

### 两种输出模式 / Two Output Modes

| 模式 / Mode | 命令 / Command | 说明 / Description |
|-------------|----------------|-------------------|
| 🗂️ **传统模式** / Traditional | `python generate.py <文件夹> -o <输出.txt>` | 生成单个 Txt 文件，适合直接粘贴/上传给 Claude、ChatGPT、DeepSeek 等 / Single TXT file, suitable for feeding to LLMs |
| 🏛️ **门户模式** / Portal | `python generate.py <文件夹> --portal -o <输出目录>` | 生成可搜索、可折叠的知识门户，推荐在 Edge Copilot 中使用 / Searchable collapsible knowledge portal, recommended for Edge Copilot |

> **v2.0 变更**：传统模式默认输出 **纯文本（.txt）** 而非 HTML，更适合直接粘贴到 AI 对话窗口。如需旧版 HTML 输出，请使用 `--format html`。

### 完整参数说明 / Full Parameter Reference

```
usage: python generate.py [-h] -o OUTPUT [--max-chars MAX_CHARS]
                          [--portal] [--no-skipped]
                          [--lang LANG] [--format FORMAT]
                          folder

位置参数 / Positional arguments:
  folder                要扫描的文件夹路径 / Folder path to scan

传统模式选项 / Traditional mode options:
  --max-chars MAX_CHARS 输出总字符数上限（默认不限）/ Max output chars (no limit by default)
  --format FORMAT       输出格式：txt（默认）或 html / Output format: txt (default) or html

门户模式选项 / Portal mode options:
  --portal              生成可搜索折叠的知识门户 / Generate searchable collapsible knowledge portal
  --no-skipped          不在首页显示不支持的文档标记 / Hide unsupported file markers on homepage

通用选项 / General options:
  -h, --help            显示帮助信息 / Show help
  -o OUTPUT, --output   传统模式：输出 TXT 路径；门户模式：输出目录路径 / Output path
  --lang LANG           输出页面语言（en/zh-CN，默认 en）/ Output page language
```

> **注意**：门户模式现在生成的是**单页面 HTML**，所有文件内容集中在一个页面内，每个文件以可折叠的块结构展示。不再使用分页（pagination），因为 AI 缺乏跨页推理能力。

### 实用示例 / Practical Examples

```bash
# 传统模式：基本用法（输出 TXT）/ Traditional: basic usage (output TXT)
python generate.py ./项目文档 -o output.txt

# 传统模式：限制输出 10 万字符 / Traditional: limit to 100K chars
python generate.py ./知识库 -o output.txt --max-chars 100000

# 门户模式：生成知识门户（推荐）/ Portal: generate knowledge portal
python generate.py ./项目文档 --portal -o ./portal_output

# 门户模式：跳过不支持的文档标记 / Portal: skip unsupported markers
python generate.py ./文档 --portal -o ./portal --no-skipped

# 指定语言（中文界面）/ Specify language (Chinese UI)
python generate.py ./文档 --portal -o ./portal --lang zh-CN
```

### 🖥️ 图形界面 / GUI

```bash
python gui.py
# 或直接打开指定文件夹 / Or open a folder directly:
python gui.py "C:\你的文件夹路径"
```

**GUI 功能一览：**

| 功能 / Feature | 说明 / Description |
|----------------|-------------------|
| 📂 **文件夹选择** | 浏览、粘贴或拖拽选择文件夹，快捷键 `Ctrl+O` |
| 🔄 **输出模式切换** | 传统模式 / 门户模式，切换时自动调整 UI 设置项 |
| 🚀 **一键生成** | 点击生成按钮，进度条实时反馈，快捷键 `Ctrl+G` |
| 🌐 **中英双语** | 界面右上角 EN/中文 按钮即时切换，偏好自动保存 |
| 📋 **实时文件列表** | 扫描后显示所有文件及其大小、状态（支持/跳过） |
| 🧹 **Clear 按钮** | 一键清空当前文件夹加载状态 |
| ▶️ **HTTP 服务器** | 门户生成后可直接启动本地服务器供 AI 读取 |
| 📂 **拖拽支持** | 支持文件夹拖入 GUI（需 tkinterdnd2） |

### 🏛️ 门户模式详解 / Portal Mode Details

门户模式生成一个完整的**单页知识门户**，所有文件内容集中在一个 HTML 页面中，结构如下：

```
output_dir/
├── index.html          ← 🏠 首页（搜索框 + 文件夹树 + 关键词云 + 可折叠文件块）
└── (其他静态文件)
```

**页面布局 / Page Layout：**

```
┌─────────────────────────────────────────────────────────┐
│ 📁 文件夹名           [🤖 Expand All] [📁 Collapse All]  │
│ Docs: 12  |  Chars: 150,234  |  Size: 1.2 MB            │
├─────────────────────────────────────────────────────────┤
│ 🔍 搜索文件名和标签...                                    │
├──────────────────────┬──────────────────────────────────┤
│ 📂 文件夹结构         │ 📄 文件内容                       │
│                      │                                  │
│ └── src/             │ ┌─ 📄 main.py  1.2 KB  ▶ ─┐     │
│     ├── main.py      │ │ 450 chars  [python][app] │     │
│     ├── utils.py     │ └──────────────────────────┘     │
│     └── data.json    │ ┌────────────────────── ▼ ┐      │
│                      │ │ 📄 utils.py  850 B      │      │
│                      │ │ 320 chars  [helper][io] │      │
│                      │ │ ┌─────────────────────┐ │      │
│                      │ │ │ def read_file():...  │ │      │
│                      │ │ │ def write_file():... │ │      │
│                      │ │ └─────────────────────┘ │      │
│                      │ └──────────────────────────┘     │
│ 🏷️ 关键词             │                                  │
│ python helper app    │                                  │
│ io data config       │                                  │
└──────────────────────┴──────────────────────────────────┘
```

**页面特点 / Features：**

| 功能 | 说明 |
|------|------|
| 🔍 **实时搜索** | 输入关键词即时过滤文件名和标签，文件树同步高亮 |
| 🗂️ **文件夹结构树** | 左侧显示完整文件夹树（以 ASCII 连接线展示层级），点击文件名可跳转并自动展开对应文件块 |
| 🏷️ **关键词云** | 自动提取所有文档的关键词，点击即可筛选 |
| 📄 **可折叠文件块** | 每个文件以头部（图标 + 文件名 + 大小 + 标签）+ 隐藏内容的结构展示，点击头部或 ▶ 按钮展开/收起 |
| 🤖 **一键全部展开** | "Expand All (AI Mode)" 按钮——方便 AI 一次性读取所有代码 |
| 📁 **一键全部收起** | "Collapse All" 按钮——快速恢复默认折叠状态 |
| 🌙 **暗黑模式** | 自动跟随系统颜色方案 |
| 🖨️ **打印友好** | 内置 @media print 样式，打印时自动展开所有内容 |
| 🌐 **中英双语** | 页面内 EN/中文 按钮即时切换，偏好保存到 localStorage |
| 🖱️ **搜索高亮** | 文件树中匹配的文件保持高亮，不匹配的文件半透明显示 |

### 在 Edge Copilot 中使用 / Use with Edge Copilot

```
1. 门户模式生成知识门户 / Generate portal
2. 在 Edge 浏览器中双击打开 index.html / Open index.html in Edge
3. 点击 "🤖 Expand All (AI Mode)" 展开所有内容 / Click "Expand All"
4. 按 Ctrl+Shift+. 唤醒 Edge Copilot / Press Ctrl+Shift+. to wake Copilot
5. Copilot 自动读取当前页面全部内容，直接提问 / Ask questions directly
```

---

## 💡 核心功能 / Core Features

| 功能 / Feature | 说明 / Description |
|----------------|-------------------|
| 📂 **扫描文件夹** | 递归扫描，自动跳过隐藏文件、node_modules、__pycache__ 等 |
| 📄 **多格式解析** | PDF、DOCX、PPTX、XLSX、TXT、Markdown、代码文件等 |
| 🎯 **长度控制** | `--max-chars` 适配 LLM 上下文窗口 |
| 🔍 **搜索 + 关键词云** | 门户模式实时搜索过滤文件名和标签 |
| 🗂️ **文件夹结构树** | ASCII 连接线展示层级结构，点击跳转文件 |
| 📄 **可折叠文件块** | 点击头部或 ▶ 展开/收起，信息集中不重复 |
| 🤖 **AI 模式** | 一键全部展开，方便 AI 一次性读取 |
| ⚡ **零依赖** | 纯 Python，无需 GPU、数据库、Web 服务 |
| 🌙 **暗黑模式** | 自动跟随系统颜色方案 |
| 🖨️ **打印友好** | 内置 @media print 样式，打印时自动展开 |
| 🌐 **中英双语 UI** | GUI 和门户页面均支持即时切换中英文 |
| 🔄 **语言同步持久化** | GUI 语言偏好自动保存，门户页面记住语言选择 |
| 📂 **拖拽支持** | 支持文件夹拖入 GUI（需 tkinterdnd2） |
| ▶️ **HTTP 服务器** | 门户生成后可直接启动本地服务器供 AI 读取 |

---

## 📦 支持的格式 / Supported Formats

| 格式 / Format | 解析引擎 / Parser | 备注 / Notes |
|---------------|--------------------|--------------|
| TXT / MD / HTML / JSON / XML / CSV / YAML / TOML / INI / LOG / CFG 等 | 原生 UTF-8 读取 | 自动检测编码（UTF-8/GBK/Latin-1） |
| PDF | `pdfminer.six` | 支持水印、多栏等复杂排版 |
| DOCX (Word) | `python-docx` | ⚠️ 仅 `.docx`，不支持旧版 `.doc` |
| PPTX (PowerPoint) | `python-pptx` | ⚠️ 仅 `.pptx`，不支持旧版 `.ppt` |
| XLSX (Excel) | `openpyxl` | ⚠️ 仅 `.xlsx`，不支持旧版 `.xls` |
| 代码文件（.cs / .xaml / .sln / .py / .js / .ts 等） | 原生 UTF-8 读取 | 支持 50+ 种编程语言扩展名 |
| 其他格式（.exe, .zip, .mp4, .png 等） | — | 静默跳过 |

> **旧版 Office 格式（.doc / .ppt / .xls）**：请先用 Office 或 WPS 另存为 `.docx` / `.pptx` / `.xlsx`。

---

## 📂 项目结构 / Project Structure

```
FolderKnowledgeSiteGeneratorForAI/
├── generate.py              ← 📌 主入口 / Main entry point
├── gui.py                   ← 🖥️ 桌面 GUI（Tkinter）/ Desktop GUI
├── start.cmd                ← 🪟 Windows 一键启动脚本
├── requirements.txt         ← 依赖清单 / Dependencies
├── pyproject.toml           ← 项目元数据 & 构建配置 / Project metadata & build config
├── LICENSE                  ← MIT 许可证 / MIT License
├── .gitignore               ← Git 忽略规则 / Git ignore rules
│
├── src/                     ← 📦 核心包 / Core package
│   ├── __init__.py
│   ├── constants.py         ← 常量定义（支持的文件类型等）/ Constants (supported file types, etc.)
│   ├── gui_scanner.py       ← GUI 专用文件夹扫描器（异步扫描）/ GUI-specific folder scanner (async)
│   │
│   ├── parser/              ← 📄 文档解析引擎 / Document parsing engine
│   │   ├── __init__.py
│   │   ├── dispatcher.py    ← MIME 类型判断 & 分派器 / MIME type dispatcher
│   │   ├── text_parser.py   ← 文本文件解析 / Text file parser
│   │   ├── pdf_parser.py    ← PDF 解析 / PDF parser
│   │   └── office_parser.py ← DOCX/PPTX/XLSX 解析 / Office parser
│   │
│   └── generator/           ← 🏗️ 知识门户生成器 / Portal generator
│       ├── __init__.py
│       ├── portal.py        ← 单页门户生成器 / Single-page portal generator
│       ├── templates.py     ← HTML 模板构建 / HTML template builder
│       └── templates/       ← HTML 模板文件 / HTML template files
│           └── index_page.html    ← 首页模板（搜索+树+折叠块）
│
├── tests/                   ← 🧪 测试套件 / Test suite
│   ├── conftest.py          ← pytest 共享 fixtures / Shared pytest fixtures
│   ├── test_cli.py          ← CLI 入口测试 / CLI entry point tests
│   ├── test_parser.py       ← 解析器测试 / Parser tests
│   └── test_portal.py       ← 门户生成器测试 / Portal generator tests
│
├── test_data/               ← 测试样本数据 / Test sample data
├── test_output/             ← 测试输出目录 / Test output directory
└── test_final_output/       ← 集成测试输出 / Integration test output
```

---

## 🧪 测试 / Testing

```bash
# 安装测试依赖 / Install test dependencies
pip install pytest

# 运行全部测试 / Run all tests (129 tests)
pytest tests/ -v

# 仅门户测试 / Portal tests only
pytest tests/test_portal.py -v

# 仅解析器测试 / Parser tests only
pytest tests/test_parser.py -v

# 详细输出 / Detailed output with full traceback
pytest tests/ -v --tb=long

# Lint 检查 / Lint check
pip install ruff
ruff check src/ tests/
```

> CI（GitHub Actions）已集成 ruff lint 和自动化测试，提交 PR 或推送 main 时自动运行。

---

## ✨ 版本历史 / Release Notes

### v1.4.0 — 修复与健壮性提升 / Bugfixes & Robustness
- **移除已废弃的 `--max-chars-per-page` 参数**：该参数在之前版本已从 generate.py 中移除，现从 CLI 测试中彻底清除，门户模式不再分页
- **`gui.py` 语言同步修复**：单文件模式遗漏 `language` 参数，GUI 切换为中文后生成的 HTML 仍显示英文，现已补传 `language=self._lang`
- **`templates.py` 元信息占位符**：`index_page.html` 模板中的 `<meta description>` / `<meta keywords>` 不再使用硬编码字符串做 `str.replace()`，改为专用占位符 `$meta_description_escaped` / `$meta_keywords_escaped`
- **文件树幽灵条目修复**：当文件因编码损坏解析失败时，左侧文件夹树仍显示该文件但右侧无对应块。现方案：解析失败的文件在文件树中显示为灰色（`⏭️` 前缀），点击无响应而非弹出 alert
- **`jumpToFile` CSS 选择器转义加强**：使用 `CSS.escape()` polyfill 处理文件名中的特殊字符（`'`、`[`、`]`、`\n` 等），避免 `querySelector` 因非法属性值而失败
- **`gui_scanner.py` 扩展名去重**：移除 `gui_scanner.py` 中与 `constants.py` 重复的 `FALLBACK_EXTS`，统一从 `src.constants.SUPPORTED_TEXT_EXTS` 导入
- **多字节字符安全截断**：`portal.py` 的 `MAX_CHARS_PER_FILE` 截断改为从最后一个 `\n` 分割，避免切断多字节 Unicode 字符（如中文）
- **常量集成测试覆盖**：新增 `test_parser.py` 中的参数化测试，覆盖 `SUPPORTED_TEXT_EXTS` 中的所有扩展名，确保 `.cs` / `.xaml` / `.sln` 等代码文件可被正确解析为文本
- **测试总数：129 项全部通过**（parser 101 + CLI 12 + portal 16）

### v1.3.0 — 单页门户 & 可折叠文件块
- **门户模式改为单页面**：所有文件内容集中在一个 HTML 页面，不再使用分页（AI 缺乏跨页推理能力）
- **全新文件块结构**：每个文件以 `doc-header`（图标 + 文件名 + 大小 + 标签 + 展开按钮）+ `doc-content`（隐藏的代码区）结构展示，信息集中不重复
- **一键全部展开/收起**：新增 "Expand All (AI Mode)" 和 "Collapse All" 按钮
- **删除旧卡片区**：移除了首页的文档卡片（doc-list/doc-grid），所有信息都在文件块头部展示
- **修复闭包陷阱**：修复了 `gui.py` 中 `lambda: self._gen_err(str(e))` 的 Python 3 NameError
- **搜索结果高亮**：文件树中匹配的文件保持高亮，不匹配的半透明显示
- **代码优化**：清理未使用的 import，通过 ruff 检查

### v1.2.0 — 语言同步 & 文件夹结构树
- **中英双语同步**：GUI 选择中文后，生成的门户页面默认显示中文
- **设置持久化**：语言偏好保存到 `~/.folderknowledge_settings.json`
- **文件夹结构树**：门户首页左侧新增完整文件夹树，点击文件名直接跳转
- **跳过文件智能显示**：不支持的格式仅显示在文件树中（灰色标注）
- **Clear 按钮**：GUI 新增 Clear 按钮，一键清空所有状态
- **拖拽兼容性修复**：确保 tkinterdnd2 正确注册 Drop 事件

### v1.1.0 — 初始版本
- 基本的文件夹扫描与文档解析
- 支持 PDF/DOCX/PPTX/XLSX/TXT/MD 等格式
- 传统模式生成单文件输出
- 基础 GUI 界面

---

## ❓ 常见问题 / FAQ

| 问题 / Question | 解答 / Answer |
|----------------|---------------|
| **输出太大，LLM 放不下？** | 用 `--max-chars` 限制长度，AI 模式下也只显示前 N 字符 |
| **文件解析乱码？** | 工具已自动尝试 UTF-8 → GBK → Latin-1；PDF 扫描件需先 OCR |
| **如何忽略某些文件？** | 自动跳过 `.` 开头隐藏文件；更多规则可修改 `portal.py` 中的 `_FILTER_EXTS` / `_FILTER_DIRS` |
| **二进制文件会报错吗？** | 不会——不支持的格式自动静默跳过 |
| **门户模式和传统模式有什么区别？** | 门户模式生成**交互式页面**（搜索、树导航、折叠块）；传统模式生成**纯文本文件**适合直接粘贴给 AI |
| **门户模式为什么不用分页了？** | 因为 AI 缺乏跨页推理能力。所有内容放在一个页面中，AI 可以一次性读取全部展开的内容。而且文件默认折叠，不影响加载速度 |
| **文件内容默认显示还是折叠？** | 默认**折叠**，点击头部或 ▶ 按钮展开。也可点击 "Expand All (AI Mode)" 全部展开 |

---

## 🤝 贡献 / Contributing

欢迎提交 Issue 和 Pull Request！请确保：

1. 代码通过 ruff lint 检查
2. 新增功能包含对应的测试用例
3. 所有测试通过：`pytest tests/ -v`

---

## 📄 许可证 / License

本项目基于 **MIT License** 开源 — 详见 [LICENSE](LICENSE) 文件。

---

<p align="center">
  <sub>Made with ❤️ by <a href="https://github.com/ABaLaQiYaShanMaiI">ABaLaQiYaShanMaiI</a></sub>
  <br>
  <sub>⭐ Star on <a href="https://github.com/ABaLaQiYaShanMaiI/FolderKnowledgeSiteGeneratorForAI">GitHub</a> if you find this useful!</sub>
</p>