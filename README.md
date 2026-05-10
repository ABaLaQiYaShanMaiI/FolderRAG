> ⚠️ **重要提示 / Important Note**  
> **此项目专门针对有页面读取功能的网页版 AI（如 Edge Copilot、Claude、ChatGPT 等）设计**  
> **This project is specifically designed for browser-based AI with page reading capabilities (e.g., Edge Copilot, Claude, ChatGPT, etc.)**  
>
> 生成的所有 HTML 页面均可被网页版 AI 直接读取和分析，无需任何插件、文件上传或 API 调用。  
> All generated HTML pages can be directly read and analyzed by browser-based AI — no plugins, file uploads, or API calls required.

---

# DocPortal 📁 → 🌐

> **Zero server · Zero API · Zero model — Turn folders into lightweight, offline knowledge portals for browser-based AI.**

DocPortal 是一个极致轻量的本地知识库工具——不运行 AI 模型、不调用 API、不启动后台服务，只需一条命令即可将整个文件夹（PDF、Word、PPT、Excel、文本等）解析并打包成一个带搜索、关键词云、自动分页的静态知识网站，专供网页版 AI 直接读取。

DocPortal is an ultra-lightweight local knowledge base tool — it runs no AI models, calls no APIs, and starts no background servers. With a single command, it turns any folder into a static knowledge site with full-text search, keyword cloud, and automatic page splitting, designed specifically for browser-based AI to read natively.

---

## 📋 目录 / Table of Contents

- [快速开始](#-快速开始--quick-start)
- [使用指南](#-使用指南--usage-guide)
- [使用场景](#-使用场景--use-cases)
- [支持的格式](#-支持的格式--supported-formats)
- [项目结构](#-项目结构--project-structure)
- [测试](#-测试--testing)
- [常见问题](#-常见问题--faq)
- [许可证](#-许可证--license)

---

## 🚀 快速开始 / Quick Start

### 环境要求 / Requirements

- Python **3.8** 及以上 / or later

### 安装 / Install

```bash
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
python gui.py

# ⌨️ 命令行 / CLI
python generate.py ./文档 -o knowledge.html              # 传统模式 / Traditional mode
python generate.py ./文档 --portal -o ./portal_output    # 门户模式（推荐）/ Portal mode (recommended)
```

---

## 📖 使用指南 / Usage Guide

### 两种输出模式 / Two Output Modes

| 模式 / Mode | 命令 / Command | 说明 / Description |
|-------------|----------------|-------------------|
| 🗂️ **传统模式** / Traditional | `python generate.py <文件夹> -o <输出.html>` | 生成单个大 HTML 文件，适合直接粘贴/上传给 Claude、ChatGPT 等 / Single file, suitable for feeding to LLMs |
| 🏛️ **门户模式** / Portal | `python generate.py <文件夹> --portal -o <输出目录>` | 生成可搜索的分页知识门户，推荐在 Edge Copilot 中使用 / Searchable paged portal, recommended for Edge Copilot |

### 完整参数说明 / Full Parameter Reference

```
usage: python generate.py [-h] -o OUTPUT [--max-chars MAX_CHARS]
                          [--portal] [--max-chars-per-page MAX_CHARS_PER_PAGE]
                          [--no-skipped]
                          folder

位置参数 / Positional arguments:
  folder                要扫描的文件夹路径 / Folder path to scan

传统模式选项 / Traditional mode options:
  --max-chars MAX_CHARS 输出总字符数上限（默认不限）/ Max output chars (no limit by default)

门户模式选项 / Portal mode options:
  --portal              生成可搜索的分页知识门户 / Generate searchable paged knowledge portal
  --max-chars-per-page  每页最大字符数（默认 8000）/ Max chars per page (default: 8000)
  --no-skipped          不在首页显示不支持的文档标记 / Hide unsupported file markers on homepage

通用选项 / General options:
  -h, --help            显示帮助信息 / Show help
  -o OUTPUT, --output   传统模式：输出 HTML 路径；门户模式：输出目录路径 / Output path
```

### 实用示例 / Practical Examples

```bash
# 传统模式：基本用法 / Traditional: basic usage
python generate.py ./项目文档 -o output.html

# 传统模式：限制输出 10 万字符 / Traditional: limit to 100K chars
python generate.py ./知识库 -o output.html --max-chars 100000

# 门户模式：生成知识门户（推荐用于 Edge Copilot）/ Portal: generate knowledge portal
python generate.py ./项目文档 --portal -o ./portal_output

# 门户模式：精细控制每页大小 / Portal: fine-tune per-page char limit
python generate.py ./大型文档集 --portal -o ./portal --max-chars-per-page 6000

# 门户模式：跳过不支持的文档标记 / Portal: skip unsupported markers
python generate.py ./文档 --portal -o ./portal --no-skipped
```

### 🖥️ 图形界面 / GUI

启动图形界面 / Launch GUI：

```bash
python gui.py
# 或直接打开指定文件夹 / Or open a folder directly:
python gui.py "C:\你的文件夹路径"
```

| 功能 / Feature | 说明 / Description |
|----------------|-------------------|
| 📂 **文件夹选择** | 浏览或拖拽选择文件夹，快捷键 `Ctrl+O` |
| 🔄 **输出模式切换** | 传统模式 `Ctrl+H` / 门户模式 `Ctrl+P` |
| 🚀 **一键生成** | 点击生成，进度条实时反馈，快捷键 `Ctrl+G` |
| ⌨️ **快捷键** | `Ctrl+O` 打开 / `Ctrl+G` 生成 / `Ctrl+S` 选择输出 / `Esc` 退出 |

### 🏛️ 门户模式详解 / Portal Mode Details

门户模式生成可搜索的分页知识门户，每个文档生成独立 HTML 页面（默认控制在 ~8000 字符），首页带搜索框和关键词云。

生成的文件结构 / Output structure：

```
output_dir/
├── index.html          ← 🏠 首页（搜索框 + 关键词云 + 文档卡片列表）
└── docs/
    ├── 技术文档_需求说明书_pdf.html
    ├── 报告_2024年度总结_docx.html
    └── ...
```

**门户模式特点 / Features**：
- 🔍 首页实时搜索过滤 / Real-time search filtering
- 🏷️ 自动提取关键词标签，形成关键词云 / Auto-extracted keyword cloud
- 🌙 暗黑模式自动跟随系统主题 / Dark mode follows system theme
- 🖨️ 打印友好样式 / Print-friendly styles
- 🔗 面包屑导航：首页 > 文档名 / Breadcrumb navigation
- 📋 一键复制全文 / One-click copy full text
- 🕐 显示文件修改时间、创建时间 / File metadata display

### 在 Edge Copilot 中使用 / Use with Edge Copilot

```
1. 门户模式生成知识门户 / Generate portal
2. 在 Edge 浏览器中双击打开 index.html / Open index.html in Edge
3. 搜索关键词找到目标文档 / Search for documents
4. 按 Ctrl+Shift+. 唤醒 Edge Copilot / Press Ctrl+Shift+. to wake Copilot
5. Copilot 自动读取当前页面内容，直接提问 / Ask questions directly
```

---

## 💡 使用场景 / Use Cases

| 场景 / Scenario | 做法 / Approach |
|----------------|-----------------|
| 🤖 **给 Claude/ChatGPT 喂本地知识** | 传统模式生成 HTML → 粘贴/上传给 AI |
| 🌐 **Edge Copilot 知识库** | 门户模式生成 → Edge 打开 → Ctrl+Shift+. 提问 |
| 🔍 **文档归档检索** | 门户模式生成 → 搜索关键词 → 定位目标文档 |
| 📊 **企业知识抽取** | 扫描合同、报告等批量文档，提取文本交 AI 分析 |

---

## 📦 支持的格式 / Supported Formats

| 格式 / Format | 解析引擎 / Parser | 备注 / Notes |
|---------------|--------------------|--------------|
| TXT / MD / HTML / JSON / XML / CSV / YAML / TOML / INI / LOG / CFG 等 | 原生 UTF-8 读取 | 自动检测编码（UTF-8/GBK/Latin-1） |
| PDF | `pdfminer.six` | 支持水印、多栏等复杂排版 |
| DOCX (Word) | `python-docx` | ⚠️ 仅 `.docx`，不支持旧版 `.doc` |
| PPTX (PowerPoint) | `python-pptx` | ⚠️ 仅 `.pptx`，不支持旧版 `.ppt` |
| XLSX (Excel) | `openpyxl` | ⚠️ 仅 `.xlsx`，不支持旧版 `.xls` |
| 其他格式（.exe, .zip, .mp4, .png 等） | — | 静默跳过 |

> **旧版 Office 格式（.doc / .ppt / .xls）**：请先用 Office 或 WPS 另存为 `.docx` / `.pptx` / `.xlsx`。

---

## 📂 项目结构 / Project Structure

```
DocPortal/
├── generate.py              ← 📌 主入口 / Main entry point
├── gui.py                   ← 🖥️ 桌面 GUI（Tkinter）/ Desktop GUI
├── requirements.txt         ← 依赖清单 / Dependencies
├── pyproject.toml           ← 项目元数据 / Project metadata
├── src/
│   ├── parser/              ← 📄 文档解析引擎 / Document parsing engine
│   │   ├── dispatcher.py    ← MIME 类型判断 & 分派器 / MIME type dispatcher
│   │   ├── text_parser.py   ← 文本文件解析 / Text file parser
│   │   ├── pdf_parser.py    ← PDF 解析 / PDF parser
│   │   └── office_parser.py ← DOCX/PPTX/XLSX 解析 / Office parser
│   └── generator/           ← 🏗️ 知识门户生成器 / Portal generator
│       ├── portal.py        ← 智能分页门户生成器 / Smart paged portal generator
│       └── templates.py     ← HTML 模板（含暗黑模式/打印样式）/ HTML templates
└── tests/
    ├── test_parser.py       ← 解析器测试 / Parser tests
    └── test_portal.py       ← 门户生成器测试 / Portal tests
```

---

## 🧪 测试 / Testing

```bash
pip install pytest
pytest tests/ -v                        # 运行全部测试 / Run all tests
pytest tests/test_portal.py -v          # 仅门户测试 / Portal tests only
pytest tests/ -v --tb=long              # 详细信息 / Detailed output
```

> CI（GitHub Actions）已集成 ruff lint 和自动化测试，提交 PR 或推送 main 时自动运行。

---

## ❓ 常见问题 / FAQ

| 问题 / Question | 解答 / Answer |
|----------------|---------------|
| **输出太大，LLM 放不下？** | 用 `--max-chars` 限制长度，或使用门户模式（每页 8000 字符） |
| **文件解析乱码？** | 工具已自动尝试 UTF-8 → GBK → Latin-1；PDF 扫描件需先 OCR |
| **如何忽略某些文件？** | 自动跳过 `.` 开头隐藏文件；更多规则可修改 `collect_files()` |
| **二进制文件会报错吗？** | 不会——不支持的格式自动静默跳过 |
| **门户输出目录已存在？** | 覆盖同名文件，未改动文件保留 |

---

## 📄 许可证 / License

本项目基于 **MIT License** 开源 — 详见 [LICENSE](LICENSE) 文件。

---

## ✨ 核心功能总览 / Core Features

| 功能 / Feature | 说明 / Description |
|----------------|-------------------|
| 📂 **扫描文件夹** | 递归扫描，自动跳过隐藏文件 |
| 📄 **多格式解析** | PDF、DOCX、PPTX、XLSX、TXT 等 |
| 🎯 **长度控制** | `--max-chars` 适配 LLM 上下文窗口 |
| 🔍 **搜索 + 关键词云** | 门户模式实时搜索过滤 |
| ⚡ **零依赖** | 纯 Python，无需 GPU、数据库、Web 服务 |
| 🌙 **暗黑模式** | 自动跟随系统颜色方案 |
| 🖨️ **打印友好** | 内置 @media print 样式 |
| 🌐 **中英双语 UI** | 所有页面和 GUI 同时显示中英文 |

> 想了解 DocPortal 与传统 RAG 方案的区别？请参阅上方的 [使用指南](#-使用指南--usage-guide)。
