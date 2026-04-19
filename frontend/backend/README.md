# 法护星后端服务

## 概述

法护星后端服务提供以下功能：
- 劳资计算器（加班费、经济补偿金、五险一金、个税计算）
- 诉状生成（整合元器API和DeepSeek API）
- PDF导出功能

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并配置：

```bash
cp .env.example .env
# 编辑 .env 文件，填写API密钥
```

### 3. 启动服务

```bash
python main.py
```

服务将运行在 `http://localhost:8000`

## API端点

### 计算器API

- `POST /api/calculator/calculate/overtime` - 计算加班费
- `POST /api/calculator/calculate/severance` - 计算经济补偿金  
- `POST /api/calculator/calculate/social-insurance` - 计算五险一金
- `POST /api/calculator/calculate/individual-tax` - 计算个人所得税
- `POST /api/calculator/calculate/all` - 综合计算所有项目

### 诉状生成API

- `POST /api/lawsuit/generate/lawsuit` - 生成诉状
- `POST /api/lawsuit/generate/calculation-report` - 生成计算报告
- `POST /api/lawsuit/export/pdf` - 导出内容为PDF

### 健康检查

- `GET /health` - 健康检查
- `GET /` - 根路径

## 环境变量

| 变量名 | 描述 | 示例 |
|--------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | your_deepseek_api_key |
| `YUANQI_API_KEY` | 元器API密钥 | your_yuanqi_api_key |
| `YUANQI_ASSISTANT_ID` | 元器Assistant ID | your_assistant_id |
| `PORT` | 服务端口 | 8000 |
| `HOST` | 服务主机 | 0.0.0.0 |
| `PDF_OUTPUT_DIR` | PDF输出目录 | ./pdf_outputs |
| `PDF_TEMPLATE_DIR` | PDF模板目录 | ./templates |

## 目录结构

```
backend/
├── main.py                 # 主应用入口
├── requirements.txt        # 依赖包列表
├── .env                    # 环境变量配置
├── services/               # 服务层
│   ├── calculator_service.py    # 计算器服务
│   ├── deepseek_service.py      # DeepSeek服务
│   ├── pdf_generator.py        # PDF生成器
│   └── lawsuit_service.py       # 诉状生成服务
├── routers/                # 路由层
│   ├── calculator_router.py     # 计算器路由
│   └── lawsuit_router.py        # 诉状生成路由
└── templates/              # PDF模板目录
```

## 使用示例

### 计算加班费

```python
import requests

url = "http://localhost:8000/api/calculator/calculate/overtime"
data = {
    "base_salary": 8000,
    "overtime_hours": 20
}

response = requests.post(url, json=data)
print(response.json())
```

### 生成诉状

```python
import requests

url = "http://localhost:8000/api/lawsuit/generate/lawsuit"
data = {
    "case_info": "劳动纠纷案件",
    "plaintiff": "张三",
    "defendant": "某公司",
    "case_cause": "劳动报酬纠纷",
    "requests": ["要求支付加班费", "要求支付经济补偿金"],
    "evidence": ["劳动合同", "工资条", "考勤记录"],
    "user_requirements": "要求公司支付加班费和经济补偿金"
}

response = requests.post(url, json=data)
print(response.json())
```

## 注意事项

1. 确保API密钥正确配置
2. 网络连接正常
3. 磁盘空间充足（用于存储PDF文件）
4. 服务端口未被占用

## 故障排除

如果遇到问题，请检查：

1. 环境变量是否正确配置
2. API密钥是否有效
3. 网络连接是否正常
4. 依赖包是否安装完整

查看日志输出获取更多详细信息。