# FolderRAG 📁 → 🔍

**基于文件夹监控的 RAG（检索增强生成）知识库系统**

FolderRAG 自动监控指定文件夹中的文件变更，实时解析文档、分块、向量化，并通过语义搜索 API 提供智能检索能力。支持文本、PDF、Office 文档和二进制文件等多种格式。

---

## 🚀 核心特性

| 特性 | 说明 |
|------|------|
| **📂 文件夹实时监控** | 利用 Watchdog 监听文件创建/修改，自动增量索引 |
| **📄 多格式解析** | 支持 TXT、PDF、DOCX、PPTX、XLSX 及二进制文件 |
| **🧩 智能分块** | 可配置的文本分块大小和重叠窗口 |
| **🔢 向量化嵌入** | 支持本地模型 (`BAAI/bge-small-zh-v1.5`) 和外部 API |
| **🗃️ 向量存储** | 基于 ChromaDB 的持久化向量数据库 |
| **🌐 RESTful API** | FastAPI 构建的高性能搜索接口 |
| **🖥️ Web UI** | 内置搜索界面，支持 Hex 预览 |
| **🐳 Docker 支持** | 一键部署 |

---

## 📋 系统架构

```
┌─────────────────────────────────────────────┐
│                 watch_folder/                │
│   (用户放置文件的目录，由 Watchdog 监控)       │
└─────────────────────┬───────────────────────┘
                      │ 文件创建/修改事件
                      ▼
┌─────────────────────────────────────────────┐
│              FolderWatcher                   │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│   │  Parser  │→ │ Chunker  │→ │ Embedder │ │
│   │ 解析文件  │  │ 文本分块  │  │ 向量化    │ │
│   └──────────┘  └──────────┘  └──────────┘ │
│                        │                    │
│                        ▼                    │
│                 ┌──────────────┐            │
│                 │ VectorStore  │            │
│                 │  (ChromaDB)  │            │
│                 └──────────────┘            │
└─────────────────────┬───────────────────────┘
                      │ 查询
                      ▼
┌─────────────────────────────────────────────┐
│              FastAPI Server                  │
│   ┌──────────┐  ┌──────────────────────┐    │
│   │ REST API │←│ Web UI (HTML+JS)     │    │
│   │  搜索接口  │  │  语义搜索前端       │    │
│   └──────────┘  └──────────────────────┘    │
└─────────────────────────────────────────────┘
```

---

## 🛠️ 快速开始

### 环境要求

- Python 3.9+
- （可选）Docker

### 1️⃣ 本地安装

```bash
# 克隆仓库
git clone https://github.com/your-username/FolderRAG.git
cd FolderRAG

# 创建虚拟环境（推荐）
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2️⃣ 配置环境变量

```bash
# 复制配置模板
cp .env.example .env
# 编辑 .env 文件，按需修改配置
```

**.env 配置说明：**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `HOST` | `0.0.0.0` | 服务监听地址 |
| `PORT` | `8000` | 服务端口 |
| `WATCH_DIR` | `./watch_folder` | 要监控的文件夹路径 |
| `EMBEDDER_BACKEND` | `local` | 嵌入后端：`local` 或 `deepseek` |
| `DEEPSEEK_API_KEY` | - | 使用 DeepSeek 时需要 |
| `VECTOR_DB_PATH` | `./data/chroma_db` | 向量数据库持久化路径 |
| `CHUNK_SIZE` | `500` | 文本分块大小（近似字符数） |
| `CHUNK_OVERLAP` | `50` | 分块重叠窗口 |

### 3️⃣ 启动服务

```bash
# 确保 watch_folder 目录存在
mkdir watch_folder

# 启动服务
python src/main.py
```

访问 **http://localhost:8000** 打开 Web 搜索界面。

### 4️⃣ 使用 Docker

```bash
# 构建镜像
docker build -t folderrag .

# 运行容器
docker run -d \
  --name folderrag \
  -p 8000:8000 \
  -v $(pwd)/watch_folder:/app/watch_folder \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env:/app/.env \
  folderrag
```

---

## 📚 API 文档

### 语义搜索

```bash
curl -X POST http://localhost:8000/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "你的搜索内容", "k": 5}'
```

**请求参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `query` | string | ✅ | - | 搜索查询文本 |
| `k` | integer | ❌ | `5` | 返回结果数量 |
| `filters` | object | ❌ | `null` | 过滤条件（暂未使用） |

**响应示例：**

```json
{
  "results": [
    {
      "id": "chunk_id",
      "text": "匹配的文本内容...",
      "source": "文件路径",
      "offset": 0,
      "score": 0.92,
      "mime": "application/pdf",
      "extract_type": "text",
      "hex_preview": null
    }
  ]
}
```

### 获取文档详情

```bash
curl http://localhost:8000/v1/doc/{doc_id}
```

### 健康检查

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

---

## 📂 项目结构

```
FolderRAG/
├── src/
│   ├── __init__.py          # 包初始化
│   ├── main.py              # 主入口，协调各模块
│   ├── watcher.py           # 文件夹监控（Watchdog 调度）
│   ├── chunker.py           # 文本分块引擎
│   ├── embedder.py          # 向量化嵌入（本地/API）
│   ├── vector_store.py      # ChromaDB 向量存储封装
│   ├── parser/
│   │   ├── __init__.py      # 解析器调度（MIME 分发）
│   │   ├── text_parser.py   # 纯文本解析
│   │   ├── pdf_parser.py    # PDF 文本提取
│   │   ├── office_parser.py # Office文档 (DOCX/PPTX/XLSX)
│   │   └── binary_handler.py# 二进制文件（Hex预览+ASCII提取）
│   ├── api/
│   │   ├── __init__.py
│   │   ├── server.py        # FastAPI 应用与路由
│   │   └── schemas.py       # Pydantic 数据模型
│   └── web/
│       ├── static/
│       │   ├── index.html   # 搜索前端界面
│       │   └── app.js       # 前端逻辑
│       └── templates/
│           └── search_results.html  # 模板占位
├── tests/
│   ├── test_api.py          # API 接口测试
│   └── test_parser.py       # 解析器单元测试
├── config.yaml              # 全局配置（嵌入、分块、向量存储等）
├── .env.example             # 环境变量模板
├── requirements.txt         # Python 依赖
├── Dockerfile               # Docker 构建文件
├── .dockerignore            # Docker 构建忽略列表
├── .gitignore               # Git 忽略列表
├── LICENSE                  # MIT 许可证
└── README.md                # 本文档
```

---

## ⚙️ 配置详解

### `config.yaml` 主要配置

```yaml
chunk:
  max_tokens: 500           # 每个块的最大字符数
  overlap_tokens: 50        # 块之间的重叠字符数

embedder:
  backend: local            # local 或 deepseek
  model_name: BAAI/bge-small-zh-v1.5  # 本地模型名
  batch_size: 32            # 批处理大小

vector_store:
  type: chroma
  persist_directory: ./data/chroma_db  # 向量数据库存储路径

binary:
  hex_preview_bytes: 8192   # 二进制文件 Hex 预览字节数
  index_ascii_segments: true # 是否索引可打印 ASCII 段
```

---

## 🧪 测试

```bash
# 安装测试依赖
pip install pytest

# 运行测试
pytest tests/ -v

# 指定测试
pytest tests/test_api.py -v
```

---

## 📦 支持的文档格式

| 格式 | MIME 类型 | 解析引擎 |
|------|-----------|----------|
| TXT, MD, etc. | `text/*` | 原生文本读取 |
| PDF | `application/pdf` | `pdfminer.six` |
| DOCX | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | `python-docx` |
| PPTX | `application/vnd.openxmlformats-officedocument.presentationml.presentation` | `python-pptx` |
| XLSX | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | `openpyxl` |
| 二进制文件 | 其他 | 可打印 ASCII 提取 + Hex 预览 |

---

## 🔧 技术栈

| 组件 | 技术 |
|------|------|
| Web 框架 | [FastAPI](https://fastapi.tiangolo.com/) |
| 文件监控 | [Watchdog](https://github.com/gorakhargosh/watchdog) |
| 向量数据库 | [ChromaDB](https://www.trychroma.com/) |
| 嵌入模型 | [Sentence-Transformers](https://www.sbert.net/) |
| PDF 解析 | [pdfminer.six](https://github.com/pdfminer/pdfminer.six) |
| Office 解析 | python-docx / python-pptx / openpyxl |
| 请求重试 | [Tenacity](https://tenacity.readthedocs.io/) |
| 容器化 | Docker |
| 测试 | Pytest |

---

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 🌟 路线图

- [ ] 支持更多嵌入后端（OpenAI、Voyage、Cohere）
- [ ] 基于 XLSX/CSV 的结构化数据索引
- [ ] 增量删除/重命名文件同步
- [ ] 多模态支持（图片 OCR）
- [ ] 高性能批量索引模式
- [ ] 中文/英文混合搜索优化
- [ ] 可视化索引状态仪表盘

---

> **FolderRAG** — 让文件夹变成可搜索的知识库，开启 RAG 应用的第一公里。
