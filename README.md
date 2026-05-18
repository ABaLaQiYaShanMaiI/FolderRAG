> ⚠️ **重要提示 / Important Note**  
> **此项目为所有 AI 场景设计 —— 无论是粘贴到对话窗口，还是让网页 AI 直接读取**  
> **This project is designed for all AI scenarios — paste into chat windows or let browser AI read natively**  
>
> - **TXT 模式**：纯文本输出，可直接粘贴到任意 AI 对话窗口  
> - **分片模式**：超大型项目自动拆分，避免溢出 LLM 上下文  
> - **Portal 模式**：单页 HTML，浏览器 AI 可直接读取分析  
> 无需插件、文件上传或 API 调用。  
>  
> - **TXT Mode**: Plain text output, ready to paste into any LLM chat  
> - **Chunked Mode**: Automatically split large projects into manageable TXT files  
> - **Portal Mode**: Single-page HTML, directly readable by browser-based AI  
> No plugins, file uploads, or API calls required.

---

# FolderKnowledgeSiteGeneratorForAI 📁 → 🌐

[![PyPI Version](https://img.shields.io/badge/pypi-v2.2.0-blue)](https://pypi.org/project/FolderKnowledgeSiteGeneratorForAI/)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**一键将文件夹转为 AI 可读的知识门户或分片文本，无需服务器与 API。**  
**Turn any folder into AI-readable knowledge portals or chunked text — no server, no API.**

---

## 🚀 快速开始 / Quick Start

```bash
# 安装依赖
pip install -r requirements.txt

# 🖥️ 图形界面（推荐 Windows）
python gui.py [文件夹路径]

# ⌨️ 命令行
python generate.py my_folder -o out.txt                         # TXT 导出
python generate.py my_folder --split-chunks -o chunked_out/      # 分片导出
python generate.py my_folder --portal -o portal_out/             # 门户模式
```

> **Windows**：双击 `start.cmd` 启动 GUI | **Linux/macOS**：运行 `bash start.sh`

---

## 📊 输出模式 / Output Modes

| 模式 | 命令 | 输出 | 适用场景 |
|------|------|------|----------|
| 🗂️ **TXT** | 默认 | 纯文本（`.txt`） | 粘贴到 ChatGPT、DeepSeek、Claude 等对话窗口 |
| 📦 **分片** | `--split-chunks` | 多个 `part_NNN.txt` + 索引 | 超大型项目自动拆分，避免溢出 LLM 上下文 |
| 🏛️ **Portal** | `--portal` | 单页 HTML（可搜索、折叠、文件树） | 浏览器 AI（Edge Copilot / ChatGPT Web）直接读取 |

---

## 🏛️ Portal 特性 / Portal Features

- **可折叠文件块** — 每个文件默认为折叠状态，点击展开
- **Expand All / Collapse All** — 一键展开/收起所有内容
- **实时搜索** — 按文件名、标签、内容搜索，文件树同步高亮
- **文件树导航** — ASCII 风格，点击跳转
- **关键词云** — 自动提取，点击过滤
- **中英双语** — 右上角切换，偏好自动保存
- **暗黑模式** — 自动跟随系统，统一适配搜索/按钮/badge
- **打印友好** — 打印时自动展开所有内容

---

## 📦 分片模式 / Chunked Mode

超大项目安全分割为多个 TXT 文件，每个可直接粘贴到 AI 对话。

| 参数 | 默认 | 说明 |
|------|------|------|
| `--chunk-size` | 500,000 | 每片字符数（设为 0 不限） |
| `--max-chars` | 不限 | 总字符数上限 |

**输出结构：**
```
output_dir/
├── part_001.txt          # 分片内容（保持文件级完整性，不从中切开）
├── part_002.txt
├── ...
├── <文件夹名>_index.html  # 交互式索引
└── _manifest.txt          # 纯文本清单
```

---

## 🖥️ 图形界面 / GUI

| 功能 | 说明 |
|------|------|
| 📂 **文件夹选择** | 浏览、粘贴或拖拽，快捷键 `Ctrl+O` |
| 🔄 **模式切换** | Single TXT / Split TXT / Portal，自动调整 UI |
| 🚀 **一键生成** | 进度条实时反馈，快捷键 `Ctrl+G` |
| 🌐 **中英双语** | 即时切换，偏好自动保存 |
| 📋 **实时文件列表** | 显示文件、大小、状态 |
| ▶️ **HTTP 服务器** | 生成后一键启动本地服务器供 AI 读取 |
| 📂 **拖拽支持** | 支持文件夹拖入 GUI（需 tkinterdnd2） |

---

## 📦 支持格式 / Supported Formats

| 类别 | 格式 |
|------|------|
| 纯文本/标记 | `.txt`, `.md`, `.html`, `.json`, `.xml`, `.csv`, `.yaml`, `.toml`, `.ini` 等 |
| Office 文档 | `.docx`, `.pptx`, `.xlsx`（需 `python-docx`, `python-pptx`, `openpyxl`） |
| PDF | `.pdf`（需 `pdfminer.six`） |
| 代码文件 | `.py`, `.js`, `.ts`, `.java`, `.cs`, `.swift`, `.kt`, `.rs`, `.go` 等 50+ 种 |
| 自动跳过 | `.exe`, `.dll`, `.zip`, `.jpg`, `.png`, `.mp4`, `.log`, `__pycache__` 等 |

---

## ⌨️ CLI 参数 / CLI Reference

```
usage: python generate.py [-h] -o OUTPUT [--portal] [--no-skipped]
                          [--max-chars-per-file MAX_CHARS_PER_FILE]
                          [--log-file LOG_FILE] [--split-chunks]
                          [--chunk-size CHUNK_SIZE] [--max-chars MAX_CHARS]
                          [--lang {en,zh}]
                          folder
```

| 参数 | 说明 |
|------|------|
| `folder` | 要扫描的文件夹路径 |
| `-o, --output` | TXT 模式：输出文件路径；分片/门户模式：输出目录 |
| `--portal` | 门户模式 |
| `--split-chunks` | 分片模式 |
| `--chunk-size N` | 分片最大字符数（默认 500,000） |
| `--max-chars N` | 分片模式总字符上限 |
| `--no-skipped` | 门户模式不显示跳过文件标记 |
| `--max-chars-per-file N` | 门户模式单文件字符上限（默认 50,000） |
| `--lang {en,zh}` | 输出语言（默认 en） |
| `--log-file FILE` | 日志写入文件 |

---

## 🤝 贡献 / Contributing

- **代码风格**：`ruff check src/ tests/`
- **运行测试**：`pytest tests/ -v`
- **提交规范**：feature branch → PR → main

---

## 📄 许可证 / License

[MIT](LICENSE)

---

<p align="center">
  <sub>⭐ <a href="https://github.com/ABaLaQiYaShanMaiI/FolderKnowledgeSiteGeneratorForAI">Star on GitHub</a> if you find this useful!</sub>
  <br>
  <sub>Made with ❤️ by <a href="https://github.com/ABaLaQiYaShanMaiI">ABaLaQiYaShanMaiI</a></sub>
</p>