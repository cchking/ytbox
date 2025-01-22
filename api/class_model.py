#class.py

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


from database import Base, engine, SessionLocal

from init import *

# 2. 添加 GitHub 用户信息模型
class GitHubUserInfo(BaseModel):
    id: int
    login: str
    name: Optional[str]
    email: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]

# 添加LinuxDO OAuth用户信息模型
class LinuxDOUserInfo(BaseModel):
    id: str
    sub: str
    username: str
    login: str 
    name: str
    email: str
    avatar_template: Optional[str]
    avatar_url: Optional[str]
    active: bool
    trust_level: int
    external_ids: Optional[str]
    api_key: Optional[str]

# Enums
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class ModelGroup(str, Enum):
    FREE = "free"
    VIP = "vip"
    COIN = "coin" 

# 首先创建请求模型
class VipUpdateRequest(BaseModel):
    userId: int
    operation: str  # "add" 或其他操作
    days: int

# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(SQLAEnum(UserRole), default=UserRole.USER)  # 只用于存储 user/admin
    vip_until = Column(DateTime, nullable=True)  # VIP 到期时间
    coins = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    is_banned = Column(Boolean, default=False, nullable=False)
    created_market_models = relationship("MarketModel", back_populates="creator")
    model_pulls = relationship("ModelPull", back_populates="user")
    model_usages = relationship("ModelUsage", back_populates="user")
    model_reviews = relationship("ModelReview", back_populates="user")
    review_comments = relationship("ModelReviewComment", back_populates="user")
User.api_logs = relationship("APILog", back_populates="user")

class CoinLogResponse(BaseModel):
    id: int
    amount: int
    type: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True

# 定义统计响应模型 
class CoinStatsResponse(BaseModel):
    total_income: int  # 总收入
    total_expense: int  # 总支出
    total_admin: int   # 管理员操作总额
    total_signin: int  # 签到总收入
    current_balance: int # 当前余额
    logs: List[CoinLogResponse]  # 日志列表
    total: int  # 总记录数
    page: int   # 当前页码
    page_size: int  # 每页大小


# 更新消息模型定义
class ImageUrl(BaseModel):
    url: str
    detail: Optional[str] = "auto"  # auto, low, high

class MessageCreate(BaseModel):
    content: Optional[str] = None
    images: Optional[List[ImageUrl]] = None
    model: str

class StreamWrapper:
    def __init__(self, generator):
        self.generator = generator
        self.status_code = 200
        self.first_chunk = None

# 然后定义 Folder
class Folder(Base):
    __tablename__ = "folders"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))





class ChatWithPromptCreate(BaseModel):
    name: str
    folder_id: Optional[int] = None

# 接着定义 Chat
class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))

# 然后定义 Message
class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    role = Column(String)
    content = Column(String)
    model_name = Column(String, nullable=True)
    edit_message_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))



# 定义所有关系
User.folders = relationship("Folder", back_populates="user")
User.chats = relationship("Chat", back_populates="user")
Folder.user = relationship("User", back_populates="folders")
Folder.chats = relationship("Chat", back_populates="folder")
Chat.user = relationship("User", back_populates="chats")
Chat.folder = relationship("Folder", back_populates="chats")
Chat.messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
Message.chat = relationship("Chat", back_populates="messages")


# 2. 创建一个不包含 created_at 的登录响应模型
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    vip_until: Optional[datetime] = None

    class Config:
        from_attributes = True



class APILog(Base):
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    endpoint = Column(String)
    method = Column(String)
    request_data = Column(String, nullable=True)
    request_headers = Column(String, nullable=True)
    response_status = Column(Integer)
    response_data = Column(String, nullable=True)
    response_time = Column(Float, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    error = Column(String, nullable=True)
    
    user = relationship("User", back_populates="api_logs")


class AIModel(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    company = Column(String)
    tags = Column(String)
    description = Column(String, nullable=True)
    icon = Column(String, nullable=True)
    group = Column(SQLAEnum(ModelGroup))
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)  # Add sort_order field
    
    channels = relationship("Channel", back_populates="model")
    price = relationship("ModelPrice", back_populates="model", uselist=False)

class ModelPrice(Base):
    __tablename__ = "model_prices"
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("models.id"))
    price = Column(Integer)  # 使用价格(金币)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(TIMEZONE))
    
    model = relationship("AIModel", back_populates="price")

AIModel.price = relationship("ModelPrice", back_populates="model", uselist=False)

# 金币变动记录
class CoinLog(Base):
    __tablename__ = "coin_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)  # 变动金额
    type = Column(String)  # 类型:admin(管理员操作)/consume(消费)/signin(签到)
    description = Column(String)  # 描述
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    user = relationship("User", back_populates="coin_logs")

User.coin_logs = relationship("CoinLog", back_populates="user")

# 签到系统配置
class SigninSettings(Base):
    __tablename__ = "signin_settings"
    
    id = Column(Integer, primary_key=True) 
    enabled = Column(Boolean, default=True)
    reward_type = Column(String)  # vip/coin
    reward_amount = Column(Integer)  # VIP天数/金币数量
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(TIMEZONE))

# 签到记录
class SigninLog(Base):
    __tablename__ = "signin_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reward_type = Column(String)
    reward_amount = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    user = relationship("User", back_populates="signin_logs")

User.signin_logs = relationship("SigninLog", back_populates="user")



class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    channel_name = Column(String)
    channel_model_name = Column(String)
    models = Column(String)  # 新增这一行，用于存储 JSON 字符串
    target_model_id = Column(Integer, ForeignKey("models.id"), nullable=True)
    base_url = Column(String)
    api_key = Column(String)
    weight = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    organization = Column(String, nullable=True)
    redirect_mapping = Column(String, nullable=True)
    
    model = relationship("AIModel", back_populates="channels")

class ModelUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    tags: Optional[str] = None
    description: Optional[str] = None
    group: Optional[ModelGroup] = None
    is_active: Optional[bool] = None



class StreamingFilter(str, Enum):
    TRUE = "true"
    FALSE = "false"
    NULL = "null"


class AIRequestLog(Base):
    __tablename__ = "ai_request_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    model_name = Column(String)
    channel_id = Column(Integer, ForeignKey("channels.id"))
    streaming = Column(Boolean, default=False)
    first_token_latency = Column(Float, nullable=True)  # 修改这里
    total_latency = Column(Float)
    
    # Token 统计
    prompt_tokens = Column(Integer)  # 提示使用的 tokens
    completion_tokens = Column(Integer)  # 补全使用的 tokens
    total_tokens = Column(Integer)  # 总 tokens
    
    # 提示和补全内容
    prompt_messages = Column(String)  # 存储为 JSON 字符串
    request_text = Column(String)  # 最后一条提示消息
    response_text = Column(String)  # 补全响应
    
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    # 关系
    user = relationship("User", back_populates="ai_requests")
    channel = relationship("Channel", back_populates="ai_requests")


class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    url = Column(String)
    type = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    user = relationship("User", back_populates="uploaded_files")

# 添加关系到User模型
User.uploaded_files = relationship("UploadedFile", back_populates="user")


class LimitType(str, Enum):
    RPM = "rpm"  # 每分钟请求数
    RTM = "rtm"  # 每分钟token数
    DAILY = "daily"  # 每日请求总数
    MODEL = "model"  # 模型使用限制

class UserLimit(Base):
    __tablename__ = "user_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    limit_type = Column(SQLAEnum(LimitType))
    limit_value = Column(Integer)  # -1 表示无限制
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    updated_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE), onupdate=lambda: datetime.now(TIMEZONE))
    
    user = relationship("User", back_populates="limits")

class UserModelLimit(Base):
    __tablename__ = "user_model_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    model_id = Column(Integer, ForeignKey("models.id"))
    daily_limit = Column(Integer)  # -1 表示无限制
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    updated_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE), onupdate=lambda: datetime.now(TIMEZONE))
    
    user = relationship("User", back_populates="model_limits")
    model = relationship("AIModel")

class UserUsageLog(Base):
    __tablename__ = "user_usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    model_id = Column(Integer, ForeignKey("models.id"))
    request_count = Column(Integer, default=1)
    token_count = Column(Integer)
    timestamp = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    user = relationship("User", back_populates="usage_logs")
    model = relationship("AIModel")
class EmailWhitelistRule(Base):
    __tablename__ = "email_whitelist_rules"

    id: Mapped[int] = Column(Integer, primary_key=True)
    pattern: Mapped[str] = Column(String, unique=True, index=True)  # 邮箱模式，如 "@qq.com"
    description: Mapped[Optional[str]] = Column(String, nullable=True)
    created_by: Mapped[int] = Column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    is_active: Mapped[bool] = Column(Boolean, default=True)

    creator = relationship("User", back_populates="whitelist_rules")

# 2. 更新User模型添加关系
User.whitelist_rules = relationship("EmailWhitelistRule", back_populates="creator")


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id: Mapped[int] = Column(Integer, primary_key=True)
    rpmLimit: Mapped[int] = Column(Integer, default=60)
    rtmLimit: Mapped[int] = Column(Integer, default=1000)
    dailyLimit: Mapped[int] = Column(Integer, default=1000)
    vipRpmLimit: Mapped[int] = Column(Integer, default=120)
    vipRtmLimit: Mapped[int] = Column(Integer, default=2000)
    vipDailyLimit: Mapped[int] = Column(Integer, default=2000)
    allowRegistration: Mapped[bool] = Column(Boolean, default=True)
    requireEmailVerification: Mapped[bool] = Column(Boolean, default=True)
    allowLogin: Mapped[bool] = Column(Boolean, default=True)
    enableSystemLogs: Mapped[bool] = Column(Boolean, default=True)
    enableForbiddenWords: Mapped[bool] = Column(Boolean, default=True)
    smtp: Mapped[Optional[JSON]] = Column(JSON)
    signin_enabled: Mapped[bool] = Column(Boolean, default=True)
    signin_reward_type: Mapped[str] = Column(String, default="coin")
    signin_reward_amount: Mapped[int] = Column(Integer, default=10)
    invite_enabled: Mapped[bool] = Column(Boolean, default=True)
    inviter_reward_type: Mapped[str] = Column(String, default="coin")
    inviter_reward_amount: Mapped[int] = Column(Integer, default=100)
    invitee_reward_type: Mapped[str] = Column(String, default="coin")
    invitee_reward_amount: Mapped[int] = Column(Integer, default=50)
    card_purchase_url: Mapped[Optional[str]] = Column(String, nullable=True)
    card_purchase_description: Mapped[Optional[str]] = Column(String, nullable=True)
    enable_email_whitelist: Mapped[bool] = Column(Boolean, default=False)  # 是否启用白名单

    # 添加新的前端设置字段
    frontend_logo: Mapped[Optional[str]] = Column(String, nullable=True)
    frontend_title: Mapped[Optional[str]] = Column(String, nullable=True)
    frontend_vip_benefits: Mapped[Optional[str]] = Column(String, nullable=True)
    frontend_user_guide: Mapped[Optional[str]] = Column(String, nullable=True)
    # 添加健康检查相关的配置
    enable_health_check: Mapped[bool] = Column(Boolean, default=True)  # 是否启用健康检查
    health_check_interval: Mapped[int] = Column(Integer, default=5)  # 健康检查间隔（分钟）
    health_check_batch_size: Mapped[int] = Column(Integer, default=500)  # 每次检查的模型数量
    updated_at: Mapped[datetime] = Column(
        DateTime, 
        default=lambda: datetime.now(TIMEZONE),
        onupdate=lambda: datetime.now(TIMEZONE)
    )


class WhitelistRuleCreate(BaseModel):
    pattern: str
    description: Optional[str] = None

class WhitelistRuleUpdate(BaseModel):
    pattern: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None



class FrontendSettingsUpdate(BaseModel):
    logo: Optional[str] = None
    title: Optional[str] = None
    vip_benefits: Optional[str] = None
    user_guide: Optional[str] = None



class ForbiddenWord(Base):
    __tablename__ = "forbidden_words"
    
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, index=True)
    level = Column(String)  # 违禁级别：low, medium, high
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    created_by = Column(Integer, ForeignKey("users.id"))
    
    creator = relationship("User", back_populates="forbidden_words")

class DangerousChat(Base):
    __tablename__ = "dangerous_chats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)  # 违规内容
    matched_words = Column(String)  # 匹配到的违禁词，JSON 格式
    request_data = Column(JSON)  # 完整的请求数据
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    user = relationship("User", back_populates="dangerous_chats")

class PromptType(str, Enum):
    CREATED = "created"    # 用户创建的
    PURCHASED = "purchased"  # 用户购买的
    ALL = "all"           # 所有相关的

# 提示词商品表
class PromptProduct(Base):
    __tablename__ = "prompt_products"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)  # 标题
    description = Column(String)  # 描述
    content = Column(String)  # 提示词内容
    price = Column(Integer)  # 价格(金币)
    creator_id = Column(Integer, ForeignKey("users.id"))  # 创建者
    likes = Column(Integer, default=0)  # 点赞数
    dislikes = Column(Integer, default=0)  # 踩数
    status = Column(String)  # 状态：pending(待审核), approved(已通过), rejected(已拒绝), delisted(下架)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(TIMEZONE))
    
    creator = relationship("User", back_populates="prompt_products")
    purchases = relationship("PromptPurchase", back_populates="product")
    votes = relationship("PromptVote", back_populates="product")

# 提示词购买记录表
class PromptPurchase(Base):
    __tablename__ = "prompt_purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("prompt_products.id"))
    price = Column(Integer)  # 购买时的价格
    commission_rate = Column(Float)  # 购买时的抽成比例
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    user = relationship("User", back_populates="prompt_purchases")
    product = relationship("PromptProduct", back_populates="purchases")

# 提示词投票表(点赞/踩)
class PromptVote(Base):
    __tablename__ = "prompt_votes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("prompt_products.id"))
    vote_type = Column(String)  # like 或 dislike
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    user = relationship("User", back_populates="prompt_votes")
    product = relationship("PromptProduct", back_populates="votes")

# 提示词市场设置表
class PromptMarketSettings(Base):
    __tablename__ = "prompt_market_settings"
    
    id = Column(Integer, primary_key=True)
    commission_rate = Column(Float, default=0.1)  # 平台抽成比例，默认10%
    require_review = Column(Boolean, default=True)  # 是否需要审核
    min_price = Column(Integer, default=1)  # 最低价格
    max_price = Column(Integer, default=1000)  # 最高价格
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(TIMEZONE))




class PrivatePrompt(Base):
    __tablename__ = "private_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)  # 标题
    description = Column(String)  # 描述
    content = Column(String)  # 提示词内容
    user_id = Column(Integer, ForeignKey("users.id"))  # 创建者
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(TIMEZONE))
    
    creator = relationship("User", back_populates="private_prompts")


# 在其他模型定义之后，添加新的绑定模型
class ModelChannelBinding(Base):
    __tablename__ = "model_channel_bindings"
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("models.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    model = relationship("AIModel", back_populates="channel_bindings")
    channel = relationship("Channel", back_populates="model_bindings")

# 然后在 AIModel 和 Channel 类中添加关系
AIModel.channel_bindings = relationship("ModelChannelBinding", back_populates="model")
Channel.model_bindings = relationship("ModelChannelBinding", back_populates="channel")




#模型市场
# 在现有的数据模型部分添加以下内容

class ModelDistributionType(str, Enum):
    FREE_PULL = "free_pull"      # 免费拉取
    COIN_PULL = "coin_pull"      # 金币拉取
    KEY_PULL = "key_pull"        # 兑换码拉取（可与前两者共存）

class ModelUsageType(str, Enum):
    FREE = "free"                # 免费使用
    COIN = "coin"               # 按次收费（金币）

class MarketModel(Base):
    __tablename__ = "market_models"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    description = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id"))
    icon = Column(String, nullable=True)  
    
    # 分发设置
    distribution_type = Column(String)  
    pull_price = Column(Integer)       
    
    # 使用设置
    usage_type = Column(String)         
    usage_price = Column(Integer)       
    
    # API配置
    api_base_url = Column(String, nullable=True)  
    api_key = Column(String, nullable=True)       
    
    # 统计信息
    pull_count = Column(Integer, default=0)  
    usage_count = Column(Integer, default=0)  
    rating = Column(Float, default=0)   
    status = Column(String, default='pending') 
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(TIMEZONE))
    
    # 关系定义
    creator = relationship("User", back_populates="created_market_models")  # 添加这行
    pulls = relationship("ModelPull", back_populates="model")
    usages = relationship("ModelUsage", back_populates="model")
    reviews = relationship("ModelReview", back_populates="model")
    model_keys = relationship("ModelKey", back_populates="model")


class ModelPull(Base):
    __tablename__ = "model_pulls"
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("market_models.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    pull_type = Column(String)          # 拉取方式
    pull_price = Column(Integer)        # 拉取时的价格
    key_code = Column(String, nullable=True)  # 使用的兑换码（如果有）
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    # 关系
    model = relationship("MarketModel", back_populates="pulls")
    user = relationship("User", back_populates="model_pulls")

class ModelUsage(Base):
    __tablename__ = "model_usages"
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("market_models.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    usage_price = Column(Integer)      # 使用时的价格
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    # 关系
    model = relationship("MarketModel", back_populates="usages")
    user = relationship("User", back_populates="model_usages")

class ModelKey(Base):
    __tablename__ = "model_keys"
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("market_models.id"))
    key_code = Column(String, unique=True)
    used_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    # 关系
    model = relationship("MarketModel", back_populates="model_keys")
    user = relationship("User", foreign_keys=[used_by])



class ReviewCommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)  # 改为 content
    parent_id: Optional[int] = None


class ModelReview(Base):
    __tablename__ = "model_reviews"
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("market_models.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Float)
    comment = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    # 添加这个关系
    comments = relationship("ModelReviewComment", back_populates="review")
    
    # 其他已有的关系
    model = relationship("MarketModel", back_populates="reviews")
    user = relationship("User", back_populates="model_reviews")


class ModelReviewComment(Base):
    __tablename__ = "model_review_comments"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    review_id = Column(Integer, ForeignKey("model_reviews.id"))
    parent_id = Column(Integer, ForeignKey("model_review_comments.id"), nullable=True)
    content = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    # 关系
    user = relationship("User", back_populates="review_comments")
    review = relationship("ModelReview", back_populates="comments")
    parent = relationship("ModelReviewComment", remote_side=[id], backref="replies")

# 更新User模型，添加相关关系
User.created_market_models = relationship("MarketModel", back_populates="creator")
User.model_pulls = relationship("ModelPull", back_populates="user")
User.model_usages = relationship("ModelUsage", back_populates="user")
User.model_reviews = relationship("ModelReview", back_populates="user")



class PrivateModel(Base):
    __tablename__ = "private_models"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    description = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id"))
    icon = Column(String, nullable=True)
    
    # API配置
    api_base_url = Column(String)
    api_key = Column(String)        

    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(TIMEZONE))
    
    # 关系
    creator = relationship("User", back_populates="private_models")

# 添加关系到User模型
User.private_models = relationship("PrivateModel", back_populates="creator")

# Pydantic 模型
class PrivateModelCreate(BaseModel):
    name: str
    description: str
    api_base_url: str
    api_key: str

class PrivateModelResponse(BaseModel):
    id: int
    name: str
    description: str
    api_base_url: str
    icon: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class MarketModelCreate(BaseModel):
    name: str
    description: str
    distribution_type: ModelDistributionType
    pull_price: Optional[int] = 0
    usage_type: ModelUsageType
    usage_price: Optional[int] = 0
    api_base_url: Optional[str] = None  # 新增字段
    api_key: Optional[str] = None       # 新增字段





class MarketModelResponse(BaseModel):
    id: int
    name: str
    description: str
    creator_id: int
    creator_username: str
    distribution_type: str
    pull_price: int
    usage_type: str
    usage_price: int
    pull_count: int
    usage_count: int
    rating: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    api_base_url: Optional[str]  # 添加API基础地址
    # 注意：出于安全考虑，不包含api_key

    class Config:
        from_attributes = True


class ModelPullRequest(BaseModel):
    key_code: Optional[str] = None  # 兑换码（如果使用）

class ModelReviewCreate(BaseModel):
    rating: float = Field(..., ge=1, le=5)  # 评分在1-5之间
    comment: str = Field(..., min_length=1, max_length=1000)  # 评论内容限制

    class Config:
        json_schema_extra = {
            "example": {
                "rating": 5,
                "comment": "这是一条评价"
            }
        }

class ModelDetailResponse(BaseModel):
    id: int
    name: str
    description: str
    creator: dict
    distribution_type: str
    pull_price: int
    usage_type: str
    usage_price: int
    icon: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    stats: dict
    user_interaction: dict

    class Config:
        from_attributes = True


class KeysGenerateRequest(BaseModel):
    count: int = Field(ge=1, le=100)  # 生成数量在1-100之间


# 新增评论相关的响应模型
class ReviewCreate(BaseModel):
    rating: float = Field(..., ge=1, le=5)  # 评分范围 1-5
    comment: str = Field(..., min_length=1, max_length=1000)


class CommentResponse(BaseModel):
    id: int
    user_id: int
    username: str
    content: str
    created_at: datetime
    parent_id: Optional[int] = None

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    username: str
    rating: float
    comment: str
    created_at: datetime
    comments: List[CommentResponse] = []

    class Config:
        from_attributes = True



# 评论列表的响应模型
class ReviewListResponse(BaseModel):
    total: int
    items: List[ReviewResponse]
    average_rating: float
    rating_distribution: Dict[int, int]  # 评分分布 {5: 10, 4: 20, ...}


class CardType(str, Enum):
    VIP = "vip"
    COIN = "coin"

class Card(Base):
    __tablename__ = "cards"
    
    id = Column(Integer, primary_key=True, index=True)
    card_no = Column(String, unique=True, index=True)  # 卡密号码
    type = Column(SQLAEnum(CardType))  # 卡密类型：vip/coin
    value = Column(Integer)  # VIP天数或金币数量
    creator_id = Column(Integer, ForeignKey("users.id"))  # 创建者
    used_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 使用者
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    used_at = Column(DateTime, nullable=True)  # 使用时间
    expired_at = Column(DateTime, nullable=True)  # 过期时间
    is_used = Column(Boolean, default=False)  # 是否已使用
    is_expired = Column(Boolean, default=False)  # 是否已过期
    batch_no = Column(String, nullable=True)  # 批次号



class InviteCode(Base):
    __tablename__ = "invite_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)  # 邀请码
    user_id = Column(Integer, ForeignKey("users.id"))  # 创建者ID
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    creator = relationship("User", foreign_keys=[user_id], back_populates="created_invite_codes")

class InviteReward(Base):
    __tablename__ = "invite_rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    inviter_id = Column(Integer, ForeignKey("users.id"))  # 邀请人ID
    invitee_id = Column(Integer, ForeignKey("users.id"))  # 被邀请人ID
    inviter_reward_type = Column(String)  # 邀请人奖励类型(vip/coin)
    inviter_reward_amount = Column(Integer)  # 邀请人奖励数量
    invitee_reward_type = Column(String)  # 被邀请人奖励类型(vip/coin) 
    invitee_reward_amount = Column(Integer)  # 被邀请人奖励数量
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    inviter = relationship("User", foreign_keys=[inviter_id], back_populates="sent_invites")
    invitee = relationship("User", foreign_keys=[invitee_id], back_populates="received_invites")


# 模型配置
class ImageSize(str, Enum):
    SQUARE = "1024x1024"
    VERTICAL_768 = "768x1344"
    VERTICAL_864 = "864x1152"
    HORIZONTAL_1344 = "1344x768"
    HORIZONTAL_1152 = "1152x864"
    HORIZONTAL_1440 = "1440x720"
    VERTICAL_1440 = "720x1440"

class ContentFilterResponse(BaseModel):
    role: str
    level: int

class ImageGenerationResponse(BaseModel):
    created: int
    data: List[dict]
    content_filter: Optional[List[ContentFilterResponse]] = None

class ImageGenerationRequest(BaseModel):
    model: str  # cogview-3-plus、cogview-3、cogview-3-flash
    prompt: str
    size: Optional[ImageSize] = ImageSize.SQUARE
    user_id: Optional[str] = None

class ImageGenerationLog(Base):
    __tablename__ = "image_generation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    model = Column(String)
    prompt = Column(String)
    size = Column(String)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    error = Column(String, nullable=True)
    
    user = relationship("User", back_populates="image_logs")

# 添加关系到User模型
User.image_logs = relationship("ImageGenerationLog", back_populates="user")



# 视频尺寸枚举
class VideoSize(str, Enum):
    SD_480P = "720x480"
    SQUARE = "1024x1024"
    HD_960P = "1280x960"
    VERTICAL_960P = "960x1280"
    FULL_HD = "1920x1080"
    VERTICAL_HD = "1080x1920"
    WIDE_2K = "2048x1080"
    UHD_4K = "3840x2160"

# 视频质量模式
class QualityMode(str, Enum):
    QUALITY = "quality"
    SPEED = "speed"

# 视频生成请求模型
class VideoGenerationRequest(BaseModel):
    model: str  # cogvideox、cogvideox-flash
    prompt: Optional[str] = None
    image_url: Optional[str] = None  # 修改这里，改为接受普通字符串
    image_id: Optional[str] = None  # 添加image_id字段
    quality: Optional[QualityMode] = QualityMode.QUALITY
    with_audio: Optional[bool] = False
    size: Optional[VideoSize] = None
    duration: Optional[int] = 5  # 5 or 10 seconds
    fps: Optional[int] = 30     # 30 or 60 fps
    user_id: Optional[str] = None

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in [5, 10]:
            raise ValueError("Duration must be either 5 or 10 seconds")
        return v

    @field_validator('fps')
    @classmethod
    def validate_fps(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in [30, 60]:
            raise ValueError("FPS must be either 30 or 60")
        return v
        
    @field_validator('model')
    @classmethod
    def validate_model(cls, v: str) -> str:
        valid_models = ['cogvideox', 'cogvideox-flash']
        if v not in valid_models:
            raise ValueError(f"Model must be one of {valid_models}")
        return v


# 视频结果模型
class VideoResult(BaseModel):
    url: str
    cover_image_url: str

# 视频生成响应模型
class VideoGenerationResponse(BaseModel):
    id: str
    request_id: str
    model: str
    task_status: str
    video_result: Optional[List[VideoResult]] = None

# 视频生成日志模型
class VideoGenerationLog(Base):
    __tablename__ = "video_generation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    model = Column(String)
    prompt = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    image_id = Column(String, nullable=True)  # 新增列
    size = Column(String)
    quality = Column(String)
    with_audio = Column(Boolean, default=False)
    duration = Column(Integer)
    fps = Column(Integer)
    video_url = Column(String, nullable=True)
    cover_image_url = Column(String, nullable=True)
    task_id = Column(String, unique=True)
    request_id = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    error = Column(String, nullable=True)
    status = Column(String, default="PROCESSING")
    
    user = relationship("User", back_populates="video_logs")
# 添加关系到User模型
User.video_logs = relationship("VideoGenerationLog", back_populates="user")

# 定义模型健康检查记录表
class ModelHealthCheck(Base):
    __tablename__ = "model_health_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))
    status = Column(String)  # success/error
    latency = Column(Float)  # 响应延迟（毫秒）
    error_message = Column(String, nullable=True)
    check_time = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    
    model = relationship("AIModel", back_populates="health_checks")
    channel = relationship("Channel", back_populates="health_checks")

# 添加关系到现有模型
AIModel.health_checks = relationship("ModelHealthCheck", back_populates="model")
Channel.health_checks = relationship("ModelHealthCheck", back_populates="channel")

# 健康检查响应模型
class ModelHealthStatus(BaseModel):
    model_name: str
    channel_name: str
    status: str
    latency: float
    last_check_time: datetime
    error_message: Optional[str] = None
    success_rate: float  # 最近24小时的成功率
    avg_latency: float  # 最近24小时的平均延迟
    total_checks: int   # 最近24小时的检查总次数



# 更新 User 模型的关系定义
User.created_invite_codes = relationship("InviteCode", foreign_keys=[InviteCode.user_id], back_populates="creator")
User.sent_invites = relationship("InviteReward", foreign_keys=[InviteReward.inviter_id], back_populates="inviter")
User.received_invites = relationship("InviteReward", foreign_keys=[InviteReward.invitee_id], back_populates="invitee")
# 更新用户模型的关系
User.created_cards = relationship("Card", foreign_keys=[Card.creator_id], back_populates="creator")
User.used_cards = relationship("Card", foreign_keys=[Card.used_by], back_populates="user")
Card.creator = relationship("User", foreign_keys=[Card.creator_id], back_populates="created_cards")
Card.user = relationship("User", foreign_keys=[Card.used_by], back_populates="used_cards")


# 更新User模型的关系
User.private_prompts = relationship("PrivatePrompt", back_populates="creator")

# 更新User模型，添加关系
User.prompt_products = relationship("PromptProduct", back_populates="creator")
User.prompt_purchases = relationship("PromptPurchase", back_populates="user")
User.prompt_votes = relationship("PromptVote", back_populates="user")



# 更新相关的模型关系
User.forbidden_words = relationship("ForbiddenWord", back_populates="creator")
User.dangerous_chats = relationship("DangerousChat", back_populates="user")
User.limits = relationship("UserLimit", back_populates="user")
User.model_limits = relationship("UserModelLimit", back_populates="user")
User.usage_logs = relationship("UserUsageLog", back_populates="user")
User.ai_requests = relationship("AIRequestLog", back_populates="user")
Channel.ai_requests = relationship("AIRequestLog", back_populates="channel")


















# Pydantic Models (Schemas)

class InviteSettings(BaseModel):
    invite_enabled: bool
    inviter_reward_type: str  
    inviter_reward_amount: int
    invitee_reward_type: str
    invitee_reward_amount: int

class InviteCodeResponse(BaseModel):
    code: str
    is_used: bool
    used_by: Optional[str] = None  # 使用者用户名
    created_at: datetime
    used_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class InviteStatsResponse(BaseModel):
    total_invites: int
    total_rewards: Dict[str, int]  # 按类型统计的总奖励
    recent_invites: List[Dict]
    
    class Config:
        from_attributes = True



class TokenData(BaseModel):
    username: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    username: str
    email: EmailStr

# 更新 APILogResponse 模型
class APILogResponse(BaseModel):
    id: int
    user_id: int
    endpoint: str
    method: str
    request_data: Optional[str]
    request_headers: Optional[str]
    response_status: int
    response_data: Optional[str]
    response_time: Optional[float]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime
    username: str = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


class AIRequestLogResponse(BaseModel):
    id: int
    user_id: int
    username: str
    model_name: str
    channel_id: int
    channel_name: str
    streaming: bool = False
    first_token_latency: float = 0.0
    total_latency: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    prompt_messages: List[dict] = []
    request_text: str = ""
    response_text: str = ""
    error: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class APILoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response_status = 500  # 默认状态码
        response_data = None
        
        # 检查是否启用日志记录
        db = SessionLocal()
        try:
            settings = db.query(SystemSettings).first()
            enable_logging = settings.enableSystemLogs if settings else True
        except Exception as e:
            print(f"Error checking logging settings: {str(e)}")
            enable_logging = True  # 如果出错，默认启用日志
        finally:
            db.close()

        # 如果未启用日志记录，直接调用下一个中间件
        if not enable_logging:
            return await call_next(request)
            
        # 获取请求信息
        try:
            raw_body = await request.body()
            request_data = raw_body.decode() if raw_body else None
            headers = dict(request.headers)
            headers.pop('authorization', None)  # 移除敏感信息
            request_headers = json.dumps(headers)
        except:
            request_data = None
            request_headers = None

        # 获取用户ID
        user_id = None
        try:
            token = request.headers.get('authorization', '').split('Bearer ')[-1]
            if token and token != 'Bearer':
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get("sub")
                if username:
                    db = SessionLocal()
                    user = db.query(User).filter(User.username == username).first()
                    if user:
                        user_id = user.id
                    db.close()
        except:
            pass

        error = None
        response = None
        try:
            response = await call_next(request)
            response_status = response.status_code
            
            # 检测是否为流式响应
            content_type = response.headers.get('Content-Type', '')
            if 'text/event-stream' in content_type:
                if not request.url.path.startswith('/api/admin/logs'):
                    try:
                        db = SessionLocal()
                        log_entry = APILog(
                            user_id=user_id,
                            endpoint=request.url.path,
                            method=request.method,
                            request_data=request_data,
                            request_headers=request_headers,
                            response_status=response_status,
                            ip_address=request.client.host,
                            user_agent=request.headers.get('user-agent'),
                            timestamp=datetime.now(TIMEZONE)
                        )
                        db.add(log_entry)
                        db.commit()
                    except Exception as e:
                        print(f"Error logging streaming request: {str(e)}")
                    finally:
                        db.close()
                return response
            
            # 处理普通响应
            response_body = [section async for section in response.body_iterator]
            response.body_iterator = iterate_in_threadpool(iter(response_body))
            
            try:
                response_data = response_body[0].decode() if response_body else None
            except:
                response_data = None
                
        except Exception as e:
            error = str(e)
            response_data = str(e)
            
        finally:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            if not request.url.path.startswith('/api/admin/logs'):
                try:
                    db = SessionLocal()
                    log_entry = APILog(
                        user_id=user_id,
                        endpoint=request.url.path,
                        method=request.method,
                        request_data=request_data,
                        request_headers=request_headers,
                        response_status=response_status,
                        response_data=response_data,
                        response_time=response_time,
                        ip_address=request.client.host,
                        user_agent=request.headers.get('user-agent'),
                        error=error,
                        timestamp=datetime.now(TIMEZONE)
                    )
                    db.add(log_entry)
                    db.commit()
                except Exception as e:
                    print(f"Error logging request: {str(e)}")
                    db.rollback()
                finally:
                    db.close()

        return response if response else JSONResponse(
            status_code=response_status,
            content={"detail": "Internal server error"}
        )


# 更新 UserCreate 模型
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[UserRole] = UserRole.USER  # 添加角色字段，默认为普通用户

# 在已有的 Pydantic Models 部分添加以下模型
class FolderBase(BaseModel):
    name: str
class ChatUpdate(BaseModel):
    name: Optional[str] = None
    folder_id: Optional[int] = None

class FolderCreate(FolderBase):
    pass

class FolderUpdate(FolderBase):
    pass

class FolderResponse(FolderBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True



class ChatCreate(BaseModel):
    name: str
    folder_id: Optional[int] = None

class MessageCreate(BaseModel):
    content: str

class ChatResponse(BaseModel):
    id: int
    name: str
    folder_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    model_name: Optional[str] = None
    model_icon: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_banned: bool
    vip_until: Optional[datetime] = None
    coins: Optional[int] = 0
    # 添加签到相关字段
    signin_enabled: Optional[bool] = False
    today_signed: Optional[bool] = False
    signin_reward_type: Optional[str] = None
    signin_reward_amount: Optional[int] = None

    class Config:
        from_attributes = True


class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class ModelBase(BaseModel):
    name: str
    company: str
    tags: str
    description: Optional[str] = None
    group: ModelGroup
    icon: Optional[str] = None  # 添加 icon 字段

class ModelCreate(ModelBase):
    pass

class ModelPriceResponse(BaseModel):
    price: Optional[int] = None

    class Config:
        from_attributes = True
        
class ModelChannelBindingResponse(BaseModel):
    id: int
    channel_id: int
    model_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ModelResponse(ModelBase):
    id: int
    is_active: bool
    is_deleted: bool = False
    icon: Optional[str] = None
    price: Optional[ModelPriceResponse] = None
    sort_order: int = 0
    channel_bindings: List[ModelChannelBindingResponse] = []

    class Config:
        from_attributes = True

class ChatWithPrivatePromptCreate(BaseModel):
    name: str
    prompt_id: int
    folder_id: Optional[int] = None

class ChannelBase(BaseModel):
    channel_name: str
    channel_model_name: str
    base_url: str
    api_key: str
    weight: float = 1.0
    is_active: bool = True
    organization: str = ""
    target_model_id: Optional[int] = None  # 添加这个字段并设为可选

class ChannelCreate(BaseModel):
    channel_name: str
    channel_model_name: str
    models: Optional[List[str]] = []
    base_url: str
    api_key: str
    weight: float = 1.0
    is_active: bool = True
    organization: Optional[str] = None

class ChannelUpdate(BaseModel):
    channel_name: Optional[str] = None
    channel_model_name: Optional[str] = None
    models: Optional[list[str]] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    weight: Optional[float] = None
    is_active: Optional[bool] = None
    organization: Optional[str] = None
    target_model_id: Optional[int] = None
    redirect_mapping: Optional[str] = None  # 改名

class ChannelResponse(BaseModel):
    id: int
    channel_name: str
    channel_model_name: str
    models: list[str] = []
    base_url: str
    weight: float
    is_active: bool
    target_model_id: Optional[int] = None
    created_at: datetime
    organization: Optional[str] = None
    redirect_mapping: Optional[str] = None

    class Config:
        from_attributes = True



class CustomStreamingResponse(Response):
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: dict = None,
        media_type: str = None,
        background: None = None
    ):
        # 设置流式传输需要的响应头
        if headers is None:
            headers = {}
        headers.update({
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Transfer-Encoding': 'chunked'
        })
        
        # 调用父类的初始化方法
        super().__init__(
            content="",  # 内容会通过流式传输
            status_code=status_code,
            headers=headers,
            media_type=media_type or "text/event-stream",
            background=background
        )
        self.body_iterator = content

    async def stream_response(self, send) -> None:
        await send({
            'type': 'http.response.start',
            'status': self.status_code,
            'headers': [
                [k.lower().encode('latin1'), v.encode('latin1')]
                for k, v in self.headers.items()
            ]
        })
        
        try:
            async for chunk in self.body_iterator:
                if chunk:
                    if not isinstance(chunk, bytes):
                        chunk = chunk.encode('utf-8')
                    await send({
                        'type': 'http.response.body',
                        'body': chunk,
                        'more_body': True
                    })
                    # 允许事件循环处理其他任务
                    await asyncio.sleep(0)
        except Exception as e:
            print(f"流式传输错误: {str(e)}")
            # 发送错误信息给客户端
            error_msg = f"data: {json.dumps({'error': str(e)})}\n\n".encode('utf-8')
            await send({
                'type': 'http.response.body',
                'body': error_msg,
                'more_body': True
            })

        # 发送结束标记
        await send({
            'type': 'http.response.body',
            'body': b'',
            'more_body': False
        })




class StreamingConfig:
    """流式响应的配置类"""
    def __init__(self, model_name: str, messages: list, temperature: float = 1.0):
        self.model = model_name
        self.messages = messages
        self.temperature = temperature
        self.stream = True  # 流式响应固定为 True
        
    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "messages": self.messages,
            "temperature": self.temperature,
            "stream": self.stream
        }






class StreamingMetrics:
    """流式响应的指标跟踪类"""
    def __init__(self):
        self.start_time = time.time()
        self.first_token_time = None
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.has_received_first_token = False
        self.accumulated_response = ""

    def record_first_token(self):
        if not self.has_received_first_token:
            self.first_token_time = time.time()
            self.has_received_first_token = True

    def update_tokens(self, prompt_tokens: int = None, completion_tokens: int = None):
        if prompt_tokens is not None:
            self.prompt_tokens = prompt_tokens
        if completion_tokens is not None:
            self.completion_tokens = completion_tokens
        self.total_tokens = self.prompt_tokens + self.completion_tokens

    def get_latency_metrics(self):
        current_time = time.time()
        return {
            "first_token_latency": (self.first_token_time - self.start_time) * 1000 if self.first_token_time else None,
            "total_latency": (current_time - self.start_time) * 1000
        }
    

class ChatMetrics:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.start_time = time.time()
        self.first_token_time = None
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.has_received_first_token = False
        self.accumulated_response = ""
        print(f"[DEBUG] ChatMetrics initialized for model: {model}")

    def calculate_history_tokens(self, messages: List[Dict[str, str]]) -> None:
        try:
            print(f"[DEBUG] Calculating history tokens for {len(messages)} messages")
            
            # 对于自定义模型名称，使用默认的 cl100k_base 编码器
            if self.model in ["admin"]:
                encoding = tiktoken.get_encoding("cl100k_base")
            else:
                try:
                    encoding = tiktoken.encoding_for_model(self.model)
                except KeyError:
                    encoding = tiktoken.get_encoding("cl100k_base")
            
            print(f"[DEBUG] Using encoder: {encoding.name}")
            
            total_tokens = 0
            total_tokens += 3  # 每个请求的基础token数
            
            for message in messages:
                total_tokens += 4  # 每条消息的基础token数
                
                content = message.get('content')
                
                # 处理多模态消息
                if isinstance(content, list):
                    # 如果内容是列表（多模态格式），处理每个部分
                    for part in content:
                        if isinstance(part, dict):
                            if part.get('type') == 'text':
                                # 处理文本部分
                                text_content = part.get('text', '')
                                total_tokens += len(encoding.encode(str(text_content)))
                            elif part.get('type') == 'image_url':
                                # 图片URL部分计算固定token
                                total_tokens += 65  # OpenAI的图片token计算规则
                        else:
                            # 如果部分不是字典，尝试转换为字符串
                            total_tokens += len(encoding.encode(str(part)))
                else:
                    # 普通文本内容
                    total_tokens += len(encoding.encode(str(content))) if content else 0
                
                # 处理角色token
                if 'role' in message:
                    total_tokens += len(encoding.encode(str(message['role'])))
            
            self.prompt_tokens = total_tokens
            self.total_tokens = total_tokens
            
            print(f"[DEBUG] Token calculation:")
            print(f"[DEBUG] - Prompt tokens: {self.prompt_tokens}")
            print(f"[DEBUG] - Total tokens: {self.total_tokens}")
            
        except Exception as e:
            print(f"[DEBUG] Error in calculate_history_tokens: {str(e)}")
            print(f"[DEBUG] Error traceback: {traceback.format_exc()}")
            raise

    def record_first_token(self) -> None:
        if not self.has_received_first_token:
            self.first_token_time = time.time()
            self.has_received_first_token = True
            print(f"[DEBUG] First token received at: {self.first_token_time - self.start_time:.2f}s")

    def update_completion(self, response_text: str) -> None:
        try:
            print(f"[DEBUG] Updating completion with response text length: {len(response_text)}")
            self.accumulated_response = response_text
            encoding = tiktoken.get_encoding("cl100k_base")
            self.completion_tokens = len(encoding.encode(response_text))
            self.total_tokens = self.prompt_tokens + self.completion_tokens
            
            print(f"[DEBUG] Updated completion:")
            print(f"[DEBUG] - Response length: {len(response_text)}")
            print(f"[DEBUG] - Completion tokens: {self.completion_tokens}")
            print(f"[DEBUG] - Total tokens: {self.total_tokens}")
        except Exception as e:
            print(f"[DEBUG] Error in update_completion: {str(e)}")
            print(f"[DEBUG] Error traceback: {traceback.format_exc()}")
            raise

    def get_metrics(self) -> Dict:
        current_time = time.time()
        metrics = {
            "first_token_latency": (self.first_token_time - self.start_time) * 1000 if self.first_token_time else 0,
            "total_latency": (current_time - self.start_time) * 1000,
            "total_tokens": self.total_tokens,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens
        }
        print(f"[DEBUG] Returning metrics: {metrics}")
        return metrics

    def __str__(self) -> str:
        return (
            f"ChatMetrics(model={self.model}, "
            f"prompt_tokens={self.prompt_tokens}, "
            f"completion_tokens={self.completion_tokens}, "
            f"total_tokens={self.total_tokens}, "
            f"accumulated_response_length={len(self.accumulated_response)}, "
            f"has_received_first_token={self.has_received_first_token})"
        )
# 3. 添加 Pydantic 模型用于请求和响应
class LimitCreate(BaseModel):
    limit_type: LimitType
    limit_value: int

class LimitResponse(BaseModel):
    id: int
    user_id: int
    limit_type: LimitType
    limit_value: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ModelLimitCreate(BaseModel):
    model_id: int
    daily_limit: int

class ModelLimitResponse(BaseModel):
    id: int
    user_id: int
    model_id: int
    daily_limit: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SMTPSettings(BaseModel):
    host: str
    port: int
    user: str
    pass_: str = Field(alias='pass')
    from_: str = Field(alias='from')

    class Config:
        populate_by_name = True

    def to_db_dict(self) -> dict:
        """转换为数据库存储格式"""
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'pass': self.pass_,
            'from': self.from_
        }

class SystemSettingsUpdate(BaseModel):
    rpmLimit: Optional[int] = None
    rtmLimit: Optional[int] = None
    dailyLimit: Optional[int] = None
    vipRpmLimit: Optional[int] = None
    vipRtmLimit: Optional[int] = None
    vipDailyLimit: Optional[int] = None
    allowRegistration: Optional[bool] = None
    requireEmailVerification: Optional[bool] = None
    allowLogin: Optional[bool] = None
    enableSystemLogs: Optional[bool] = None
    enableForbiddenWords: Optional[bool] = None
    smtp: Optional[SMTPSettings] = None
    # 添加签到设置字段
    signin_enabled: Optional[bool] = None
    signin_reward_type: Optional[str] = None
    signin_reward_amount: Optional[int] = None
    card_purchase_url: Optional[str] = None
    card_purchase_description: Optional[str] = None
    invite_enabled: Optional[bool] = None
    inviter_reward_type: Optional[str] = None
    inviter_reward_amount: Optional[int] = None
    invitee_reward_type: Optional[str] = None 
    invitee_reward_amount: Optional[int] = None
    enable_email_whitelist: Optional[bool] = None
    # 添加健康检查相关的配置
    enable_health_check: Optional[bool] = None
    health_check_interval: Optional[int] = None
    health_check_batch_size: Optional[int] = None

class SystemSettingsResponse(BaseModel):
    rpmLimit: int
    rtmLimit: int
    dailyLimit: int
    vipRpmLimit: int
    vipRtmLimit: int
    vipDailyLimit: int
    allowRegistration: bool
    requireEmailVerification: bool
    allowLogin: bool
    enableSystemLogs: bool
    enableForbiddenWords: bool
    smtp: Optional[SMTPSettings] = None
    # 添加签到设置字段
    signin_enabled: bool
    signin_reward_type: str
    signin_reward_amount: int
    card_purchase_url: Optional[str] = None
    card_purchase_description: Optional[str] = None
    invite_enabled: bool
    inviter_reward_type: str
    inviter_reward_amount: int  
    invitee_reward_type: str
    invitee_reward_amount: int
    enable_email_whitelist: bool
    # 添加健康检查设置
    enable_health_check: bool  # 添加这行
    health_check_interval: int  # 添加这行
    health_check_batch_size: int  # 添加这行    updated_at: datetime

    class Config:
        from_attributes = True


class ForbiddenWordCreate(BaseModel):
    word: str
    level: str
    description: Optional[str] = None

class ForbiddenWordResponse(BaseModel):
    id: int
    word: str
    level: str
    description: Optional[str]
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True

class DangerousChatResponse(BaseModel):
    id: int
    user_id: int
    username: str
    content: str
    matched_words: List[str]
    ip_address: str
    user_agent: str
    created_at: datetime
    request_data: Dict[str, Any]  # 添加这个字段来包含完整的请求数据

    class Config:
        from_attributes = True

# 4. 添加违禁词检测函数
def check_forbidden_words(content: str, db: Session) -> Tuple[bool, List[str]]:
    forbidden_words = db.query(ForbiddenWord).all()
    matched_words = []
    
    for word in forbidden_words:
        if word.word in content:
            matched_words.append(word.word)
    
    return len(matched_words) > 0, matched_words


class Tag(Base):
    __tablename__ = "prompt_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # 标签名称
    color = Column(String)  # 标签颜色(如 #FF0000)
    description = Column(String, nullable=True)  # 标签描述
    type = Column(String)  # 标签类型：category(分类)、level(等级)等
    sort_order = Column(Integer, default=0)  # 排序顺序
    is_active = Column(Boolean, default=True)  # 是否启用
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))
    created_by = Column(Integer, ForeignKey("users.id"))
    
    creator = relationship("User", back_populates="created_tags")
    products = relationship("PromptProduct", secondary="prompt_product_tags", back_populates="tags")

# 添加中间表，用于提示词和标签的多对多关系
class PromptProductTag(Base):
    __tablename__ = "prompt_product_tags"
    
    product_id = Column(Integer, ForeignKey("prompt_products.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("prompt_tags.id"), primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(TIMEZONE))

# 更新User模型，添加标签关系
User.created_tags = relationship("Tag", back_populates="creator")

# 更新PromptProduct模型，添加标签关系
PromptProduct.tags = relationship("Tag", secondary="prompt_product_tags", back_populates="products")



class PromptProductCreate(BaseModel):
    title: str
    description: str
    content: str
    price: int
    tags: List[int] = []  # 添加标签ID列表字段

class PromptProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    price: Optional[int] = None
    status: Optional[str] = None

class PromptVoteCreate(BaseModel):
    vote_type: str  # like 或 dislike

class PromptMarketSettingsUpdate(BaseModel):
    commission_rate: Optional[float] = None
    require_review: Optional[bool] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None


class TagBase(BaseModel):
    name: str
    color: str
    description: Optional[str] = None
    type: str
    sort_order: Optional[int] = 0

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class TagResponse(TagBase):
    id: int
    is_active: bool
    created_at: datetime
    created_by: int
    
    class Config:
        from_attributes = True


class PromptProductResponse(BaseModel):
    id: int
    title: str
    description: str
    content: Optional[str]
    price: int
    creator_id: int
    creator_username: str
    likes: int = 0
    dislikes: int = 0
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None  # 设置为可选
    has_purchased: bool = False
    has_voted: Optional[str] = None
    tags: List[TagResponse] = []  

    class Config:
        from_attributes = True

class PromptPurchaseResponse(BaseModel):
    id: int
    product_id: int
    product_title: str
    price: int
    commission_rate: float
    created_at: datetime

    class Config:
        from_attributes = True

class PromptPurchaseStats(BaseModel):
    total_spent: int
    purchase_count: int
    purchases: List[PromptPurchaseResponse]

    class Config:
        from_attributes = True


class PrivatePromptCreate(BaseModel):
    title: str
    description: str
    content: str

class PrivatePromptUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None 
    content: Optional[str] = None

class PrivatePromptResponse(BaseModel):
    id: int
    title: str
    description: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 一键公开的请求模型
class PublishPromptRequest(BaseModel):
    prompt_id: int  # 私有提示词ID
    price: int  # 设置价格
    tags: List[int] = []  # 标签ID列表

class CardCreate(BaseModel):
    type: CardType
    value: int
    count: int = 1  # 生成数量
    expired_at: Optional[datetime] = None  # 过期时间

class CardResponse(BaseModel):
    id: int
    card_no: str
    type: CardType
    value: int
    is_used: bool
    is_expired: bool
    created_at: datetime
    expired_at: Optional[datetime]
    used_at: Optional[datetime]
    used_by: Optional[int]
    batch_no: Optional[str]

    class Config:
        from_attributes = True

