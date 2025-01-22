#func.py
from init import *
from class_model import *
# 清理过期验证码的函数
def cleanup_expired_codes():
    now = datetime.now(timezone.utc)
    expired = [email for email, data in verification_codes.items() 
              if data["expires"] < now]
    for email in expired:
        del verification_codes[email]

# Utility functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#工具函数
async def check_ai_output_forbidden_words(content: str, db: Session) -> Tuple[bool, List[str]]:
    """
    检查AI输出内容中的违禁词
    """
    forbidden_words = db.query(ForbiddenWord).all()
    matched_words = []
    
    for word in forbidden_words:
        if word.word in content:
            matched_words.append(word.word)
    
    return len(matched_words) > 0, matched_words

async def log_dangerous_chat_with_context(
    db: Session,
    user_id: int,
    content: str,
    matched_words: List[str],
    chat_id: int,
    ip_address: str,
    user_agent: str,
    request_data: dict
):
    """
    记录违规对话及其上下文
    """
    # 获取完整对话历史
    chat_history = db.query(Message).filter(Message.chat_id == chat_id).all()
    chat_context = [
        {
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        }
        for msg in chat_history
    ]
    
    # 合并传入的 request_data 和其他数据
    full_request_data = {
        **request_data,  # 使用传入的 request_data
        "chat_history": chat_context  # 添加聊天历史
    }
    
    dangerous_chat = DangerousChat(
        user_id=user_id,
        content=content,
        matched_words=json.dumps(matched_words),
        request_data=full_request_data,  # 使用合并后的数据
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(dangerous_chat)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error saving dangerous chat: {str(e)}")

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# Permission checking
async def check_admin_permission(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admin users can perform this operation"
        )
    return current_user


async def cleanup_old_requests(db: Session):
    """
    清理旧的请求记录，保留最近7天的数据
    """
    try:
        cleanup_before = datetime.now(timezone.utc) - timedelta(days=7)
        db.query(AIRequestLog).filter(
            AIRequestLog.created_at < cleanup_before
        ).delete(synchronize_session=False)
        db.commit()
    except Exception as e:
        print(f"Error cleaning up old requests: {e}")
        db.rollback()


async def check_user_limits(user_id: int, model_id: int, db: Session) -> tuple[bool, str]:
    """使用东八区时间的请求限制检查，倒计时从达到限制开始"""
    try:
        print("\n========== 开始检查用户限制 ==========")
        now = datetime.now(TIMEZONE)
        print(f"当前时间（东八区）: {now}")
        
        # 获取用户信息
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "用户不存在"
            
        # 检查VIP状态
        if user.vip_until:
            if user.vip_until.tzinfo is None:
                user_vip_until = user.vip_until.replace(tzinfo=TIMEZONE)
            else:
                user_vip_until = user.vip_until.astimezone(TIMEZONE)
            is_vip = user_vip_until > now or user.role == UserRole.ADMIN
        else:
            is_vip = user.role == UserRole.ADMIN
            
        print(f"用户状态 - VIP: {is_vip}")
        
        # 获取限制值
        settings = db.query(SystemSettings).first()
        if not settings:
            return False, "系统设置不存在"
            
        rpm_limit = settings.vipRpmLimit if is_vip else settings.rpmLimit
        rtm_limit = settings.vipRtmLimit if is_vip else settings.rtmLimit
        daily_limit = settings.vipDailyLimit if is_vip else settings.dailyLimit
        
        print(f"限制值 - RPM: {rpm_limit}, RTM: {rtm_limit}, Daily: {daily_limit}")

        # 计算时间窗口（东八区）
        one_minute_ago = now - timedelta(minutes=1)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # 获取最近60秒内的所有请求，按时间排序
        recent_requests = db.query(AIRequestLog).filter(
            AIRequestLog.user_id == user_id,
            AIRequestLog.created_at > one_minute_ago,
            AIRequestLog.created_at <= now
        ).order_by(AIRequestLog.created_at.asc()).all()
        
        request_count = len(recent_requests)
        print(f"最近60秒内的请求数: {request_count}")

        if request_count >= rpm_limit:
            user_type = "VIP" if is_vip else "普通用户"
            
            if recent_requests:
                # 找到第rpm_limit个请求（从0开始计数，所以是rpm_limit - 1）
                limit_reached_request = recent_requests[rpm_limit - 1]
                limit_reached_time = limit_reached_request.created_at.astimezone(TIMEZONE)
                print(f"达到限制的时间: {limit_reached_time}")
                
                # 计算从达到限制时开始的60秒倒计时还剩多少秒
                time_since_limit = (now - limit_reached_time).total_seconds()
                wait_seconds = max(0, 60 - int(time_since_limit))
                
                print(f"达到限制后经过的时间: {time_since_limit}秒")
                print(f"需要等待的时间: {wait_seconds}秒")
                
                if wait_seconds > 0:
                    return False, f"{user_type}每分钟请求次数已达到上限 ({rpm_limit})，请等待 {wait_seconds} 秒后重试"
            
            return False, f"{user_type}每分钟请求次数已达到上限 ({rpm_limit})"

        # 获取今日请求数
        daily_requests = db.query(AIRequestLog).filter(
            AIRequestLog.user_id == user_id,
            AIRequestLog.created_at >= today_start,
            AIRequestLog.created_at <= now
        ).count()
        
        print(f"今日总请求数: {daily_requests}")
        
        if daily_requests >= daily_limit:
            user_type = "VIP" if is_vip else "普通用户"
            return False, f"{user_type}今日请求次数已达到上限 ({daily_limit})"

        print("\n----- 检查通过 -----")
        return True, None
        
    except Exception as e:
        print(f"\n!!!!! 发生错误 !!!!!")
        print(f"错误类型: {type(e)}")
        print(f"错误信息: {str(e)}")
        traceback.print_exc()
        return False, f"检查使用限制时出错: {str(e)}"
    finally:
        print("\n========== 限制检查结束 ==========\n")
# 添加辅助函数来检查生成限制
async def check_generation_limit(
    user: User,
    media_type: str,
    db: Session
) -> Tuple[bool, str]:
    """
    检查用户的生成限制
    :param user: 用户对象
    :param media_type: 'image' 或 'video'
    :param db: 数据库会话
    :return: (是否允许生成, 错误消息)
    """
    # 确保 vip_until 有时区信息
    now = datetime.now(TIMEZONE)
    is_vip = False
    
    if user.vip_until:
        if user.vip_until.tzinfo is None:
            user_vip_until = user.vip_until.replace(tzinfo=TIMEZONE)
        else:
            user_vip_until = user.vip_until.astimezone(TIMEZONE)
        is_vip = user_vip_until > now or user.role == UserRole.ADMIN

    # 获取适用的限制
    rate_limit = RATE_LIMITS["vip" if is_vip else "normal"][media_type]
    minutes = rate_limit["minutes"]
    limit = rate_limit["limit"]

    # 计算时间窗口
    time_window = now - timedelta(minutes=minutes)

    # 查询在时间窗口内的生成次数
    if media_type == "image":
        count = db.query(ImageGenerationLog).filter(
            ImageGenerationLog.user_id == user.id,
            ImageGenerationLog.created_at >= time_window
        ).count()
    else:  # video
        count = db.query(VideoGenerationLog).filter(
            VideoGenerationLog.user_id == user.id,
            VideoGenerationLog.created_at >= time_window
        ).count()

    if count >= limit:
        user_type = "VIP" if is_vip else "普通用户"
        return False, f"{user_type}每{minutes}分钟只能生成{limit}个{media_type}"
    
    return True, None
# 添加随机选择 API key 的函数
def get_random_api_key(key_type: str) -> str:
    """
    随机获取一个 API key
    :param key_type: 'cogview' 或 'cogvideo'
    :return: API key
    """
    keys = API_KEYS_COGVIEW if key_type == 'cogview' else API_KEYS_COGVIDEO
    return random.choice(keys)

async def log_user_usage(
    user_id: int,
    model_id: int,
    token_count: int,
    db: Session
):
    """记录用户的API使用情况"""
    log = UserUsageLog(
        user_id=user_id,
        model_id=model_id,
        token_count=token_count
    )
    db.add(log)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error logging user usage: {str(e)}")
# Create database tables
Base.metadata.create_all(bind=engine)
async def ensure_user_limits(user_id: int, db: Session):
    """确保用户有基本的限制配置"""
    # 获取用户信息
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
        
    # 获取系统设置
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    # 判断用户是否是VIP或管理员
    is_vip = user.role == UserRole.ADMIN or (user.vip_until and user.vip_until > datetime.now(timezone.utc))
    
    # 获取对应的限制值
    rpm_value = settings.vipRpmLimit if is_vip else settings.rpmLimit
    rtm_value = settings.vipRtmLimit if is_vip else settings.rtmLimit
    daily_value = settings.vipDailyLimit if is_vip else settings.dailyLimit
    
    # 更新或创建RPM限制
    rpm_limit = db.query(UserLimit).filter(
        UserLimit.user_id == user_id,
        UserLimit.limit_type == LimitType.RPM
    ).first()
    if rpm_limit:
        rpm_limit.limit_value = rpm_value
    else:
        rpm_limit = UserLimit(
            user_id=user_id,
            limit_type=LimitType.RPM,
            limit_value=rpm_value
        )
        db.add(rpm_limit)
    
    # 更新或创建RTM限制
    rtm_limit = db.query(UserLimit).filter(
        UserLimit.user_id == user_id,
        UserLimit.limit_type == LimitType.RTM
    ).first()
    if rtm_limit:
        rtm_limit.limit_value = rtm_value
    else:
        rtm_limit = UserLimit(
            user_id=user_id,
            limit_type=LimitType.RTM,
            limit_value=rtm_value
        )
        db.add(rtm_limit)
    
    # 更新或创建每日限制
    daily_limit = db.query(UserLimit).filter(
        UserLimit.user_id == user_id,
        UserLimit.limit_type == LimitType.DAILY
    ).first()
    if daily_limit:
        daily_limit.limit_value = daily_value
    else:
        daily_limit = UserLimit(
            user_id=user_id,
            limit_type=LimitType.DAILY,
            limit_value=daily_value
        )
        db.add(daily_limit)
        
    try:
        db.commit()
    except Exception as e:
        print(f"Error updating user limits: {str(e)}")
        db.rollback()

def count_message_tokens(messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo") -> Tuple[int, int]:
    """
    计算消息历史的 tokens
    返回: (总 tokens, 提示 tokens)
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    except Exception as e:
        print(f"Error getting encoding: {e}")
        return 0, 0

    # 每条消息的基础token（根据OpenAI的计算方式）
    tokens_per_message = 3
    # 整个请求的基础token
    tokens_per_request = 3

    total_tokens = tokens_per_request
    for message in messages:
        total_tokens += tokens_per_message
        for key, value in message.items():
            try:
                total_tokens += len(encoding.encode(value))
            except Exception as e:
                print(f"Error encoding {key}: {e}")
                # 如果编码失败，使用字符长度作为粗略估计
                total_tokens += len(value)

    # 对于assistant的消息，我们只计算它们作为提示的部分
    prompt_tokens = total_tokens - sum(
        len(encoding.encode(msg["content"]))
        for msg in messages
        if msg["role"] == "assistant"
    )

    return total_tokens, prompt_tokens

def check_email_whitelist(email: str, db: Session) -> bool:
    print(f"\n========== 开始白名单检查 ==========")
    print(f"检查邮箱: {email}")
    
    # 检查是否启用了白名单
    settings = db.query(SystemSettings).first()
    if not settings or not settings.enable_email_whitelist:
        print("白名单未启用，直接通过")
        return True
        
    # 获取所有活跃的白名单规则
    rules = db.query(EmailWhitelistRule).filter(
        EmailWhitelistRule.is_active == True
    ).all()
    
    print(f"找到的活跃白名单规则数: {len(rules)}")
    
    # 如果白名单启用但没有规则，不应该允许所有邮箱通过
    if not rules:
        print("白名单已启用但没有规则，拒绝所有邮箱")
        return False
        
    # 检查邮箱是否匹配任何规则
    for rule in rules:
        print(f"检查规则: {rule.pattern}")
        if email.endswith(rule.pattern):
            print(f"邮箱匹配规则: {rule.pattern}")
            return True
            
    print("邮箱不匹配任何活跃的白名单规则")
    return False

def count_completion_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    计算单个回复的 tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception as e:
        print(f"Error in completion token counting: {e}")
        return len(text)

async def log_chat_request(
    db: Session,
    user_id: int,
    channel_id: int,
    model_name: str,
    chat_metrics: ChatMetrics,
    messages: List[dict],
    request_text: str,
    error: str = None
) -> None:
    """记录聊天请求的详细信息"""
    print("\n========== 开始记录请求 ==========")
    try:
        now = datetime.now(TIMEZONE)
        print(f"记录时间（东八区）: {now}")
        
        metrics = chat_metrics.get_metrics()
        log_entry = AIRequestLog(
            user_id=user_id,
            model_name=model_name,
            channel_id=channel_id,
            streaming=True,
            first_token_latency=metrics["first_token_latency"],
            total_latency=metrics["total_latency"],
            prompt_tokens=chat_metrics.prompt_tokens,
            completion_tokens=chat_metrics.completion_tokens,
            total_tokens=chat_metrics.total_tokens,
            prompt_messages=json.dumps(messages),
            request_text=request_text,
            response_text=chat_metrics.accumulated_response if not error else "[Error in Response]",
            error=error,
            created_at=now
        )
        
        print("\n----- 记录详情 -----")
        print(f"首次响应延迟: {metrics['first_token_latency']}ms")
        print(f"总延迟: {metrics['total_latency']}ms")
        print(f"Token统计:")
        print(f"- 提示词: {chat_metrics.prompt_tokens}")
        print(f"- 补全: {chat_metrics.completion_tokens}")
        print(f"- 总计: {chat_metrics.total_tokens}")
        
        db.add(log_entry)
        db.commit()
        print("\n请求记录已保存")
        
    except Exception as e:
        print(f"\n!!!!! 记录请求时发生错误 !!!!!")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        print("\n========== 请求记录结束 ==========\n")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def send_reset_email(email: str, token: str):
    msg = MIMEText(f'Your password reset token is: {token}')
    msg['Subject'] = 'Password Reset'
    msg['From'] = EMAIL_USER
    msg['To'] = email

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
async def stream_response(response: httpx.Response) -> AsyncGenerator[bytes, None]:
    """
    处理流式响应的生成器函数
    """
    async for chunk in response.aiter_bytes():
        if chunk:
            try:
                # 解析返回的数据块
                text = chunk.decode('utf-8')
                if text.startswith('data: '):
                    text = text[6:]  # 去掉 'data: ' 前缀
                if text.strip() == '[DONE]':
                    continue
                
                # 解析 JSON 数据
                data = json.loads(text)
                if not data.get('choices'):
                    continue
                    
                content = data['choices'][0].get('delta', {}).get('content', '')
                if content:
                    # 构建与客户端约定的数据格式
                    response_data = {
                        "role": "assistant",
                        "content": content,
                        "finish_reason": None
                    }
                    # 转换为字符串并添加前缀
                    yield f"data: {json.dumps(response_data)}\n\n".encode('utf-8')
                    
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error processing chunk: {str(e)}")
                continue
# 检查用户是否有VIP访问权限的辅助函数
def check_vip_access(user: User, model: AIModel) -> bool:
    """检查用户是否有访问权限的辅助函数"""
    # 如果是免费模型或金币模型，直接返回 True
    if model.group in [ModelGroup.FREE, ModelGroup.COIN]:
        return True
        
    if user.role == UserRole.ADMIN:
        return True
        
    if not user.vip_until:
        return False
        
    # 确保 vip_until 有时区信息并统一转换为东八区
    now = datetime.now(TIMEZONE)
    if user.vip_until.tzinfo is None:
        user_vip_until = user.vip_until.replace(tzinfo=TIMEZONE)
    else:
        user_vip_until = user_vip_until.astimezone(TIMEZONE)
            
    return user_vip_until > now

def ensure_upload_directories():
    """Ensure all required upload directories exist with proper permissions"""
    upload_dirs = [
        Path("uploads/model-icons"),
        Path("uploads/files")
    ]
    
    for directory in upload_dirs:
        directory.mkdir(parents=True, exist_ok=True)
        os.chmod(directory, 0o775)  # Set proper directory permissions

def configure_static_files(app: FastAPI):
    """Configure static file serving for FastAPI"""
    # Create required directories
    ensure_upload_directories()
    
    # Get absolute path for uploads directory
    uploads_path = Path("uploads").absolute()
    
    # Mount static file handler
    app.mount(
        "/uploads",
        StaticFiles(directory=str(uploads_path), check_dir=True),
        name="uploads"
    )

async def log_ai_request(
    db: Session,
    user_id: int,
    model_name: str,
    channel_id: int,
    streaming: bool,
    first_token_latency: Optional[float],
    total_latency: float,
    prompt_tokens: int,
    completion_tokens: int,
    request_text: Union[str, List, Dict],  # 修改类型标注
    response_text: str,
    error: Optional[str] = None
):
    """记录聊天请求的详细信息"""
    try:
        # 确保 request_text 是字符串
        if isinstance(request_text, (list, dict)):
            request_text = json.dumps(request_text)

        log_entry = AIRequestLog(
            user_id=user_id,
            model_name=model_name,
            channel_id=channel_id,
            streaming=streaming,
            first_token_latency=first_token_latency,
            total_latency=total_latency,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            request_text=request_text,  # 现在是 JSON 字符串
            response_text=response_text,
            error=error,
            created_at=datetime.now(TIMEZONE)
        )
        
        db.add(log_entry)
        try:
            db.commit()
            db.refresh(log_entry)
            return log_entry
        except Exception as e:
            db.rollback()
            print(f"Error logging AI request: {str(e)}")
            return None
    except Exception as e:
        print(f"Error in log_ai_request: {str(e)}")
        return None
async def sync_user_limit(db: Session, user_id: int, limit_type: LimitType, limit_value: int):
    existing_limit = db.query(UserLimit).filter(
        UserLimit.user_id == user_id,
        UserLimit.limit_type == limit_type
    ).first()
    
    if existing_limit:
        existing_limit.limit_value = limit_value
    else:
        new_limit = UserLimit(
            user_id=user_id,
            limit_type=limit_type,
            limit_value=limit_value
        )
        db.add(new_limit)
async def get_user_rate_limits(user: User, db: Session) -> dict:
    """
    根据用户的VIP状态返回对应的频率限制
    """
    # 获取系统设置
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)

    # 检查用户是否是VIP
    is_vip = user.vip_until and user.vip_until > datetime.now(timezone.utc)
    
    # VIP用户和管理员使用VIP限制
    if is_vip or user.role == UserRole.ADMIN:
        return {
            "rpm": settings.vipRpmLimit,
            "rtm": settings.vipRtmLimit,
            "daily": settings.vipDailyLimit
        }
    
    # 普通用户使用默认限制
    return {
        "rpm": settings.rpmLimit,
        "rtm": settings.rtmLimit,
        "daily": settings.dailyLimit
    }
async def check_video_status(task_id: str, db: Session, client: ZhipuAI):
    """后台任务：检查视频生成状态"""
    max_retries = 60  # 最大重试次数
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 查询任务状态
            response = client.videos.retrieve_videos_result(id=task_id)
            
            # 更新数据库状态
            log = db.query(VideoGenerationLog).filter(VideoGenerationLog.task_id == task_id).first()
            if not log:
                return
                
            log.status = response.task_status
            
            if response.task_status == "SUCCESS":
                # 更新视频URL和封面URL
                if response.video_result:
                    log.video_url = response.video_result[0].url
                    log.cover_image_url = response.video_result[0].cover_image_url
                db.commit()
                return
            elif response.task_status == "FAIL":
                log.error = "Video generation failed"
                db.commit()
                return
                
            # 如果还在处理中，等待后继续查询
            await asyncio.sleep(5)  # 每5秒查询一次
            retry_count += 1
            
        except Exception as e:
            log.error = str(e)
            log.status = "FAIL"
            db.commit()
            return
# 修改使用模型时检查金币
async def check_model_access(user: User, model: AIModel, db: Session) -> bool:
    """检查用户是否可以使用模型"""
    if model.group == ModelGroup.FREE:
        return True
        
    if model.group == ModelGroup.VIP:
        return (user.role == UserRole.ADMIN or 
                (user.vip_until and user.vip_until > datetime.now(timezone.utc)))
                
    if model.group == ModelGroup.COIN:
        if not model.price:
            return True
        return user.coins >= model.price.price
        
    return False


def serialize_datetime(dt):
    """序列化datetime对象为ISO格式字符串"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TIMEZONE)
    return dt.isoformat()

async def handle_model_payment(
    db: Session,
    model_id: int,
    user_id: int
) -> None:
    """处理模型使用费用"""
    model = db.query(MarketModel).filter(MarketModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    if model.usage_type != ModelUsageType.COIN:
        return
        
    current_user = db.query(User).filter(User.id == user_id).first()
    
    # 检查金币余额
    if current_user.coins < model.usage_price:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient coins. Required: {model.usage_price}"
        )
            
    # 扣除用户金币
    current_user.coins -= model.usage_price
    
    # 记录用户金币消费
    coin_log = CoinLog(
        user_id=user_id,
        amount=-model.usage_price,
        type="consume",
        description=f"Use model: {model.name}"
    )
    db.add(coin_log)
    
    # 给创建者加金币
    creator = db.query(User).filter(User.id == model.creator_id).first()
    if creator:
        creator.coins = (creator.coins or 0) + model.usage_price
        creator_coin_log = CoinLog(
            user_id=creator.id,
            amount=model.usage_price,
            type="income",
            description=f"Model usage income: {model.name}"
        )
        db.add(creator_coin_log)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

async def record_model_usage(
    db: Session,
    model_id: int,
    user_id: int
) -> None:
    """记录模型使用"""
    # 检查是否已拉取
    pull_record = db.query(ModelPull).filter(
        ModelPull.model_id == model_id,
        ModelPull.user_id == user_id
    ).first()
    
    if not pull_record:
        raise HTTPException(
            status_code=403,
            detail="You need to pull this model first"
        )
    
    model = db.query(MarketModel).filter(MarketModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # 记录使用
    usage = ModelUsage(
        model_id=model_id,
        user_id=user_id,
        usage_price=model.usage_price if model.usage_type == ModelUsageType.COIN else 0
    )
    db.add(usage)
    
    # 更新使用计数
    model.usage_count += 1
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

async def record_model_usage(
    db: Session,
    model_id: int,
    user_id: int,
    tokens: Optional[int] = None,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None
) -> None:
    """记录模型使用"""
    try:
        # 检查是否已拉取
        pull_record = db.query(ModelPull).filter(
            ModelPull.model_id == model_id,
            ModelPull.user_id == user_id
        ).first()
        
        if not pull_record:
            raise HTTPException(
                status_code=403,
                detail="You need to pull this model first"
            )
        
        model = db.query(MarketModel).filter(MarketModel.id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # 记录使用
        usage = ModelUsage(
            model_id=model_id,
            user_id=user_id,
            usage_price=model.usage_price if model.usage_type == ModelUsageType.COIN else 0,
            tokens=tokens,  # 新增字段
            prompt_tokens=prompt_tokens,  # 新增字段
            completion_tokens=completion_tokens  # 新增字段
        )
        db.add(usage)
        
        # 更新使用计数
        model.usage_count += 1
        
        print(f"记录市场模型使用 - 模型: {model.name}, 用户: {user_id}")
        if tokens:
            print(f"Token统计 - 总数: {tokens}, 提示词: {prompt_tokens}, 补全: {completion_tokens}")
        
        try:
            db.commit()
            print("使用记录保存成功")
        except Exception as e:
            db.rollback()
            print(f"保存使用记录失败: {str(e)}")
            raise
            
    except Exception as e:
        print(f"记录模型使用时出错: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

async def select_channel(db: Session, model_name: str) -> Optional[Channel]:
    # 先尝试查找特定绑定的渠道
    channels = db.query(Channel)\
        .join(ModelChannelBinding)\
        .join(AIModel)\
        .filter(
            Channel.is_active == True,
            AIModel.name == model_name
        ).all()
    
    if not channels:
        # 如果没有特定绑定,查找所有支持该模型的渠道
        channels = db.query(Channel)\
            .filter(
                Channel.is_active == True,
                Channel.models.like(f'%{model_name}%')
            ).all()
    
    if not channels:
        return None
        
    # 根据权重随机选择渠道
    total_weight = sum(c.weight for c in channels)
    random_value = random.uniform(0, total_weight)
    current_weight = 0
    
    for channel in channels:
        current_weight += channel.weight
        if current_weight >= random_value:
            return channel
            
    return channels[0] if channels else None

async def select_channel_for_model(
    db: Session,
    model_id: int,
    model_name: str
) -> Optional[Channel]:
    """基于绑定关系为模型选择合适的渠道"""
    try:
        # 优先检查绑定渠道
        bound_channels = db.query(Channel)\
            .join(ModelChannelBinding)\
            .filter(
                ModelChannelBinding.model_id == model_id,
                Channel.is_active == True
            ).all()
            
        if bound_channels:
            # 基于权重选择绑定渠道
            total_weight = sum(c.weight for c in bound_channels)
            random_value = random.uniform(0, total_weight)
            current_weight = 0
            
            for channel in bound_channels:
                current_weight += channel.weight
                if current_weight >= random_value:
                    return channel

            return bound_channels[0]
            
        # 如无绑定渠道,回退到支持该模型名称的渠道
        return await select_channel(db, model_name)
        
    except Exception as e:
        print(f"选择渠道时出错: {str(e)}")
        return None


def get_actual_model(channel: Channel, requested_model: str) -> str:
    """确定实际使用的模型名称"""
    try:
        print(f"\n========== 获取实际模型名称 ==========")
        print(f"请求模型: {requested_model}")
        print(f"渠道: {channel.channel_name}")
        
        # 1. 检查重定向映射
        if channel.redirect_mapping:
            try:
                mapping = json.loads(channel.redirect_mapping)
                print(f"重定向映射: {mapping}")
                
                if requested_model in mapping:
                    actual_model = mapping[requested_model]
                    print(f"应用重定向: {requested_model} -> {actual_model}")
                    return actual_model
            except json.JSONDecodeError:
                print("警告: 重定向映射解析失败")
        
        # 2. 验证模型是否被支持
        try:
            models = json.loads(channel.models) if channel.models else []
            if requested_model in models:
                print(f"使用原始模型: {requested_model}")
                return requested_model
        except json.JSONDecodeError:
            print("警告: 支持模型列表解析失败")
        
        # 3. 使用渠道默认模型
        print(f"使用渠道默认模型: {channel.channel_model_name}")
        return channel.channel_model_name
        
    except Exception as e:
        print(f"获取实际模型时出错: {str(e)}")
        print(traceback.format_exc())
        # 发生错误时返回请求的模型
        return requested_model
    finally:
        print("========== 模型名称确定结束 ==========\n")

def process_response_chunk(response_data: dict, metrics: StreamingMetrics):
    """处理响应数据块"""
    if not metrics.has_received_first_token and 'choices' in response_data:
        metrics.record_first_token()
        
    if 'usage' in response_data:
        metrics.update_tokens(
            response_data['usage'].get('prompt_tokens'),
            response_data['usage'].get('completion_tokens')
        )
    
    if 'choices' in response_data and response_data['choices']:
        choice = response_data['choices'][0]
        if 'delta' in choice and 'content' in choice['delta']:
            metrics.accumulated_response += choice['delta']['content']

# async def log_completion(db: Session, user: User, model: str, channel: Channel, 
#                         metrics: StreamingMetrics, request_text: str):
#     """记录成功完成的请求"""
#     latency = metrics.get_latency_metrics()
#     await log_ai_request(
#         db=db,
#         user_id=user.id,
#         model_name=model,
#         hat_metrics=ChatMetrics(...),
#         channel_id=channel.id,
#         streaming=True,
#         first_token_latency=latency['first_token_latency'],
#         total_latency=latency['total_latency'],
#         prompt_tokens=metrics.prompt_tokens,
#         completion_tokens=count_tokens(metrics.accumulated_response),
#         request_text=request_text,
#         response_text="[Streaming Response]",
#         error=None
#     )

# async def log_error(db: Session, user: User, model: str, channel: Channel, 
#                     metrics: StreamingMetrics, request_text: str, error: str):
#     """记录错误请求"""
#     latency = metrics.get_latency_metrics()
#     await log_ai_request(
#         db=db,
#         user_id=user.id,
#         model_name=model,
#         channel_id=channel.id,
#         streaming=True,
#         first_token_latency=latency['first_token_latency'],
#         total_latency=latency['total_latency'],
#         prompt_tokens=metrics.prompt_tokens,
#         completion_tokens=count_tokens(metrics.accumulated_response),
#         request_text=request_text,
#         response_text="[Error in Streaming Response]",
#         error=error
#     )

async def check_all_models(db: Session, batch_size: int):
    """并行检查所有可用模型的健康状态"""
    try:
        print("\n=== 开始执行健康检测 ===")
        
        channels = db.query(Channel).filter(Channel.is_active == True).all()
        models = db.query(AIModel).filter(
            AIModel.is_deleted == False,
            AIModel.is_active == True
        ).all()
        
        print(f"找到 {len(channels)} 个活跃渠道")
        print(f"找到 {len(models)} 个活跃模型")

        check_tasks = []
        
        for model in models:
            supporting_channels = []
            for channel in channels:
                try:
                    channel_models = json.loads(channel.models) if channel.models else []
                    if model.name in channel_models:
                        supporting_channels.append(channel)
                        continue
                    
                    if channel.redirect_mapping:
                        try:
                            mapping = json.loads(channel.redirect_mapping)
                            if model.name in mapping:
                                supporting_channels.append(channel)
                        except json.JSONDecodeError:
                            pass
                except json.JSONDecodeError:
                    continue
            
            if not supporting_channels:
                print(f"模型 {model.name} 没有找到支持的渠道")
                continue

            # 为每个支持的渠道创建检测任务
            for channel in supporting_channels:
                check_tasks.append(check_single_model(model, channel, db))

        # 分批执行检测任务
        if check_tasks:
            total_tasks = len(check_tasks)
            batch_count = (total_tasks + batch_size - 1) // batch_size
            print(f"\n总共 {total_tasks} 个检测任务，分 {batch_count} 批执行，每批 {batch_size} 个")
            
            start_time = time.time()
            total_success = 0
            total_error = 0
            
            for i in range(0, total_tasks, batch_size):
                batch = check_tasks[i:i + batch_size]
                print(f"\n执行第 {i//batch_size + 1}/{batch_count} 批，{len(batch)} 个任务")
                
                batch_start = time.time()
                results = await asyncio.gather(*batch, return_exceptions=True)
                batch_time = time.time() - batch_start
                
                # 统计本批次结果
                batch_success = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'success')
                batch_error = len(results) - batch_success
                
                total_success += batch_success
                total_error += batch_error
                
                print(f"本批次耗时: {round(batch_time, 2)}秒, 成功: {batch_success}, 失败: {batch_error}")
            
            total_time = time.time() - start_time
            print(f"\n所有检测完成:")
            print(f"- 总耗时: {round(total_time, 2)}秒")
            print(f"- 总成功: {total_success}")
            print(f"- 总失败: {total_error}")
        
        print("\n=== 健康检测完成 ===")
                    
    except Exception as e:
        print(f"健康检测过程出错: {str(e)}")
        print(f"错误详情:\n{traceback.format_exc()}")
        raise

async def check_single_model(model: AIModel, channel: Channel, db: Session) -> Dict:
    """异步检查单个模型的健康状态"""
    start_time = time.time()
    
    try:
        actual_model = model.name
        if channel.redirect_mapping:
            try:
                mapping = json.loads(channel.redirect_mapping)
                if model.name in mapping:
                    actual_model = mapping[model.name]
            except:
                pass
        
        request_url = f"{channel.base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {channel.api_key}",
            "Content-Type": "application/json"
        }
        test_data = {
            "model": actual_model,
            "messages": [{"role": "user", "content": "1"}],
            "max_tokens": 1
        }
        
        print(f"检测 {model.name} via {channel.channel_name}...")
        # 异步发送测试请求
        async with httpx.AsyncClient() as client:
            response = await client.post(
                request_url,
                headers=headers,
                json=test_data,
                timeout=30.0
            )
            
            latency = (time.time() - start_time) * 1000
            
            # 使用同步方式记录健康检查
            health_check = ModelHealthCheck(
                model_id=model.id,
                channel_id=channel.id,
                status='success',
                latency=latency,
                error_message=None
            )
            
            # 删除旧记录（只保留最近24条）
            oldest = db.query(ModelHealthCheck)\
                .filter(ModelHealthCheck.model_id == model.id)\
                .order_by(ModelHealthCheck.check_time.desc())\
                .offset(23)\
                .first()
                
            if oldest:
                db.query(ModelHealthCheck)\
                    .filter(
                        ModelHealthCheck.model_id == model.id,
                        ModelHealthCheck.check_time < oldest.check_time
                    )\
                    .delete(synchronize_session=False)
            
            db.add(health_check)
            db.commit()
            
            print(f"{model.name} 检测成功: {round(latency)}ms")
            return {
                "model": model.name,
                "channel": channel.channel_name,
                "status": "success",
                "latency": latency
            }
            
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        error_message = str(e)
        
        # 记录错误
        try:
            health_check = ModelHealthCheck(
                model_id=model.id,
                channel_id=channel.id,
                status="error",
                latency=latency,
                error_message=error_message
            )
            db.add(health_check)
            db.commit()
            
            print(f"{model.name} 检测失败: {error_message}")
        except Exception as db_error:
            db.rollback()
            print(f"保存检测记录失败: {str(db_error)}")
        
        return {
            "model": model.name,
            "channel": channel.channel_name,
            "status": "error",
            "latency": latency,
            "error_message": error_message
        }






def init_app():
    """应用初始化函数"""
    # 确保上传目录存在
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_FILES_DIR.mkdir(parents=True, exist_ok=True)
    
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    # 初始化管理员账户
    init_admin_account()





def init_admin_account():
    """初始化管理员账户"""
    db = SessionLocal()
    try:
        # 检查管理员是否已存在
        result = db.execute(
            text("SELECT * FROM users WHERE username = :username"),
            {"username": ADMIN_USERNAME}
        ).first()
        
        if result:
            print(f"Admin account '{ADMIN_USERNAME}' already exists.")
            return
            
        # 创建管理员账户
        hashed_password = pwd_context.hash(ADMIN_PASSWORD)
        db.execute(
            text("""
            INSERT INTO users (
                username, 
                email, 
                hashed_password, 
                role, 
                is_active, 
                is_banned,
                created_at,
                updated_at
            ) VALUES (
                :username,
                :email,
                :password,
                :role,
                :is_active,
                :is_banned,
                DATETIME('now'),
                DATETIME('now')
            )
            """),
            {
                "username": ADMIN_USERNAME,
                "email": ADMIN_EMAIL,
                "password": hashed_password,
                "role": "ADMIN",
                "is_active": True,
                "is_banned": False
            }
        )
        db.commit()
        print(f"Admin account created successfully!")
        print(f"Username: {ADMIN_USERNAME}")
        print(f"Password: {ADMIN_PASSWORD}")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating admin account: {str(e)}")
    finally:
        db.close()