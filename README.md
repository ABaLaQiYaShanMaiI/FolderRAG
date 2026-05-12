> ⚠️ **重要提示 / Important Note**  
> **此项目为所有 AI 场景设计 —— 无论是粘贴到对话窗口，还是让网页 AI 直接读取**  
> **This project is designed for all AI scenarios — paste into chat windows or let browser AI read natively**  
>
> - **TXT 模式**：纯文本输出，可直接粘贴到 Claude、ChatGPT、DeepSeek 等任意对话窗口  
> - **分片模式**：按固定字符数自动拆分到多个 TXT 文件，避免单文件过大溢出 LLM 上下文  
> - **Portal 模式**：单页 HTML，Edge Copilot、ChatGPT Web 等浏览器 AI 可直接读取和分析  
> 无需插件、文件上传或 API 调用。  
>  
> - **TXT Mode**: Plain text output, ready to paste into any LLM chat (Claude, ChatGPT, DeepSeek, etc.)  
> - **Chunked Mode**: Automatically split into multiple TXT files by character count, preventing oversized files from overflowing LLM context  
> - **Portal Mode**: Single-page HTML, directly readable by browser-based AI (Edge Copilot, ChatGPT Web, etc.)  
> No plugins, file uploads, or API calls required.

---

# FolderKnowledgeSiteGeneratorForAI 📁 → 🌐

[![PyPI Version](https://img.shields.io/badge/pypi-v2.1.0-blue)](https://pypi.org/project/FolderKnowledgeSiteGeneratorForAI/)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-129%20passed-brightgreen)](tests/)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-7B3F00)](pyproject.toml)

> **将任意文件夹一键变为 AI 可读的知识门户、分片文本或多页索引，无需服务器与 API。**

---

## 🧠 核心理念 / Core Philosophy

**零依赖 · 零后端 · 零模型** —— 不运行 AI 模型、不调用 API、不启动后台服务。

**三种消费方式 / Three Consumption Modes：**

| 模式 | 输出 | 适用场景 |
|------|------|----------|
| 🗂️ **TXT 模式** | 纯文本（`.txt`） | 直接粘贴到 ChatGPT、DeepSeek、Claude 等对话窗口 |
| 📦 **分片模式** | 多个 `.txt` + 索引 HTML | 超大型项目自动拆分，避免溢出 LLM 上下文 |
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
python generate.py my_folder -o out.txt                        # TXT 导出（完整内容）
python generate.py my_folder --split-chunks -o chunked_out/    # 分片导出（自动拆分）
python generate.py my_folder --portal -o portal_out/           # 门户模式
```

> 🪟 **Windows 用户**：也可直接双击 `start.cmd` 一键启动图形界面。  
> 🐧 **Linux/macOS 用户**：运行 `bash start.sh`。

---

## 📊 输出模式对比表 / Output Mode Comparison

| 模式 | 命令参数 | 输出格式 | 适用场景 |
|------|---------|---------|----------|
| 🗂️ **TXT 导出** | 默认（`-o out.txt`） | 纯文本，每个文件用分隔线隔开 | 复制到 ChatGPT、DeepSeek 等对话 |
| 📦 **分片导出** | `--split-chunks -o out_dir/` | 多个 `part_NNN.txt` + 索引 HTML | 超大型项目，避免单文件溢出上下文 |
| 🏛️ **知识门户** | `--portal -o out_dir/` | 单页 HTML（含搜索、文件树、可折叠代码块） | Edge Copilot 等浏览器 AI 直接阅读 |

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
| 🔄 **模式切换** | 单文件 TXT / 分片 TXT / 门户模式，切换时自动调整 UI 设置项 |
| 🚀 **一键生成** | 点击生成按钮，进度条实时反馈，快捷键 `Ctrl+G` |
| 🌐 **中英双语** | 界面右上角 EN/中文 按钮即时切换，偏好自动保存 |
| 📋 **实时文件列表** | 扫描后显示所有文件及其大小、状态（支持/跳过） |
| 🧹 **Clear 按钮** | 一键清空当前文件夹加载状态 |
| ▶️ **HTTP 服务器** | 门户/分片生成后可直接启动本地服务器供 AI 读取 |
| 📂 **拖拽支持** | 支持文件夹拖入 GUI（需 tkinterdnd2） |

### 三种模式 / Three Modes

| 模式 | 说明 | 输出 |
|------|------|------|
| 🗂️ **Single TXT** | 单文件 TXT，所有内容合并为一个文件 | `.txt` 文件 |
| 📦 **Split TXT** | 分片模式，按字符数自动拆分为多个文件 | `part_*.txt` + 索引 HTML |
| 🏛️ **Portal** | 可搜索的单页知识门户 | `index.html` + 文档页 |

> **Single TXT 模式始终输出完整内容**。对于超大型文件夹，请使用 **Split TXT** 模式自动分片，避免单文件溢出 LLM 上下文。

> **GUI 中的 Split TXT 模式**与命令行 `--split-chunks` 使用相同的分片引擎。设置好输出目录与分片大小（默认 500,000 字符），勾选 "Force split" 可强制切分超大文件。

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
usage: python generate.py [-h] -o OUTPUT [--portal] [--no-skipped]
                          [--max-chars-per-file MAX_CHARS_PER_FILE]
                          [--log-file LOG_FILE] [--split-chunks]
                          [--chunk-size CHUNK_SIZE] [--max-chars MAX_CHARS]
                          [--lang {en,zh}]
                          folder
```

### 通用参数

| 参数 | 说明 |
|------|------|
| `folder` | 要扫描的文件夹路径（位置参数） |
| `-o, --output` | TXT 模式：输出文件路径；分片/门户模式：输出目录 |
| `--log-file LOG_FILE` | 将详细日志写入指定文件 |

### TXT 模式（默认）

| 参数 | 说明 |
|------|------|
| *（无额外参数）* | 始终输出完整内容，不支持截断 |

> ⚠️ `--max-chars` 在 TXT 模式下已无效（不再截断），仅用于分片模式。

### 分片模式（--split-chunks）

| 参数 | 说明 |
|------|------|
| `--split-chunks` | 启用分片模式，按固定大小将内容拆分到多个文件 |
| `--chunk-size CHUNK_SIZE` | 每个分片的最大字符数（默认 500,000，设为 0 不限） |
| `--max-chars MAX_CHARS` | 所有分片的总字符数上限（默认不限，超出则截断最后一文件） |

### 门户模式（--portal）

| 参数 | 说明 |
|------|------|
| `--portal` | 启用门户模式，生成可搜索的单页知识门户 |
| `--no-skipped` | 不在首页中显示不支持的文档标记 |
| `--max-chars-per-file MAX_CHARS_PER_FILE` | 单文件最大字符数（默认 50,000，设为 0 不限） |
| `--lang, --language` | 输出语言（en/zh，默认 en） |


---

## 📦 分片模式详解 / Chunked Mode Details

分片模式将超大知识库安全地分割为多个小型 TXT 文件，每个文件可直接粘贴到 AI 对话中。

### 核心特性

| 特性 | 说明 |
|------|------|
| ✅ **文件级完整性** | 绝不从文件中间切开，超阈值时下一文件开启新分片 |
| ✅ **超大文件专用分片** | 单文件超过分片大小时独占一个分片并给出警告 |
| ✅ **字符数分片** | 默认 500,000 字符，稳定不受编码影响 |
| ✅ **索引 HTML** | 交互式 HTML 列出每个分片包含的文件，方便按需提交 |
| ✅ **纯文本清单** | `_manifest.txt` 列出分片文件和对应的源文件 |

### 输出结构

```
output_dir/
├── part_001.txt              # 分片内容（每个文件完整）
├── part_002.txt
├── ...
├── <源文件夹名>_index.html   # 交互式索引
└── _manifest.txt             # 纯文本清单
```

### 使用流程

```
1. python generate.py my_project --split-chunks --chunk-size 500000 -o chunked_out/
2. 打开 chunked_out/my_project_index.html 查看分片概览
3. 将 part_001.txt 内容粘贴到 AI → 继续 part_002.txt → ...
4. 每个分片的开头包含上下文提示，方便 AI 理解关系
```

---

## ✨ 高级特性与最新改进 (v2.1.x) / Advanced Features & Latest Improvements

| 改进 | 说明 |
|------|------|
| 🔄 **分片模式** | 新增 `--split-chunks`，按字符数自动分片，告别单文件截断 |
| 🗑️ **移除简陋截断** | `--max-chars` 在 TXT 模式不再生效，改为分片模式下全局上限 |
| 📁 **输出命名规范化** | 索引 HTML 和输出文件夹均以源文件夹命名，一目了然 |
| 🔄 **过滤规则统一** | TXT 与 Portal 共享相同的文件/目录过滤逻辑，来自 `src/constants.py` |
| 🔒 **安全的 CSS 选择器** | 文件名特殊字符通过 `CSS.escape()` polyfill 处理 |
| 🛡️ **更强的 parser 容错** | `python-magic` 加载失败时自动回退到扩展名检测 |
| 📋 **清晰的 skip 报告** | 生成结束后打印被跳过文件的分类原因 |
| 🧰 **`src/utils.py` 抽取** | `human_readable_size` 等工具函数集中管理 |
| 📝 **模板变量化** | `index_page.html` 使用 `$placeholder` 标准占位符 |
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
│   ├── chunker/
│   │   └── __init__.py      # 分片引擎（按字符数自动分片）
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
│   ├── test_cli.py          # CLI 入口测试（含分片模式测试）
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
| 🧩 **超大型项目** | 用 `--split-chunks` 自动分片，按顺序提交给 AI |
| 🔄 **CI/CD 文档快照** | 配合 GitHub Actions 生成文档快照 |

### 在 Edge Copilot 中使用 / Use with Edge Copilot

```
1. 门户模式生成知识门户
2. 在 Edge 浏览器中双击打开 index.html
3. 点击 "🤖 Expand All (AI Mode)" 展开所有内容
4. 按 Ctrl+Shift+. 唤醒 Edge Copilot
5. Copilot 自动读取当前页面全部内容，直接提问
```

### 分片模式与 AI 对话 / Chunked Mode with AI Chat

```
1. 生成分片文件：python generate.py project/ --split-chunks -o chunks/
2. 打开索引 HTML 了解文件分布
3. 将 part_001.txt 粘贴到 AI → AI 形成初步认知
4. 继续粘贴 part_002.txt → AI 自动整合上下文
5. 每个分片顶部包含上下文标记，确保连续性
```

---

## 🧪 测试 / Testing

```bash
# 运行全部测试
pytest tests/ -v

# 测试覆盖：parser、CLI（含分片模式）、portal generator
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
| **为什么 TXT 模式不再支持 `--max-chars` 截断？** | 截断会破坏文件完整性，导致 AI 无法正确理解。改为 `--split-chunks` 分片模式，确保每个文件完整。 |
| **分片模式下如何控制总输出大小？** | 使用 `--max-chars` 作为全局上限，超出时会截断最后一文件的末尾部分。 |
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