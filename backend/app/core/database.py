# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# from app.core.config import settings

# # 创建数据库引擎
# engine = create_engine(settings.DATABASE_URL)

# # 创建SessionLocal类
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 这个文件现在不需要了，因为我们使用Supabase客户端
# 保留Base类供模型使用
from sqlalchemy.ext.declarative import declarative_base

# 创建Base类（模型仍然需要）
Base = declarative_base()

# 数据库会话现在通过Supabase客户端处理
# 不再需要SQLAlchemy的引擎和会话管理

# 依赖注入函数
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()