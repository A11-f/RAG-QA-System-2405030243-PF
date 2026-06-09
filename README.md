# RAG 智能问答系统

基于本地知识库的智能问答系统，使用 Streamlit、LangChain 和 Ollama 构建，支持文档上传、向量检索和多轮对话。

## ✨ 功能特点

- 📄 **文档上传**：支持 PDF 和 DOCX 格式文档的批量上传
- 🧠 **本地推理**：使用 Ollama 本地模型进行问答，无需联网
- 🔍 **智能检索**：基于向量检索的上下文理解，返回最相关的文档片段
- 💬 **多轮对话**：支持对话历史记忆，实现连续问答
- 📊 **实时状态**：显示知识库中文档数量、文本块数量和处理耗时
- ⚡ **性能优化**：嵌入缓存机制、向量数据库持久化、相似度分数显示

## 🔧 环境要求

- Python 3.9+
- Ollama 服务（已安装 qwen2:7b 或 deepseek-r1:7b 模型）
- Windows 10/11 / Linux / macOS

## 🚀 安装步骤

### 1. 安装 Ollama

1. 下载 Ollama：https://ollama.com/download
2. 安装后，在终端运行以下命令下载模型：

```bash
# 下载大语言模型（二选一）
ollama pull qwen2:7b    # 推荐，性能均衡
ollama pull deepseek-r1:7b  # 推理能力更强

# 下载嵌入模型
ollama pull nomic-embed-text
```

### 2. 安装 Python 依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 运行应用

```bash
streamlit run app.py
```

应用启动后，打开浏览器访问 http://localhost:8501

## 📖 使用说明

### 基本流程

1. **构建知识库**
   - 在左侧栏上传 PDF 或 DOCX 文档
   - 或勾选「使用示例文档」使用内置的5份NLP示例文档
   - 点击「构建知识库」按钮

2. **提问**
   - 在右侧输入框中输入问题
   - 点击「提问」按钮
   - 等待回答生成

3. **查看结果**
   - 回答会显示在对话历史中
   - 点击「详细信息」展开可查看参考来源和相似度分数

### 示例问题

```
什么是自然语言处理？
词向量是什么？
Transformer的主要结构是什么？
BERT模型有什么特点？
如何进行文本分类？
```

## 🔍 关键技术点

### RAG 流程

```
文档上传 → 文本提取 → 文本分块 → 向量化 → 向量存储 → 检索 → 生成回答
```

### 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 大语言模型 | Ollama + Qwen2:7b | 本地推理，无需联网 |
| 嵌入模型 | nomic-embed-text | 生成文本向量表示 |
| 向量存储 | 自定义实现 | 支持持久化和缓存 |
| Web 框架 | Streamlit | 快速构建交互式界面 |
| 文档处理 | PyPDF2 + python-docx | PDF和DOCX解析 |

### 核心参数

- **chunk_size**: 1000 - 文本分块大小
- **chunk_overlap**: 200 - 分块重叠大小
- **top_k**: 3 - 返回最相关的文档数量
- **temperature**: 0.1 - 生成温度（越低越精确）

## 📁 项目结构

```
.
├── app.py                 # Streamlit Web 应用主入口
├── config.py              # 配置文件（路径、模型、参数）
├── document_loader.py     # 文档加载模块（PDF/DOCX解析）
├── vector_store.py        # 向量存储模块（嵌入缓存、持久化）
├── rag_chain.py           # RAG 问答链模块（提示词、检索）
├── test_ollama.py         # Ollama API 测试脚本
├── test_rag.py            # RAG 系统测试脚本
├── create_sample_docs.py  # 示例文档生成脚本
├── requirements.txt       # 依赖包列表
├── .gitignore            # Git 忽略配置
├── README.md             # 项目说明文档
├── data/                  # 示例文档目录
├── vector_db/             # 向量数据库存储（自动生成）
└── local_uploads/        # 本地上传文件目录（自动生成）
```

## 📊 性能优化

1. **嵌入缓存**：使用 MD5 哈希缓存已计算的嵌入向量，避免重复计算
2. **向量持久化**：支持将向量数据库保存到磁盘，重启后自动加载
3. **相似度阈值**：过滤低相似度的文档，提高回答质量
4. **超时处理**：设置合理的请求超时时间，提升系统稳定性

## 📈 回答质量保障

1. **严格基于文档**：回答必须引用参考文档内容
2. **明确来源**：显示参考来源和相似度分数
3. **拒绝编造**：文档中没有相关信息时明确说明
4. **温度控制**：较低的温度参数确保回答更精确

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📝 更新日志

### v1.0.0
- 初始版本发布
- 支持 PDF/DOCX 文档上传
- 基于 Ollama 的本地推理
- Streamlit Web 界面
- 向量数据库持久化
- 嵌入缓存机制