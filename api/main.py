#main.py

from fastapi import (
    FastAPI,
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    Request,
    Query,
    Form,
    File,
    UploadFile,
    Body
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.background import BackgroundTask
from starlette.responses import Response
from starlette.concurrency import iterate_in_threadpool
from databases import Database
from sqlalchemy.pool import QueuePool
################################################
# SQLAlchemy数据库相关导入
################################################
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Enum as SQLAEnum,
    text,
    func,
    and_,
    or_,
    JSON
)
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    Session,
    relationship,
    contains_eager,
    joinedload,
    Mapped,
    selectinload  
)

################################################
# 认证和安全相关
################################################
from jose import JWTError, jwt
from passlib.context import CryptContext

################################################
# Pydantic数据验证
################################################
from pydantic import BaseModel, EmailStr, Field,HttpUrl,field_validator

################################################
# 日期和时间处理
################################################
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

################################################
# 类型提示
################################################
from typing import (
    Optional,
    List,
    Dict,
    Tuple,
    Union,
    AsyncGenerator,
    Any
)
from openai import OpenAI
################################################
# 枚举类型处理
################################################
from enum import Enum

################################################
# 文件和路径处理
################################################
from pathlib import Path
from io import StringIO
import shutil
import os

################################################
# 网络和异步处理
################################################
import httpx
import asyncio
################################################
# 邮件处理
################################################
import smtplib
from email.mime.text import MIMEText

################################################
# 实用工具
################################################
import json
import csv
import random
import secrets
import time
import tiktoken
import traceback
import string
from zhipuai import ZhipuAI
import base64




# 导入初始化配置和数据库设置
from init import *
from class_model import *
from func import *
from create_admin import *

# 导入所有路由模块（保持原始路由路径）
from admin import router as admin_router
from logs import router as ai_logs_router
from ai_logs import router as logs_router
from cards import router as cards_router
from channels import router as channels_router
from chat import router as chat_router
from dangerous import router as dangerous_router
from generation import router as generation_router
from market_model import router as market_model_router
from market_prompts import router as market_prompts_router
from models import router as models_router
from settings import router as settings_router
from user import router as user_router

#init.py
# 定义东八区时区
TIMEZONE = ZoneInfo('Asia/Shanghai')
# 配置上传目录
UPLOAD_DIR = Path("uploads/model-icons")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_FILES_DIR = Path("uploads/files")
UPLOAD_FILES_DIR.mkdir(parents=True, exist_ok=True)


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






# 创建FastAPI应用
app = FastAPI(title="ChatYT API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 确保在应用启动时挂载静态文件目录
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# 配置静态文件服务
configure_static_files(app)

################################################
# 注册所有路由（保持原始路由路径）
################################################
# 注意：这里不添加额外的前缀，使用路由文件中定义的原始路径
app.include_router(admin_router)
app.include_router(ai_logs_router)
app.include_router(logs_router)
app.include_router(cards_router)
app.include_router(channels_router)
app.include_router(chat_router)
app.include_router(dangerous_router)
app.include_router(generation_router)
app.include_router(market_model_router)
app.include_router(market_prompts_router)
app.include_router(models_router)
app.include_router(settings_router)
app.include_router(user_router)

################################################
# 中间件设置
################################################
app.add_middleware(APILoggingMiddleware)


create_admin()

configure_static_files(app)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


















