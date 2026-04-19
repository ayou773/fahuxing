import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import MetaData


# 从环境变量获取数据库连接
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://legal_user:legal_pass@localhost/legal_db"
)

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "server_settings": {
            "application_name": "fa_hu_xing"
        }
    }
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# 基础模型类
Base = declarative_base()


async def init_db():
    """初始化数据库（生产环境应使用Alembic迁移）"""
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
        # 可添加初始数据
        # await conn.execute(...)