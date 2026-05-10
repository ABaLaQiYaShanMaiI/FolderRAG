# FolderRAG 📁 → 📄

> **注**：本工具名称中的 "RAG" 指的是将文件夹内容整理成结构化知识包供 AI 检索阅读，而非完整的检索增强生成（Retrieval-Augmented Generation）系统。若需更精准的名称，可理解为"文件夹转 HTML 知识包"工具（Folder → Docs → HTML）。

**文件夹 → 知识 HTML 导出工具**

FolderRAG 递归扫描本地文件夹中的所有文档，自动解析 PDF、Word、Excel、PPT 和文本文件，生成一份**结构化 HTML 文件**，可直接交给任何 AI / LLM 工具（如 Claude、ChatGPT）阅读。

```bash
python generate.py ./my_folder -o knowledge.html
```

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| **📂 扫描文件夹** | 递归扫描目录下所有文件，自动跳过 `.` 开头的隐藏文件 |
| **📄 多格式解析** | PDF、DOCX、PPTX、XLSX、TXT、MD、HTML、JSON、XML 等 |
| **📝 结构化输出** | 生成 `<article>` 标签包裹的 HTML，来源路径清晰标注，AI 友好 |
| **🎯 长度控制** | `--max-chars` 参数限制输出总字符数，适配 LLM 上下文窗口 |
| **⚡ 轻量无依赖** | 无需数据库、无需向量模型、无需 Web 服务，纯 Python 脚本运行 |
| **🌐 跨平台** | Windows / macOS / Linux 均可运行 |

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

### 2️⃣ 运行

```bash
python generate.py ./文档 -o knowledge.html
```

> `./文档` 替换为你要扫描的文件夹路径，`-o knowledge.html` 指定输出文件名。

### 3️⃣ 限制输出长度（适配 LLM 上下文窗口）

```bash
python generate.py ./文档 -o knowledge.html --max-chars 50000
```

`--max-chars` 控制输出总字符数，超出部分自动截断，防止超出 LLM 的上下文限制。

---

## 📖 完整参数说明

```
usage: python generate.py [-h] -o OUTPUT [--max-chars MAX_CHARS] folder

位置参数:
  folder                要扫描的文件夹路径

选项:
  -h, --help            显示帮助信息并退出
  -o OUTPUT, --output OUTPUT
                        输出 HTML 文件路径（必需）
  --max-chars MAX_CHARS
                        输出总字符数上限（可选，默认不限）
```

### 实用示例

```bash
# 基本用法
python generate.py ./项目文档 -o output.html

# 限制输出 10 万字符（适合大部分 LLM）
python generate.py ./知识库 -o output.html --max-chars 100000

# 扫描桌面文件夹
python generate.py ~/Desktop/我的笔记 -o notes.html

# Windows 路径示例
python generate.py "C:\Users\用户名\文档" -o docs.html
```

---

## 📖 输出示例

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
- 超出长度限制时，末尾自动添加截断提示注释，例如：
  ```html
  <!-- 已达到 --max-chars 限制（50000 字符），后续文件已截断 -->
  ```

> **提示**：输出中的来源路径显示为**相对于扫描目录的相对路径**，不会泄漏用户的绝对路径隐私。

---

## 📦 支持的格式

| 格式 | 解析引擎 | 备注 |
|------|----------|------|
| TXT / MD / HTML / JSON / XML / CSV / YAML / TOML / INI / LOG / CFG 等文本文件 | 原生 UTF-8 读取 | 自动检测编码 |
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
├── generate.py               ← 📌 唯一入口，直接运行此文件
├── requirements.txt          ← 📌 依赖清单
├── LICENSE                   ← 开源许可证
├── pyproject.toml            ← 项目元数据（可 pip install 安装）
├── README.md                 ← 本文件
├── .gitignore                ← Git 忽略规则
├── .github/
│   └── workflows/
│       └── ci.yml            ← GitHub Actions CI 配置
├── src/
│   ├── __init__.py
│   └── parser/
│       ├── __init__.py
│       ├── dispatcher.py     ← MIME 类型判断 & 分派器
│       ├── text_parser.py    ← 文本文件解析
│       ├── pdf_parser.py     ← PDF 解析
│       └── office_parser.py  ← DOCX / PPTX / XLSX 解析
└── tests/
    ├── conftest.py           ← pytest 共享配置
    └── test_parser.py        ← 解析器单元测试
```

---

## 🧪 测试

```bash
# 安装测试依赖
pip install pytest

# 运行全部测试
pytest tests/ -v

# 运行测试并显示详细信息
pytest tests/ -v --tb=long
```

> CI（GitHub Actions）中已集成 lint（ruff）和自动化测试，提交 PR 或推送 main 分支时自动运行。

---

## 💡 使用场景

- **🤖 给 Claude / GPT 喂本地知识**：将项目文档、PDF 书籍、笔记导出为 HTML，直接粘贴/上传给 AI
- **📚 知识库批量整理**：将散落的文档统一解析为结构化文本，方便存档和检索
- **🔗 RAG 预处理**：作为 RAG（检索增强生成）管道的文档加载和清洗步骤
- **🔍 文档归档检索**：配合 grep 或 VS Code 全文搜索，在生成的 HTML 中快速检索关键词
- **📊 企业知识抽取**：扫描合同、报告等批量文档，提取文本交给 AI 做摘要或分析

---

## ❓ 常见问题

### Q: 输出文件太大，LLM 放不下怎么办？
使用 `--max-chars` 限制输出长度，例如 `--max-chars 50000`。超出部分自动截断。

### Q: 某些文件解析失败 / 乱码怎么办？
- 文本文件乱码：确保文件为 UTF-8 编码
- PDF 扫描件：`pdfminer.six` 无法解析纯扫描图片，需先 OCR
- 旧版 Office（.doc / .ppt / .xls）：请另存为新版格式

### Q: 如何忽略某些文件？
目前会自动跳过 `.` 开头的隐藏文件（如 `.git`、`.DS_Store`）。如需更多过滤规则，可修改 `generate.py` 中的 `collect_files()` 函数。

### Q: 解析速度慢怎么办？
大型文件（如几百页 PDF、大 Excel）解析较慢属正常现象。建议先用 `--max-chars` 控制规模。

### Q: 文件夹里有 .exe / .zip / .mp4 等二进制文件会报错吗？
不会。工具会自动识别文件类型，仅解析支持的格式（文本、PDF、DOCX、PPTX、XLSX），其余格式自动静默跳过，不会报错或尝试读取内容。

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
