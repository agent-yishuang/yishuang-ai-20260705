# AI 项目合集

一个基于 DeepSeek API 的 AI 应用开发作品集，包含从基础对话到多步骤 Agent 的完整实现。

## 🚀 项目列表

| 项目 | 功能 | 技术栈 |
|------|------|--------|
| `ai_toolbox.py` | 20 功能 AI 工具箱（网页版） | Gradio + DeepSeek API |
| `agent_pro.py` | 多步骤 AI Agent（规划+反思） | ReAct + DeepSeek API |
| `rag_simple.py` | RAG 知识库问答 | ChromaDB + PyPDF2 |
| `daily_report.py` | AI 日报生成器 | BeautifulSoup + DeepSeek API |
| `web_search.py` | AI 联网搜索助手 | Requests + BeautifulSoup |
| `chat_bot.py` | 连续对话机器人 | DeepSeek API |
| `pdf_reader.py` | PDF 阅读助手 | PyPDF2 + DeepSeek API |

## 🛠️ 技术栈

- **语言**：Python
- **大模型**：DeepSeek API
- **网页界面**：Gradio
- **数据处理**：PyPDF2、BeautifulSoup
- **向量数据库**：ChromaDB

## 📦 运行方式

```bash
pip install gradio requests beautifulsoup4 PyPDF2 chromadb
python ai_toolbox.py
