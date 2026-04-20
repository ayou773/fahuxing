# 法护星 (LegalStar)

![项目logo](https://via.placeholder.com/120x60?text=LegalStar)  
**基层纠纷智慧维权 AI 助手**

一款基于人工智能技术的基层法律辅助服务平台，为普通用户提供从法律咨询、维权规划、证据收集到文书生成的一站式维权工具。无需专业法律知识，即可获取专业的法律建议和可执行的维权方案。

---

## 🚀 项目亮点

- **AI 智能法律咨询** - 深度分析纠纷事实，提供专业法律建议
- **维权时间轴规划** - 分阶段维权行动方案，清晰易懂
- **智能证据清单** - 自动生成证据材料清单和获取建议
- **文书自动生成** - 支持AI模式和表单模式生成标准起诉状
- **维权计算器** - 内置加班费、经济补偿金等实用计算工具
- **前后端分离架构** - Next.js + FastAPI，易于扩展和维护

---

## 📋 核心功能

### ⚖️ 法律咨询
- 描述纠纷事实，AI自动分析案情
- 生成专业法律建议和咨询记录ID

### 🧭 维权清单
- 按时间轴划分的维权行动方案
- 24小时、7天、30天不同阶段的行动建议
- 风险提醒和注意事项

### 🗂️ 证据清单
- 智能生成证据材料清单
- 包含证据类别、获取方式、证明目的
- 证据保全建议

### 📝 文书生成
**AI智能模式** - 调用腾讯元器API智能分析案情，自动生成起诉状  
**表单填写模式** - 手动填写或智能填充表单字段

### 🧮 维权计算器
- 加班费计算器（工作日/休息日/法定节假日）
- 经济补偿金计算器

---

## 🛠️ 技术栈

### 后端
- **FastAPI** - Python异步Web框架
- **PostgreSQL** - 关系型数据库
- **SQLAlchemy** - ORM框架
- **Pydantic** - 数据验证
- **Jinja2** - 模板引擎
- **腾讯元器API** - AI法律咨询与文书生成

### 前端
- **Next.js** - React全栈框架
- **React 18** - 前端UI框架
- **TypeScript** - 类型安全
- **TailwindCSS** - 原子化CSS框架
- **react-markdown** - Markdown渲染

---

## 🚀 快速启动

### 方式一：Docker Compose（推荐）

```bash
# 1. 复制环境变量配置
cp backend/.env.example backend/.env

# 2. 一键启动所有服务
docker compose up -d

# 3. 访问服务
# 前端: http://localhost:3000
# 后端: http://localhost:8088
# API文档: http://localhost:8088/docs
```

### 方式二：本地开发

#### 后端启动
```bash
conda activate fahuxing_env  #如果第一次运行需要自己创建一个环境推荐版本 python3.12
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8088
```

#### 前端启动
```bash
cd frontend
npm install
npm run dev
```

---

## 📊 项目架构

```
法护星/
├── backend/                    # 后端服务
│   ├── main.py                # FastAPI入口
│   ├── services/              # 业务服务层
│   │   ├── yuanqi_service.py      # 腾讯元器服务
│   │   └── document_service.py    # 文书生成服务
│   └── models/                # 数据模型
├── frontend/                  # 前端应用
│   ├── app/                   # Next.js App Router
│   └── components/            # 可复用组件
└── docker-compose.yml         # Docker编排文件
```

---

## 🔗 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/consultation` | 法律咨询 |
| POST | `/rights/checklist` | 生成维权清单 |
| POST | `/evidence/checklist` | 生成证据清单 |
| GET | `/consultations/{id}/lawsuit` | AI生成起诉状 |
| POST | `/calculator/overtime` | 加班费计算 |

---

## 📝 环境配置

### 后端环境变量
```bash
YUANQI_API_KEY=your_api_key    #在后端的。env 文件里填入自己在腾讯元器上智能体的 Key
YUANQI_ASSISTANT_ID=your_assistant_id  #在后端的 .env 文件 里填入自己的腾讯元器 Id
DATABASE_URL=postgresql+asyncpg://...
```

### 前端环境变量
```bash
YUANQI_API_KEY=your_api_key  #PS 不用修改为自己的 Key
API_BASE_URL=http://127.0.0.1:8088
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细指南。

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 📞 联系我们

如有问题或建议，欢迎通过以下方式联系：

- 项目邮箱：2186167122@qq.com
- GitHub Issues

---

> **免责声明**：法护星提供的法律建议仅供参考，不构成正式法律意见。如涉及重大法律纠纷，请咨询专业律师。