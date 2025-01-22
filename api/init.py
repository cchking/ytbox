#init.py

from zoneinfo import ZoneInfo
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# 定义东八区时区
TIMEZONE = ZoneInfo('Asia/Shanghai')
# 配置上传目录
UPLOAD_DIR = Path("uploads/model-icons")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_FILES_DIR = Path("uploads/files")
UPLOAD_FILES_DIR.mkdir(parents=True, exist_ok=True)
# Database setup

DATABASE_URL = "sqlite:///./app.db"
SECRET_KEY = "用于签名JWT的密钥(随便填写)"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30
# 在配置部分添加管理员账户设置
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # 建议在生产环境中使用更强的密码
ADMIN_EMAIL = "admin@example.com"
EMAIL_HOST = "smtp.example.com"
EMAIL_PORT = 587
EMAIL_USER = "your-email@example.com"
EMAIL_PASSWORD = "your-email-password"
verification_codes = {}
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 在配置部分添加Linux.do OAuth配置
LINUXDO_CLIENT_ID = "LINUXDO_CLIENT_ID"
LINUXDO_CLIENT_SECRET = "LINUXDO_CLIENT_SECRET"
LINUXDO_OAUTH_URL = "https://connect.linux.do/oauth2/authorize"
LINUXDO_TOKEN_URL = "https://connect.linux.do/oauth2/token" 
LINUXDO_USER_API = "https://connect.linux.do/api/user"

# GitHub OAuth 配置
GITHUB_CLIENT_ID = "GITHUB_CLIENT_ID"
GITHUB_CLIENT_SECRET = "GITHUB_CLIENT_SECRET"
GITHUB_OAUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_API = "https://api.github.com/user"




# 在文件开头添加常量配置
API_KEYS_COGVIEW = [
    "q",
    "2",
    # 添加更多 key...
]

API_KEYS_COGVIDEO = [
    "1",
    "2",
    # 添加更多 key...
]

# 添加限制配置
RATE_LIMITS = {
    "normal": {
        "image": {"limit": 1, "minutes": 1},  # 普通用户每分钟1张
        "video": {"limit": 1, "minutes": 3}   # 普通用户每3分钟1条
    },
    "vip": {
        "image": {"limit": 2, "minutes": 1},  # VIP用户每分钟2张
        "video": {"limit": 1, "minutes": 1}   # VIP用户每分钟1条
    }
}


engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10000,  # 支持更多并发连接
    max_overflow=30
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12  # 指定加密轮数
)