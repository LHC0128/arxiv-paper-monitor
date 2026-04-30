import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 邮箱配置
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
    
    # Arxiv配置
    # 优先从环境变量读取关键词，并进行健壮性处理（去除多余空格和引号）
    _env_keywords = os.getenv("SEARCH_KEYWORDS")
    if _env_keywords:
        SEARCH_KEYWORDS = [kw.strip().strip('"').strip("'") for kw in _env_keywords.split(",")]
    else:
        # 默认搜索关键词
        SEARCH_KEYWORDS = [
            "Rydberg atom",
            "magneto-optical trap",
            "optical tweezers",
            "nanophotonics"
        ]
        
    MAX_RESULTS = int(os.getenv("MAX_RESULTS", 50))
    
    # 定时任务配置
    SCHEDULE_TIME = "09:00"  # 每天9点
    TEST_MODE = False  # 测试模式，为True时立即运行
    
    # 日志配置
    LOG_FILE = "logs/arxiv_digest.log"
    
    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.EMAIL_SENDER or not cls.EMAIL_PASSWORD:
            raise ValueError("邮箱配置不完整，请检查 .env 文件或 GitHub Secrets")
        return True
