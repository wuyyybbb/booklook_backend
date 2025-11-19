"""
应用配置
"""
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "Formy"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API 配置
    API_V1_PREFIX: str = "/api/v1"
    
    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # 文件存储配置
    UPLOAD_DIR: str = "./uploads"          # 上传文件存储目录
    RESULT_DIR: str = "./results"          # 结果文件存储目录
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 最大上传文件大小（10MB）
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp"}
    
    # 任务配置
    TASK_RETENTION_DAYS: int = 7           # 任务结果保留天数
    MAX_CONCURRENT_TASKS_PER_USER: int = 3 # 每用户最大并发任务数
    
    # JWT 配置（可选）
    SECRET_KEY: str = "formy-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小时
    
    # CORS 配置
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite 默认端口
    ]
    
    # Engine 配置文件路径
    ENGINE_CONFIG_PATH: str = "./engine_config.yml"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()

