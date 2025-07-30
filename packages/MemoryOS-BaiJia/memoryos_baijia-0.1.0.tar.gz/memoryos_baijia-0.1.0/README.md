# MemoryOS

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

一个智能记忆管理系统，为对话式 AI 提供短期、中期和长期记忆存储与检索功能。

## ✨ 特性

- **多层记忆架构**：短期记忆、中期记忆、长期记忆的分层管理
- **智能检索**：基于语义相似度和时间衰减的记忆检索
- **用户画像**：自动分析用户特性和偏好
- **知识提取**：从对话中提取用户私有数据和助手知识
- **热点分析**：基于访问频率和交互强度的记忆热度计算
- **OpenAI 集成**：完全兼容 OpenAI API
- **向量搜索**：基于 FAISS 的高效向量检索
- **Web 支持**：内置 Flask 支持，便于集成

## 🚀 快速开始

### 安装

```bash
pip install memoryos
```

安装时会自动安装所有必需的依赖包：
- `openai` - OpenAI API 客户端
- `numpy` - 数值计算
- `sentence-transformers` - 文本向量化
- `faiss-gpu` - 高效向量搜索
- `Flask` - Web 框架支持
- `httpx[socks]` - HTTP 客户端

### 基本使用

```python
from memoryos import Memoryos

# 初始化记忆系统
memory = Memoryos(
    user_id="user123",
    openai_api_key="your-openai-api-key",
    data_storage_path="./data"
)

# 添加对话记忆
memory.add_memory(
    user_input="你好，我是张三",
    agent_response="你好张三，很高兴认识你！"
)

# 生成响应（会自动检索相关记忆）
response = memory.get_response(
    query="我之前告诉过你我的名字吗？",
    relationship_with_user="friend"
)
print(response)
```

## 📖 详细配置

```python
memory = Memoryos(
    user_id="user123",                    # 用户标识
    assistant_id="assistant_v1",          # 助手标识
    openai_api_key="sk-xxx",             # OpenAI API 密钥
    openai_base_url="https://api.openai.com/v1",  # API 基地址（可选）
    data_storage_path="./data",          # 数据存储路径
    short_term_capacity=10,              # 短期记忆容量
    mid_term_capacity=2000,              # 中期记忆容量
    long_term_knowledge_capacity=100,    # 长期记忆知识容量
    llm_model="gpt-4o-mini"             # 使用的 LLM 模型
)
```

## 🏗️ 系统要求

- Python 3.8+
- 支持 GPU 的环境（推荐，用于 FAISS 加速）
- OpenAI API 密钥

## 📁 数据存储结构

```
data/
├── users/
│   └── user123/
│       ├── short_term.json     # 短期记忆
│       ├── mid_term.json       # 中期记忆
│       └── long_term_user.json # 用户长期记忆
└── assistants/
    └── assistant_v1/
        └── long_term_assistant.json  # 助手知识库
```

## 📄 许可证

MIT License

---

如有问题，请通过邮件联系：your.email@example.com

