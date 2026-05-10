# DocPortal 📁 → 🌐

> **Zero server · Zero API · Zero model — Turn folders into lightweight, offline knowledge portals for browser-based AI.**

---

## 中文 / Chinese

### DocPortal — 面向浏览器 AI 的轻量离线文档门户

DocPortal 是一个极致轻量的本地知识库工具——它不运行任何 AI 模型，不调用任何 API，也不启动任何后台服务。你只需要一条命令，它就把整个文件夹（含 PDF、Word、PPT、Excel、文本等）解析并打包成一个带搜索、关键词云、自动分页的静态知识网站。

#### 为什么是「轻量·离线·面向浏览器 AI」？

- **轻量** — 纯 Python 脚本，无 GPU、无大模型、无向量数据库、无 Docker，普通笔记本即可运行
- **离线** — 生成纯静态 HTML，双击即可使用，无需任何联网或后台服务
- **面向浏览器 AI** — 专为 Edge Copilot、ChatGPT、Claude 等能读网页的 AI 设计，每一页自动控制长度，无需插件或文件上传

DocPortal 不是 RAG。RAG（检索增强生成）通常需要嵌入模型、向量数据库和语言模型协同工作——这意味着 GPU、联网、复杂的部署和持续维护。DocPortal 完全放弃了这条重路线，转而把文档直接做成 AI 可以直接读取的网页：每一页都自动控制长度，确保 Edge Copilot、ChatGPT、Claude 等能完整消费，而无需任何插件或文件上传。

#### 相比其他本地知识库，DocPortal 的优势在哪里？

| 对比维度 | 其他本地知识库（AnythingLLM、Dify 等） | DocPortal |
|---------|--------------------------------------|-----------|
| 是否需要本地大模型 | ✅ 需要下载 8B~14B 模型 | ❌ 不需要 |
| 是否需要 GPU | ⚠️ 推荐独立显卡 | ✅ 纯 CPU，普通笔记本即可 |
| 是否需要 API Key | ⚠️ 部分需要 | ❌ 不需要 |
| 是否需要启动服务 | ✅ Docker / Web 服务器 / Ollama | ❌ 生成纯静态 HTML，双击即用 |
| 目标 AI | 工具自带的聊天界面 | 任何能读网页的 AI（Edge Copilot、ChatGPT、Claude） |
| 部署难度 | 下载模型 → 配置向量库 → 调参数 | 一个命令 → 双击 index.html |
| 离线可用 | ⚠️ 模型下载后可用 | ✅ 完全离线，无需任何依赖 |

DocPortal 是专为**网页侧边栏 AI（如 Edge Copilot）和对话式 AI** 设计的「文档直通车」——不改变 AI 的工作方式，只把知识送到它眼前。

---

## English

### DocPortal — One-click local docs portal for browser-based AI

DocPortal is an ultra-lightweight local knowledge base tool — it runs no AI models, calls no APIs, and starts no background servers. With a single command, it turns an entire folder (PDF, Word, PPT, Excel, plain text, etc.) into a static knowledge site complete with full-text search, keyword cloud, and automatic page splitting.

#### Why "lightweight · offline · for browser-based AI"?

- **Lightweight** — Pure Python, no GPU, no LLM, no vector DB, no Docker — runs on any laptop
- **Offline** — Generates pure static HTML, double-click to use — no internet or background services needed
- **Browser AI ready** — Designed for Edge Copilot, ChatGPT, Claude, and any AI that reads web pages. Each page is auto-sized so browser AIs can consume it completely — no plugins, no file uploads.

DocPortal is not a RAG system. Retrieval-Augmented Generation typically requires an embedding model, a vector database, and an LLM — that means GPU, internet access, complex deployment, and ongoing maintenance. DocPortal takes a radically simpler path: it turns your documents directly into web pages that AI can read natively. Each page is automatically size-limited so that browser-based AI (Edge Copilot, ChatGPT, Claude) can digest it completely — no plugins, no file uploads required.

#### What makes DocPortal different from other local knowledge-base tools?

| Aspect | Other tools (AnythingLLM, Dify, etc.) | DocPortal |
|--------|--------------------------------------|-----------|
| Local LLM required | ✅ Must download large models (8B~14B) | ❌ Not needed |
| GPU required | ⚠️ Discrete GPU recommended | ✅ CPU-only, works on any laptop |
| API Key required | ⚠️ Often required | ❌ Not needed |
| Running server | ✅ Docker / Web server / Ollama | ❌ Pure static HTML — just double-click |
| Target AI | Built-in chat interface | Any webpage-reading AI (Edge Copilot, ChatGPT, Claude) |
| Deployment difficulty | Download models → configure vector DB → tune parameters | One command → double-click index.html |
| Offline use | ⚠️ After model download | ✅ Fully offline, zero runtime dependencies |

DocPortal is a "document express lane" designed specifically for browser sidebar AIs (like Edge Copilot) and conversational AIs — it doesn't change how AI works, it just delivers knowledge right where AI looks.

---

## ✨ 核心功能 / Core Features

| 功能 / Feature | 说明 / Description |
|----------------|-------------------|
| 📂 **扫描文件夹 / Scan Folder** | 递归扫描目录下所有文件，自动跳过 `.` 开头的隐藏文件 |
| 📄 **多格式解析 / Multi-format Parsing** | PDF、DOCX、PPTX、XLSX、TXT、MD、HTML、JSON、XML 等 |
| 📝 **结构化输出 / Structured Output** | 生成 `<article>` 标签包裹的 HTML，来源路径清晰标注，AI 友好 |
| 🎯 **长度控制 / Length Control** | `--max-chars` 参数限制输出总字符数，适配 LLM 上下文窗口 |
| 🏛️ **知识门户 / Knowledge Portal** | 生成带搜索、关键词过滤、文档卡片的分页知识库 |
| ⚡ **轻量无依赖 / Lightweight** | 无需数据库、无需向量模型、无需 Web 服务，纯 Python 脚本运行 |
| 🌐 **跨平台 / Cross-platform** | Windows / macOS / Linux 均可运行 |
| 🖥️ **图形界面 / GUI** | 提供 Tkinter 桌面 GUI，支持拖拽文件夹 |
| 🔤 **智能编码 / Smart Encoding** | 自动检测 UTF-8/GBK/Latin-1 编码，中文 Windows 友好 |
| 🌙 **暗黑模式 / Dark Mode** | 门户页面自动跟随系统颜色方案 |
| 🖨️ **打印友好 / Print-friendly** | 门户页面内置 @media print 样式 |
| 🌐 **中英双语 UI / Bilingual UI** | 所有门户页面和 GUI 均同时显示中英文 / All portal pages & GUI show both Chinese and English |

---

## 🚀 快速开始 / Quick Start

### 环境要求 / Requirements

- Python **3.8** 及以上版本 / or later

### 1️⃣ 安装依赖 / Install Dependencies

```bash
# (推荐) 创建并使用虚拟环境 / Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS / Linux:
# source venv/bin/activate

# 安装依赖 / Install dependencies
pip install -r requirements.txt
```

> **💡 对于 Linux/macOS 用户 / For Linux/macOS users**：`python-magic` 依赖系统库 `libmagic`，需要额外安装：
> - macOS：`brew install libmagic`
> - Ubuntu/Debian：`sudo apt install libmagic1`
> - CentOS/RHEL：`sudo yum install libmagic-devel`
>
> Windows 用户无需额外操作，`requirements.txt` 已包含 `python-magic-bin` / No extra steps needed on Windows.

### 2️⃣ 启动方式 / Launch Methods

```bash
# 图形界面（推荐 Win10/Win11 用户）/ GUI (recommended for Windows users)
python gui.py

# 命令行 / Command line
python generate.py ./文档 -o knowledge.html
```

### 3️⃣ 命令行运行 / CLI Usage

```bash
# 传统模式：生成单个 HTML 文件 / Traditional mode: single HTML file
python generate.py ./文档 -o knowledge.html

# 门户模式：生成可搜索的知识门户 / Portal mode: searchable knowledge portal
python generate.py ./文档 --portal -o ./portal_output
```

---

## 📖 完整参数说明 / Full Parameter Reference

```
usage: python generate.py [-h] -o OUTPUT [--max-chars MAX_CHARS]
                          [--portal] [--max-chars-per-page MAX_CHARS_PER_PAGE]
                          [--no-skipped]
                          folder

位置参数 / Positional arguments:
  folder                要扫描的文件夹路径 / Folder path to scan

传统模式选项 / Traditional mode options:
  --max-chars MAX_CHARS
                        输出总字符数上限（可选，默认不限）/ Max output chars (optional, no limit by default)

门户模式选项 / Portal mode options:
  --portal              生成可搜索的分页知识门户（推荐 Edge Copilot 使用）/ Generate searchable paged knowledge portal
  --max-chars-per-page MAX_CHARS_PER_PAGE
                        每页最大字符数（默认 8000，确保 Copilot 完整读取）/ Max chars per page (default: 8000)
  --no-skipped          不在首页中显示不支持的文档标记 / Hide unsupported file markers on homepage

通用选项 / General options:
  -h, --help            显示帮助信息并退出 / Show help and exit
  -o OUTPUT, --output OUTPUT
                        传统模式：输出 HTML 文件路径；门户模式：输出目录路径 / Traditional: output HTML path; Portal: output directory
```

---

## 🏗️ 门户模式 / Portal Mode (Recommended)

DocPortal 支持两种输出模式 / supports two output modes:

### 传统模式 / Traditional Mode (Default)

生成单个大 HTML 文件，适合直接喂给 LLM（Claude / ChatGPT 等）/ Generates a single large HTML file, suitable for feeding to LLMs:

```bash
python generate.py ./文档 -o knowledge.html
```

### 🆕 门户模式 / Portal Mode

生成**可搜索的分页知识门户**，推荐在 Edge Copilot 中使用 / Generates a **searchable paged knowledge portal**, recommended for use with Edge Copilot:

```bash
# 生成知识门户到 output_dir 目录 / Generate knowledge portal to output_dir
python generate.py ./文档 --portal -o ./output_dir

# 指定每页最大字符数 / Set max chars per page
python generate.py ./文档 --portal -o ./output_dir --max-chars-per-page 8000

# 不在首页显示不支持的文件标记 / Hide unsupported file markers on homepage
python generate.py ./文档 --portal -o ./output_dir --no-skipped
```

**门户模式特点 / Portal Mode Features**：
- 📑 每个文档生成独立 HTML 页面（控制在 ~8000 字符以内）/ Independent HTML page per doc (~8000 chars)
- 🔍 首页 `index.html` 带**搜索框**，可实时过滤文档 / Homepage with real-time search filtering
- 🏷️ 自动提取**关键词标签**（含中英文停用词过滤），形成关键词云 / Auto-extracted keyword tags with keyword cloud
- 📇 文档卡片展示：文件名、大小、预览摘要、标签、文件时间 / Doc cards: filename, size, preview, tags, timestamps
- 🌐 适合在 Edge 浏览器中打开，按 `Ctrl+Shift+.` 唤醒 Copilot 提问 / Open in Edge, press `Ctrl+Shift+.` to ask Copilot
- 🌙 **暗黑模式 / Dark Mode**：自动跟随系统主题 / Auto-follows system theme
- 🖨️ **打印友好 / Print-friendly**：页面内置打印样式 / Built-in @media print styles
- 🔗 **面包屑导航 / Breadcrumb Navigation**：文档页顶部显示「首页 > 文档名」/ "Home > Doc name" at top
- 📋 **一键复制全文 / Copy Full Text**：每个文档页均有复制按钮 / Copy button on each doc page
- 🕐 **元数据展示 / Metadata**：显示文件修改时间、创建时间 / Shows file modification and creation times
- 📊 **进度显示 / Progress Bar**：CLI 模式下显示实时进度条 / Real-time progress bar in CLI mode

门户模式输出结构 / Portal output structure：
```
output_dir/
├── index.html          ← 🏠 首页入口（搜索框 + 关键词云 + 文档卡片列表）
└── docs/
    ├── 技术文档_需求说明书_pdf.html   ← 📄 每个文档独立页面 / Each doc as a separate page
    ├── 报告_2024年度总结_docx.html
    └── ...
```

### 实用示例 / Practical Examples

```bash
# 传统模式：基本用法 / Traditional: basic usage
python generate.py ./项目文档 -o output.html

# 传统模式：限制输出 10 万字符（适合大部分 LLM）/ Traditional: limit to 100K chars
python generate.py ./知识库 -o output.html --max-chars 100000

# 门户模式：生成知识门户（推荐）/ Portal: generate knowledge portal (recommended)
python generate.py ./项目文档 --portal -o ./portal_output

# 门户模式：精细控制每页大小 / Portal: fine-tune per-page char limit
python generate.py ./大型文档集 --portal -o ./portal --max-chars-per-page 6000

# 门户模式：跳过不支持的文档标记 / Portal: skip unsupported markers
python generate.py ./文档 --portal -o ./portal --no-skipped

# 扫描桌面文件夹 / Scan desktop folder
python generate.py ~/Desktop/我的笔记 -o notes.html

# Windows 路径示例 / Windows path example
python generate.py "C:\Users\用户名\文档" -o docs.html
```

---

## 🖥️ 图形界面 / GUI

DocPortal 提供图形界面，支持两种输出模式 / DocPortal provides a desktop GUI supporting both output modes:

```bash
# 启动 GUI / Launch GUI
python gui.py
```

**GUI 功能 / GUI Features**：
- 📂 点击浏览或拖拽选择文件夹 / Browse or drag-and-drop folder selection
- 📋 文件列表展示（文件名、大小、是否支持解析）/ File list (name, size, parseable flag)
- ⚙️ **输出模式切换**：单文件 HTML / 知识门户 / Output mode toggle: single HTML file / knowledge portal
- 📝 自定义输出路径、文件名、最大字符数 / Custom output path, filename, max chars
- 📏 门户模式下可设置每页字符数 / Per-page char limit in portal mode
- 🚀 一键生成，进度条实时反馈 / One-click generate with progress bar
- ✅ 生成完成后弹出详情报告 / Detailed report popup after generation
- ⌨️ 快捷键支持（`Ctrl+O` 打开、`Ctrl+G` 生成等）/ Keyboard shortcuts

详见 / See [README_GUI.md](README_GUI.md)。

---

## 📖 输出示例（传统模式）/ Output Example (Traditional Mode)

生成的 `knowledge.html` 文件结构如下 / The generated `knowledge.html` has this structure:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>Knowledge Export</title>
  <style>
    body { font-family: sans-serif; max-width: 960px; margin: 0 auto; padding: 20px; }
    article { border: 1px solid #ddd; border-radius: 6px; padding: 16px; margin-bottom: 16px; }
    h2 { font-size: 1.1em; color: #2c3e50; margin-top: 0; word-break: break-all; }
    p { white-space: pre-wrap; word-break: break-word; font-size: 0.95em; line-height: 1.6; }
  </style>
</head>
<body>
  <h1>文件夹知识导出 / Folder Knowledge Export</h1>
  <p>来源 / Source：C:\Users\...\文档</p>
  <p>共 12 个文件，45872 字符 / 12 files, 45872 chars</p>
  <hr>

  <article>
    <h2>来源 / Source：技术文档/设计说明.pdf</h2>
    <p>正文内容 / Content...</p>
  </article>

  <article>
    <h2>来源 / Source：报告/2024年度总结.docx</h2>
    <p>正文内容 / Content...</p>
  </article>

  ...
</body>
</html>
```

**特点 / Features**：
- 每个文件独立一个 `<article>` 区块 / Each file gets its own `<article>` block
- 标题带有来源路径（相对路径），AI 可清晰分辨不同来源（不暴露绝对路径）/ Source paths are relative, not absolute, for privacy
- 顶部汇总文件数量和总字符数 / Summary of file count and total chars at top
- 内置简洁样式，浏览器直接打开即可阅读 / Built-in minimal styles, readable directly in browser
- 超出长度限制时，末尾自动添加截断提示注释 / Truncation note added when exceeding char limit

---

## 📦 支持的格式 / Supported Formats

| 格式 / Format | 解析引擎 / Parser | 备注 / Notes |
|---------------|--------------------|--------------|
| TXT / MD / HTML / JSON / XML / CSV / YAML / TOML / INI / LOG / CFG 等文本文件 | 原生 UTF-8 读取 / Native UTF-8 | 自动检测编码（UTF-8/GBK/Latin-1）/ Auto-detect encoding |
| PDF | `pdfminer.six` | 支持带水印、多栏等复杂排版 / Supports watermarks, multi-column layouts |
| DOCX (Word) | `python-docx` | 仅支持 `.docx`（新版），不支持旧版 `.doc` / `.docx` only, no legacy `.doc` |
| PPTX (PowerPoint) | `python-pptx` | 仅支持 `.pptx`（新版），不支持旧版 `.ppt` / `.pptx` only, no legacy `.ppt` |
| XLSX (Excel) | `openpyxl` | 仅支持 `.xlsx`（新版），不支持旧版 `.xls` / `.xlsx` only, no legacy `.xls` |
| 其他格式（.exe, .zip, .mp4, .png 等所有未列出的格式） / Other formats | — | 静默跳过，不报错 / Silently skipped, no errors |

> ⚠️ **旧版 Office 格式（.doc / .ppt / .xls）**：由于底层库限制，暂不支持直接解析。建议用 Office 或 WPS 另存为 `.docx` / `.pptx` / `.xlsx` 后再使用 / Legacy Office formats are not supported; please save as new formats first.

---

## 📂 项目结构 / Project Structure

```
DocPortal/
├── generate.py                 ← 📌 唯一入口，直接运行此文件 / Main entry point
├── gui.py                      ← 🖥️ 桌面图形界面（Tkinter，支持门户模式）/ Desktop GUI
├── requirements.txt            ← 📌 依赖清单 / Dependencies
├── LICENSE                     ← 开源许可证 / License
├── pyproject.toml              ← 项目元数据（可 pip install 安装）/ Project metadata
├── README.md                   ← 本文件 / This file
├── README_GUI.md               ← 桌面 GUI 使用说明 / GUI documentation
├── .gitignore                  ← Git 忽略规则 / Git ignore rules
├── .github/
│   └── workflows/
│       └── ci.yml              ← GitHub Actions CI 配置 / CI configuration
├── src/
│   ├── __init__.py
│   ├── parser/                 ← 📄 文档解析引擎 / Document parsing engine
│   │   ├── __init__.py
│   │   ├── dispatcher.py       ← MIME 类型判断 & 分派器 / MIME type dispatcher
│   │   ├── text_parser.py      ← 文本文件解析 / Text file parser
│   │   ├── pdf_parser.py       ← PDF 解析 / PDF parser
│   │   └── office_parser.py    ← DOCX / PPTX / XLSX 解析 / Office parser
│   └── generator/              ← 🏗️ 知识门户生成器 / Knowledge portal generator
│       ├── __init__.py
│       ├── portal.py           ← 🆕 智能分页门户生成器 / Smart paged portal generator
│       └── templates.py        ← HTML 模板（首页 & 文档页，含暗黑模式/打印样式）/ HTML templates
└── tests/
    ├── conftest.py             ← pytest 共享配置 / Shared pytest config
    ├── test_parser.py          ← 解析器单元测试 / Parser unit tests
    └── test_portal.py          ← 🆕 门户生成器单元测试 / Portal generator tests
```

---

## 🧪 测试 / Testing

```bash
# 安装测试依赖 / Install test dependencies
pip install pytest

# 运行全部测试（含解析器 + 门户生成器）/ Run all tests
pytest tests/ -v

# 仅运行门户生成器测试 / Run portal generator tests only
pytest tests/test_portal.py -v

# 运行测试并显示详细信息 / Run tests with detailed output
pytest tests/ -v --tb=long
```

测试覆盖 / Test coverage：
| 测试 / Test | 说明 / Description |
|-------------|-------------------|
| `test_parser.py` | 解析引擎测试（文本、PDF、不存在的文件）/ Parser tests (text, PDF, non-existent files) |
| `test_portal.py` | 门户生成器测试（11 项，含关键词提取、分页、排序、空文件夹等）/ Portal tests (11 tests: keywords, pagination, sorting, empty folders, etc.) |

> CI（GitHub Actions）中已集成 lint（ruff）和自动化测试，提交 PR 或推送 main 分支时自动运行 / CI integrated with ruff linting and automated tests on PR and main push.

---

## 💡 使用场景 / Use Cases

- **🤖 给 Claude / GPT 喂本地知识 / Feed local knowledge to Claude/GPT**：将项目文档、PDF 书籍、笔记导出为 HTML，直接粘贴/上传给 AI / Export project docs, PDF books, notes as HTML for AI
- **📚 知识库批量整理 / Batch organize knowledge base**：将散落的文档统一解析为结构化文本 / Parse scattered docs into structured text
- **🌐 Edge Copilot 知识库 / Edge Copilot knowledge base**：生成门户后打开 Edge 浏览器访问，按 `Ctrl+Shift+.` 唤醒 Copilot 直接提问 / Generate portal, open in Edge, press `Ctrl+Shift+.` to ask Copilot
- **🔍 文档归档检索 / Document archive search**：配合门户模式搜索功能，在知识库中快速定位目标文档 / Search and locate documents quickly in portal mode
- **📊 企业知识抽取 / Enterprise knowledge extraction**：扫描合同、报告等批量文档，提取文本交给 AI 做摘要或分析 / Scan contracts, reports for AI summarization and analysis

---

## ❓ 常见问题 / FAQ

### Q: 输出文件太大，LLM 放不下怎么办？/ Output too large for LLM?
使用 `--max-chars` 限制输出长度，例如 `--max-chars 50000`。超出部分自动截断。建议使用门户模式，每个页面默认控制在 8000 字符 / Use `--max-chars` to limit output; or better, use portal mode (8000 chars per page by default).

### Q: 某些文件解析失败 / 乱码怎么办？/ Files fail to parse or show garbled text?
- 文本文件乱码：工具已自动尝试 UTF-8 → GBK → Latin-1，若仍乱码请确认文件编码 / Auto-tries UTF-8 → GBK → Latin-1; confirm file encoding if still garbled
- PDF 扫描件：`pdfminer.six` 无法解析纯扫描图片，需先 OCR / Scanned PDFs need OCR first
- 旧版 Office（.doc / .ppt / .xls）：请另存为新版格式 / Save as new format

### Q: 如何忽略某些文件？/ How to ignore certain files?
目前会自动跳过 `.` 开头的隐藏文件（如 `.git`、`.DS_Store`）。如需更多过滤规则，可修改 `generate.py` 中的 `collect_files()` 函数 / Hidden files (`.git`, `.DS_Store`) are auto-skipped; modify `collect_files()` for additional filters.

### Q: 解析速度慢怎么办？/ Slow parsing?
大型文件（如几百页 PDF、大 Excel）解析较慢属正常现象。CLI 门户模式支持进度条显示，可实时了解处理进度 / Large files parse slowly; portal mode shows a progress bar.

### Q: 文件夹里有 .exe / .zip / .mp4 等二进制文件会报错吗？/ Will binary files cause errors?
不会。工具会自动识别文件类型，仅解析支持的格式，其余格式自动静默跳过 / No — unsupported files are silently skipped.

### Q: 门户模式输出目录已存在会怎样？/ What if portal output directory already exists?
不会报错。工具会提示目录已存在，然后覆盖同名文件，未改动文件会保留 / Overwrites same-named files, preserves unchanged ones.

### Q: 如何安装测试依赖？/ How to install test dependencies?
```bash
# 方式一：使用 dev extras / Option 1: use dev extras
pip install ".[dev]"

# 方式二：直接安装 pytest / Option 2: install pytest directly
pip install pytest
```

---

## 📄 许可证 / License

本项目基于 **MIT License** 开源 — 详见 / See [LICENSE](LICENSE) 文件。
