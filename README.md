# FolderRAG 📁 → 📄

**文件夹 → 知识 HTML 导出工具**

FolderRAG 扫描本地文件夹中的所有文档，自动解析 PDF、Word、Excel、PPT 和文本文件，生成一份**结构化 HTML 文件**，可直接交给任何 AI/LLM 工具阅读。

```bash
python generate.py ./my_folder -o knowledge.html
```

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| **📂 扫描文件夹** | 递归扫描目录下所有文件 |
| **📄 多格式解析** | PDF、DOCX、PPTX、XLSX、TXT、MD、HTML 等 |
| **📝 结构化输出** | 生成 `<article>` 标签包裹的 HTML，AI 友好 |
| **🎯 长度控制** | `--max-chars` 参数限制输出总字符数 |
| **⚡ 轻量无依赖** | 无需数据库、无需向量模型、无需 Web 服务 |

---

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 解析文件夹，输出 HTML
python generate.py ./文档 -o knowledge.html

# 控制输出长度（适合 LLM 上下文窗口）
python generate.py ./文档 -o knowledge.html --max-chars 50000
```

---

## 📖 输出示例

生成的 `knowledge.html` 结构如下：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>Knowledge Export</title>
</head>
<body>
  <h1>文件夹知识导出</h1>
  <p>来源：C:\Users\...\文档</p>
  <hr>

  <article>
    <h2>来源：技术文档/设计说明.pdf</h2>
    <p>正文内容......</p>
  </article>

  <article>
    <h2>来源：报告/2024年度总结.docx</h2>
    <p>正文内容......</p>
  </article>
</body>
</html>
```

每个文件独立一个 `<article>` 区块，标题带有来源路径，AI 工具可以清晰分辨不同来源。

---

## 📂 项目结构

```
FolderRAG/
├── generate.py               ← 唯一入口
├── requirements.txt          ← 依赖清单
├── src/
│   └── parser/
│       ├── __init__.py
│       ├── dispatcher.py     ← MIME 分派器
│       ├── text_parser.py    ← 文本文件解析
│       ├── pdf_parser.py     ← PDF 解析
│       └── office_parser.py  ← DOCX/PPTX/XLSX 解析
├── tests/
│   └── test_parser.py        ← 解析器测试
└── README.md
```

---

## 📦 支持的格式

| 格式 | 解析引擎 |
|------|----------|
| TXT / MD / HTML / JSON / XML… | 原生 UTF-8 读取 |
| PDF | `pdfminer.six` |
| DOCX (Word) | `python-docx` |
| PPTX (PowerPoint) | `python-pptx` |
| XLSX (Excel) | `openpyxl` |
| 其他格式 | 跳过（静默忽略） |

---

## 🧪 测试

```bash
pytest tests/ -v
```

---

## 🤝 使用场景

- **给 Claude/GPT 喂本地知识**：将项目文档、PDF 书籍、笔记导出为 HTML，直接粘贴给 AI
- **知识库批量整理**：将散落的文档统一解析为结构化文本
- **RAG 预处理**：作为 RAG 管道的文档加载和清洗步骤
- **文档归档检索**：配合 grep 或全文搜索工具使用
