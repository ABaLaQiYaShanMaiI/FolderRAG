# FolderRAG 📁 → 📄

> **注**：本工具名称中的 "RAG" 指的是将文件夹内容整理成结构化知识包供 AI 检索阅读，而非完整的检索增强生成（Retrieval-Augmented Generation）系统。若需更精准的名称，可理解为"文件夹转 HTML 知识包"工具（Folder → Docs → HTML）。

**文件夹 → 知识 HTML 导出工具**

FolderRAG 递归扫描本地文件夹中的所有文档，自动解析 PDF、Word、Excel、PPT 和文本文件，生成一份**结构化 HTML 文件**或**可搜索的知识门户**，可直接交给任何 AI / LLM 工具（如 Claude、ChatGPT、Edge Copilot）阅读。

```bash
# 传统模式：单文件输出
python generate.py ./my_folder -o knowledge.html

# 门户模式（推荐）：生成可搜索的知识门户
python generate.py ./my_folder --portal -o ./portal_output
```

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| **📂 扫描文件夹** | 递归扫描目录下所有文件，自动跳过 `.` 开头的隐藏文件 |
| **📄 多格式解析** | PDF、DOCX、PPTX、XLSX、TXT、MD、HTML、JSON、XML 等 |
| **📝 结构化输出** | 生成 `<article>` 标签包裹的 HTML，来源路径清晰标注，AI 友好 |
| **🎯 长度控制** | `--max-chars` 参数限制输出总字符数，适配 LLM 上下文窗口 |
| **🏛️ 知识门户** | 生成带搜索、关键词过滤、文档卡片的分页知识库 |
| **⚡ 轻量无依赖** | 无需数据库、无需向量模型、无需 Web 服务，纯 Python 脚本运行 |
| **🌐 跨平台** | Windows / macOS / Linux 均可运行 |
| **🖥️ 图形界面** | 提供 Tkinter 桌面 GUI，支持拖拽文件夹 |
| **🔤 智能编码** | 自动检测 UTF-8/GBK/Latin-1 编码，中文 Windows 友好 |
| **🌙 暗黑模式** | 门户页面自动跟随系统颜色方案 |
| **🖨️ 打印友好** | 门户页面内置 @media print 样式 |

---

## 🚀 快速开始

### 环境要求

- Python **3.8** 及以上版本

### 1️⃣ 安装依赖

```bash
# (推荐) 创建并使用虚拟环境
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS / Linux:
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

> **💡 对于 Linux/macOS 用户**：`python-magic` 依赖系统库 `libmagic`，需要额外安装：
> - macOS：`brew install libmagic`
> - Ubuntu/Debian：`sudo apt install libmagic1`
> - CentOS/RHEL：`sudo yum install libmagic-devel`
>
> Windows 用户无需额外操作，`requirements.txt` 已包含 `python-magic-bin`。

### 2️⃣ 启动方式

```bash
# 图形界面（推荐 Win10/Win11 用户）
python gui.py

# 命令行
python generate.py ./文档 -o knowledge.html
```

### 3️⃣ 命令行运行

```bash
# 传统模式：生成单个 HTML 文件
python generate.py ./文档 -o knowledge.html

# 门户模式：生成可搜索的知识门户
python generate.py ./文档 --portal -o ./portal_output
```

---

## 📖 完整参数说明

```
usage: python generate.py [-h] -o OUTPUT [--max-chars MAX_CHARS]
                          [--portal] [--max-chars-per-page MAX_CHARS_PER_PAGE]
                          [--no-skipped]
                          folder

位置参数:
  folder                要扫描的文件夹路径

传统模式选项:
  --max-chars MAX_CHARS
                        输出总字符数上限（可选，默认不限）

门户模式选项:
  --portal              生成可搜索的分页知识门户（推荐 Edge Copilot 使用）
  --max-chars-per-page MAX_CHARS_PER_PAGE
                        每页最大字符数（默认 8000，确保 Copilot 完整读取）
  --no-skipped          不在首页中显示不支持的文档标记

通用选项:
  -h, --help            显示帮助信息并退出
  -o OUTPUT, --output OUTPUT
                        传统模式：输出 HTML 文件路径；门户模式：输出目录路径
```

---

## 🏗️ 门户模式（推荐）

FolderRAG 支持两种输出模式：

### 传统模式（默认）

生成单个大 HTML 文件，适合直接喂给 LLM（Claude / ChatGPT 等）：

```bash
python generate.py ./文档 -o knowledge.html
```

### 🆕 门户模式

生成**可搜索的分页知识门户**，推荐在 Edge Copilot 中使用：

```bash
# 生成知识门户到 output_dir 目录
python generate.py ./文档 --portal -o ./output_dir

# 指定每页最大字符数
python generate.py ./文档 --portal -o ./output_dir --max-chars-per-page 8000

# 不在首页显示不支持的文件标记
python generate.py ./文档 --portal -o ./output_dir --no-skipped
```

**门户模式特点**：
- 📑 每个文档生成独立 HTML 页面（控制在 ~8000 字符以内）
- 🔍 首页 `index.html` 带**搜索框**，可实时过滤文档
- 🏷️ 自动提取**关键词标签**（含中英文停用词过滤），形成关键词云
- 📇 文档卡片展示：文件名、大小、预览摘要、标签、文件时间
- 🌐 适合在 Edge 浏览器中打开，按 `Ctrl+Shift+.` 唤醒 Copilot 提问
- 🌙 **暗黑模式**：自动跟随系统主题（Windows / macOS）
- 🖨️ **打印友好**：页面内置打印样式，支持保存为 PDF
- 🔗 **面包屑导航**：文档页顶部显示「首页 > 文档名」
- 📋 **一键复制全文**：每个文档页均有复制按钮
- 🕐 **元数据展示**：显示文件修改时间、创建时间
- 📊 **进度显示**：CLI 模式下显示实时进度条

门户模式输出结构：
```
output_dir/
├── index.html          ← 🏠 首页入口（搜索框 + 关键词云 + 文档卡片列表）
└── docs/
    ├── 技术文档_需求说明书_pdf.html   ← 📄 每个文档独立页面
    ├── 报告_2024年度总结_docx.html
    └── ...
```

### 实用示例

```bash
# 传统模式：基本用法
python generate.py ./项目文档 -o output.html

# 传统模式：限制输出 10 万字符（适合大部分 LLM）
python generate.py ./知识库 -o output.html --max-chars 100000

# 门户模式：生成知识门户（推荐）
python generate.py ./项目文档 --portal -o ./portal_output

# 门户模式：精细控制每页大小
python generate.py ./大型文档集 --portal -o ./portal --max-chars-per-page 6000

# 门户模式：跳过不支持的文档标记
python generate.py ./文档 --portal -o ./portal --no-skipped

# 扫描桌面文件夹
python generate.py ~/Desktop/我的笔记 -o notes.html

# Windows 路径示例
python generate.py "C:\Users\用户名\文档" -o docs.html
```

---

## 🖥️ 图形界面（GUI）

FolderRAG 提供图形界面，支持两种输出模式：

```bash
# 启动 GUI
python gui.py
```

**GUI 功能**：
- 📂 点击浏览或拖拽选择文件夹
- 📋 文件列表展示（文件名、大小、是否支持解析）
- ⚙️ **输出模式切换**：单文件 HTML / 知识门户
- 📝 自定义输出路径、文件名、最大字符数
- 📏 门户模式下可设置每页字符数
- 🚀 一键生成，进度条实时反馈
- ✅ 生成完成后弹出详情报告
- ⌨️ 快捷键支持（`Ctrl+O` 打开、`Ctrl+G` 生成等）

详见 [README_GUI.md](README_GUI.md)。

---

## 📖 输出示例（传统模式）

生成的 `knowledge.html` 文件结构如下：

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
  <h1>文件夹知识导出</h1>
  <p>来源：C:\Users\...\文档</p>
  <p>共 12 个文件，45872 字符</p>
  <hr>

  <article>
    <h2>来源：技术文档/设计说明.pdf</h2>
    <p>正文内容......</p>
  </article>

  <article>
    <h2>来源：报告/2024年度总结.docx</h2>
    <p>正文内容......</p>
  </article>

  ...
</body>
</html>
```

**特点**：
- 每个文件独立一个 `<article>` 区块
- 标题带有来源路径（相对路径），AI 可清晰分辨不同来源（不暴露绝对路径）
- 顶部汇总文件数量和总字符数
- 内置简洁样式，浏览器直接打开即可阅读
- 超出长度限制时，末尾自动添加截断提示注释

> **提示**：输出中的来源路径显示为**相对于扫描目录的相对路径**，不会泄漏用户的绝对路径隐私。

---

## 📦 支持的格式

| 格式 | 解析引擎 | 备注 |
|------|----------|------|
| TXT / MD / HTML / JSON / XML / CSV / YAML / TOML / INI / LOG / CFG 等文本文件 | 原生 UTF-8 读取 | 自动检测编码（UTF-8/GBK/Latin-1） |
| PDF | `pdfminer.six` | 支持带水印、多栏等复杂排版 |
| DOCX (Word) | `python-docx` | 仅支持 `.docx`（新版），不支持旧版 `.doc` |
| PPTX (PowerPoint) | `python-pptx` | 仅支持 `.pptx`（新版），不支持旧版 `.ppt` |
| XLSX (Excel) | `openpyxl` | 仅支持 `.xlsx`（新版），不支持旧版 `.xls` |
| 其他格式（.exe, .zip, .mp4, .png 等所有未列出的格式） | — | 静默跳过，不报错——自动识别并跳过无法解析的二进制/非文档文件 |

> ⚠️ **旧版 Office 格式（.doc / .ppt / .xls）**：由于底层库限制，暂不支持直接解析。建议用 Office 或 WPS 另存为 `.docx` / `.pptx` / `.xlsx` 后再使用。

---

## 📂 项目结构

```
FolderRAG/
├── generate.py                 ← 📌 唯一入口，直接运行此文件
├── gui.py                      ← 🖥️ 桌面图形界面（Tkinter，支持门户模式）
├── requirements.txt            ← 📌 依赖清单
├── LICENSE                     ← 开源许可证
├── pyproject.toml              ← 项目元数据（可 pip install 安装）
├── README.md                   ← 本文件
├── README_GUI.md               ← 桌面 GUI 使用说明
├── .gitignore                  ← Git 忽略规则
├── .github/
│   └── workflows/
│       └── ci.yml              ← GitHub Actions CI 配置
├── src/
│   ├── __init__.py
│   ├── parser/                 ← 📄 文档解析引擎
│   │   ├── __init__.py
│   │   ├── dispatcher.py       ← MIME 类型判断 & 分派器（基于 python-magic）
│   │   ├── text_parser.py      ← 文本文件解析（TXT/MD/HTML/JSON/XML 等）
│   │   ├── pdf_parser.py       ← PDF 解析（基于 pdfminer.six）
│   │   └── office_parser.py    ← DOCX / PPTX / XLSX 解析
│   └── generator/              ← 🏗️ 知识门户生成器
│       ├── __init__.py
│       ├── portal.py           ← 🆕 智能分页门户生成器（可搜索、关键词云、文档卡片）
│       └── templates.py        ← HTML 模板（首页 & 文档页，含暗黑模式/打印样式）
└── tests/
    ├── conftest.py             ← pytest 共享配置
    ├── test_parser.py          ← 解析器单元测试
    └── test_portal.py          ← 🆕 门户生成器单元测试
```

---

## 🧪 测试

```bash
# 安装测试依赖
pip install pytest

# 运行全部测试（含解析器 + 门户生成器）
pytest tests/ -v

# 仅运行门户生成器测试
pytest tests/test_portal.py -v

# 运行测试并显示详细信息
pytest tests/ -v --tb=long
```

测试覆盖：
| 测试 | 说明 |
|------|------|
| `test_parser.py` | 解析引擎测试（文本、PDF、不存在的文件） |
| `test_portal.py` | 门户生成器测试（11 项，含关键词提取、分页、排序、空文件夹等） |

> CI（GitHub Actions）中已集成 lint（ruff）和自动化测试，提交 PR 或推送 main 分支时自动运行。

---

## 💡 使用场景

- **🤖 给 Claude / GPT 喂本地知识**：将项目文档、PDF 书籍、笔记导出为 HTML，直接粘贴/上传给 AI
- **📚 知识库批量整理**：将散落的文档统一解析为结构化文本，方便存档和检索
- **🔗 RAG 预处理**：作为 RAG（检索增强生成）管道的文档加载和清洗步骤
- **🔍 文档归档检索**：配合门户模式搜索功能，在知识库中快速定位目标文档
- **🌐 Edge Copilot 知识库**：生成门户后打开 Edge 浏览器访问，按 `Ctrl+Shift+.` 唤醒 Copilot 直接提问
- **📊 企业知识抽取**：扫描合同、报告等批量文档，提取文本交给 AI 做摘要或分析

---

## ❓ 常见问题

### Q: 输出文件太大，LLM 放不下怎么办？
使用 `--max-chars` 限制输出长度，例如 `--max-chars 50000`。超出部分自动截断。建议使用门户模式，每个页面默认控制在 8000 字符。

### Q: 某些文件解析失败 / 乱码怎么办？
- 文本文件乱码：工具已自动尝试 UTF-8 → GBK → Latin-1，若仍乱码请确认文件编码
- PDF 扫描件：`pdfminer.six` 无法解析纯扫描图片，需先 OCR
- 旧版 Office（.doc / .ppt / .xls）：请另存为新版格式

### Q: 如何忽略某些文件？
目前会自动跳过 `.` 开头的隐藏文件（如 `.git`、`.DS_Store`）。如需更多过滤规则，可修改 `generate.py` 中的 `collect_files()` 函数。

### Q: 解析速度慢怎么办？
大型文件（如几百页 PDF、大 Excel）解析较慢属正常现象。CLI 门户模式支持进度条显示，可实时了解处理进度。

### Q: 文件夹里有 .exe / .zip / .mp4 等二进制文件会报错吗？
不会。工具会自动识别文件类型，仅解析支持的格式（文本、PDF、DOCX、PPTX、XLSX），其余格式自动静默跳过，不会报错或尝试读取内容。

### Q: 门户模式输出目录已存在会怎样？
不会报错。工具会提示目录已存在，然后覆盖同名文件，未改动文件会保留。

### Q: 如何安装测试依赖？
```bash
# 方式一：使用 dev extras
pip install ".[dev]"

# 方式二：直接安装 pytest
pip install pytest
```

---

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feat/xxx`)
3. 提交更改 (`git commit -m 'feat: add xxx'`)
4. 推送到分支 (`git push origin feat/xxx`)
5. 创建 Pull Request

> 代码风格：请使用 `ruff` 进行 lint 检查。

---

## 📄 许可证

本项目基于 **MIT License** 开源 — 详见 [LICENSE](LICENSE) 文件。
