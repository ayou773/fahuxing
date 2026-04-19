"""
后端主应用
整合所有路由和服务
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入路由
from routers.calculator_router import router as calculator_router
from routers.lawsuit_router import router as lawsuit_router
from routers.consultations_router import router as consultations_router

# 创建FastAPI应用
app = FastAPI(
    title="法护星后端API",
    description="法护星后端服务API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制为具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(calculator_router, prefix="/api/calculator", tags=["计算器"])
app.include_router(lawsuit_router, prefix="/api/lawsuit", tags=["诉状生成"])
app.include_router(consultations_router, prefix="/api/consultations", tags=["咨询记录"])

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "calculator": "available",
            "lawsuit": "available",
            "deepseek": "available",
            "yuanqi": "available"
        }
    }

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "法护星后端API",
        "version": "1.0.0",
        "endpoints": [
            "/api/calculator/",
            "/api/lawsuit/"
        ]
    }

# 启动信息
if __name__ == "__main__":
    import uvicorn
    import logging

    # 配置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # 获取端口配置
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )