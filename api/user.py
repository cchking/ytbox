from class_model import *
from func import *

from fastapi import APIRouter
router = APIRouter() 



@router.post("/api/users/register", response_model=UserResponse)
async def register_user(
    user: UserCreate, 
    db: Session = Depends(get_db)
):
    """
    用户注册路由
    - 检查系统是否允许注册
    - 验证邮箱白名单
    - 验证用户名和邮箱唯一性
    - 检查邮箱验证码(如果启用)
    """
    try:
        print("\n========== 开始处理注册请求 ==========")
        print(f"用户名: {user.username}")
        print(f"邮箱: {user.email}")
        
        # 1. 检查系统设置
        settings = db.query(SystemSettings).first()
        if not settings:
            print("错误: 找不到系统设置")
            raise HTTPException(status_code=400, detail="System settings not found")

        if not settings.allowRegistration:
            print("错误: 系统当前禁止注册")
            raise HTTPException(status_code=400, detail="Registration is currently disabled")

        # 2. 检查邮箱白名单
        if not check_email_whitelist(user.email, db):
            print("错误: 邮箱不在白名单中")
            raise HTTPException(
                status_code=403,
                detail="This email domain is not whitelisted"
            )

        # 3. 验证邮箱验证码(如果启用)
        if settings.requireEmailVerification:
            print("系统要求邮箱验证")
            verification = verification_codes.get(user.email)
            if not verification:
                print("错误: 找不到验证码记录")
                raise HTTPException(status_code=400, detail="Verification code is required")
                
            if verification['expires'] < datetime.now(timezone.utc):
                verification_codes.pop(user.email, None)
                print("错误: 验证码已过期")
                raise HTTPException(status_code=400, detail="Verification code expired")

        # 4. 检查用户名是否已存在
        if db.query(User).filter(User.username == user.username).first():
            print("错误: 用户名已被注册")
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # 5. 检查邮箱是否已存在
        if db.query(User).filter(User.email == user.email).first():
            print("错误: 邮箱已被注册")
            raise HTTPException(status_code=400, detail="Email already registered")

        # 6. 创建新用户
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            role=user.role if user.role else UserRole.USER,  # 如果未指定角色,默认为普通用户
            is_active=True,
            is_banned=False,
            created_at=datetime.now(TIMEZONE)
        )
        
        db.add(db_user)
        
        try:
            print("保存用户数据...")
            db.commit()
            db.refresh(db_user)
            print(f"用户创建成功: id={db_user.id}")
        except Exception as e:
            db.rollback()
            print(f"数据库错误: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=f"Database error: {str(e)}"
            )
        finally:
            # 清理验证码
            if settings.requireEmailVerification:
                verification_codes.pop(user.email, None)
                print("已清理验证码")

        # 7. 确保用户有基本的使用限制配置
        print("配置用户限制...")
        rpm_limit = settings.rpmLimit
        rtm_limit = settings.rtmLimit
        daily_limit = settings.dailyLimit

        user_limits = [
            UserLimit(
                user_id=db_user.id,
                limit_type=LimitType.RPM,
                limit_value=rpm_limit
            ),
            UserLimit(
                user_id=db_user.id,
                limit_type=LimitType.RTM,
                limit_value=rtm_limit
            ),
            UserLimit(
                user_id=db_user.id,
                limit_type=LimitType.DAILY,
                limit_value=daily_limit
            )
        ]
        
        db.add_all(user_limits)
        
        try:
            db.commit()
            print("用户限制配置完成")
        except Exception as e:
            db.rollback()
            print(f"配置用户限制失败: {str(e)}")
            # 继续处理,不要因为限制设置失败而阻止注册

        print("注册成功完成")
        return db_user

    except HTTPException as he:
        print(f"HTTP异常: {he.detail}")
        raise he
    except Exception as e:
        print(f"未预期的错误: {str(e)}")
        print(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )
    finally:
        print("========== 注册请求处理结束 ==========\n")


@router.post("/api/users/register-with-invite")
async def register_with_invite(
    user: UserCreate,
    invite_code: str,
    email_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        print("\n========== 开始处理注册请求 ==========")
        print(f"用户名: {user.username}")
        print(f"邮箱: {user.email}")
        print(f"邀请码: {invite_code}")
        print(f"验证码: {email_code}")

        # 检查系统设置
        settings = db.query(SystemSettings).first()
        if not settings:
            print("错误: 找不到系统设置")
            raise HTTPException(status_code=400, detail="System settings not found")

        if not settings.allowRegistration:
            print("错误: 系统当前禁止注册")
            raise HTTPException(status_code=400, detail="Registration is currently disabled")

        # 验证邮箱验证码
        if settings.requireEmailVerification:
            print("系统要求邮箱验证")
            if not email_code:
                print("错误: 未提供验证码")
                raise HTTPException(status_code=400, detail="Email verification code required")
                
            verification = verification_codes.get(user.email)
            if not verification:
                print("错误: 找不到验证码记录")
                raise HTTPException(status_code=400, detail="Verification code not found")
            
            if verification['expires'] < datetime.now(timezone.utc):
                verification_codes.pop(user.email, None)
                print("错误: 验证码已过期")
                raise HTTPException(status_code=400, detail="Verification code expired")
                
            if verification['code'] != email_code:
                print(f"错误: 验证码不匹配 (输入: {email_code}, 期望: {verification['code']})")
                raise HTTPException(status_code=400, detail="Invalid verification code")

        # 检查用户名和邮箱是否已存在
        if db.query(User).filter(User.username == user.username).first():
            print("错误: 用户名已被注册")
            raise HTTPException(status_code=400, detail="Username already registered")
        
        if db.query(User).filter(User.email == user.email).first():
            print("错误: 邮箱已被注册")
            raise HTTPException(status_code=400, detail="Email already registered")

        # 检查邀请码 - 修改后的邀请码验证逻辑，只检查邀请码是否存在
        print(f"正在验证邀请码: {invite_code}")
        code = db.query(InviteCode).filter(
            InviteCode.code == invite_code
        ).first()

        if not code:
            print("错误: 邀请码不存在")
            raise HTTPException(status_code=400, detail="Invalid invite code")

        print(f"邀请码验证成功 (创建者ID: {code.user_id})")

        # 创建新用户
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=get_password_hash(user.password)
        )
        
        db.add(db_user)
        db.flush()  # 获取用户ID但不提交事务
        
        # 创建邀请记录
        reward = InviteReward(
            inviter_id=code.user_id,
            invitee_id=db_user.id,
            inviter_reward_type=settings.inviter_reward_type,
            inviter_reward_amount=settings.inviter_reward_amount,
            invitee_reward_type=settings.invitee_reward_type,
            invitee_reward_amount=settings.invitee_reward_amount
        )
        
        db.add(reward)
        print(f"创建邀请奖励记录: 邀请人={code.user_id}, 被邀请人={db_user.id}")
        
        # 处理邀请人奖励
        inviter = db.query(User).filter(User.id == code.user_id).first()
        if inviter:
            print(f"处理邀请人奖励 (类型: {settings.inviter_reward_type}, 数量: {settings.inviter_reward_amount})")
            if settings.inviter_reward_type == "coin":
                inviter.coins = (inviter.coins or 0) + settings.inviter_reward_amount
                # 记录金币变动
                inviter_coin_log = CoinLog(
                    user_id=inviter.id,
                    amount=settings.inviter_reward_amount,
                    type="admin",
                    description="Invite reward"
                )
                db.add(inviter_coin_log)
                print(f"邀请人获得 {settings.inviter_reward_amount} 金币")
            elif settings.inviter_reward_type == "vip":
                if not inviter.vip_until or inviter.vip_until < datetime.now(TIMEZONE):
                    inviter.vip_until = datetime.now(TIMEZONE)
                inviter.vip_until += timedelta(days=settings.inviter_reward_amount)
                print(f"邀请人获得 {settings.inviter_reward_amount} 天VIP")

        # 处理被邀请人奖励
        print(f"处理被邀请人奖励 (类型: {settings.invitee_reward_type}, 数量: {settings.invitee_reward_amount})")
        if settings.invitee_reward_type == "coin":
            db_user.coins = settings.invitee_reward_amount
            # 记录金币变动
            invitee_coin_log = CoinLog(
                user_id=db_user.id,
                amount=settings.invitee_reward_amount,
                type="admin",
                description="Registration reward"
            )
            db.add(invitee_coin_log)
            print(f"被邀请人获得 {settings.invitee_reward_amount} 金币")
        elif settings.invitee_reward_type == "vip":
            db_user.vip_until = datetime.now(TIMEZONE) + timedelta(days=settings.invitee_reward_amount)
            print(f"被邀请人获得 {settings.invitee_reward_amount} 天VIP")
        
        # 提交事务
        try:
            db.commit()
            print("数据库事务提交成功")
        except Exception as e:
            db.rollback()
            print(f"错误: 数据库事务提交失败 - {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        # 删除验证码
        if settings.requireEmailVerification:
            verification_codes.pop(user.email, None)
            print("已删除验证码记录")
        
        print("注册成功完成")
        return {"message": "Registration successful"}
        
    except HTTPException as he:
        print(f"HTTP异常: {he.detail}")
        db.rollback()
        raise he
    except Exception as e:
        print(f"未预期的错误: {str(e)}")
        db.rollback()
        print(f"Error in register_with_invite: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print("========== 注册请求处理结束 ==========\n")



@router.post("/api/token", response_model=LoginResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # 获取用户信息
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否被封禁
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been banned",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查系统是否允许登录
    settings = db.query(SystemSettings).first()
    if settings and not settings.allowLogin and user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System login is currently disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    is_valid = verify_password(form_data.password, user.hashed_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 确保用户有基本的使用限制配置
    # 获取系统默认设置
    if not settings:
        settings = SystemSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)

    # 检查并设置 RPM 限制
    rpm_limit = db.query(UserLimit).filter(
        UserLimit.user_id == user.id,
        UserLimit.limit_type == LimitType.RPM
    ).first()
    if not rpm_limit:
        rpm_limit = UserLimit(
            user_id=user.id,
            limit_type=LimitType.RPM,
            limit_value=settings.rpmLimit
        )
        db.add(rpm_limit)

    # 检查并设置 RTM 限制
    rtm_limit = db.query(UserLimit).filter(
        UserLimit.user_id == user.id,
        UserLimit.limit_type == LimitType.RTM
    ).first()
    if not rtm_limit:
        rtm_limit = UserLimit(
            user_id=user.id,
            limit_type=LimitType.RTM,
            limit_value=settings.rtmLimit
        )
        db.add(rtm_limit)

    # 检查并设置每日限制
    daily_limit = db.query(UserLimit).filter(
        UserLimit.user_id == user.id,
        UserLimit.limit_type == LimitType.DAILY
    ).first()
    if not daily_limit:
        daily_limit = UserLimit(
            user_id=user.id,
            limit_type=LimitType.DAILY,
            limit_value=settings.dailyLimit
        )
        db.add(daily_limit)

    try:
        # 提交所有限制配置更改
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error setting user limits: {str(e)}")
        # 继续处理，不要因为限制设置失败而阻止登录

    # 生成访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    
    # 确保 VIP 过期时间使用正确的时区
    vip_until = user.vip_until
    if vip_until and vip_until.tzinfo is None:
        vip_until = vip_until.replace(tzinfo=timezone.utc)
    
    # 返回登录响应
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
        "vip_until": vip_until
    }





@router.get("/api/auth/linuxdo/login")
async def linuxdo_login():
    """生成Linux.do OAuth登录URL"""
    oauth_url = f"{LINUXDO_OAUTH_URL}?response_type=code&client_id={LINUXDO_CLIENT_ID}"
    return {"url": oauth_url}


@router.get("/api/auth/linuxdo/callback")
async def linuxdo_callback(
    code: str,
    db: Session = Depends(get_db)
):
    """处理 Linux.do OAuth 回调"""
    try:
        print(f"\n========== 开始处理 Linux.do 回调 ==========")
        print(f"收到授权码: {code}")
        
        # 1. 获取访问令牌
        auth = base64.b64encode(f"{LINUXDO_CLIENT_ID}:{LINUXDO_CLIENT_SECRET}".encode()).decode()
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://connect.linux.do/oauth2/token",
                headers={
                    "Authorization": f"Basic {auth}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": "http://localhost:5173/auth/linuxdo/callback"
                }
            )
            
            if token_response.status_code != 200:
                print(f"获取令牌失败: {token_response.text}")
                raise HTTPException(
                    status_code=400,
                    detail="Failed to get access token"
                )
                
            token_data = token_response.json()
            access_token = token_data["access_token"]
            print("成功获取访问令牌")

        # 2. 获取用户信息
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                "https://connect.linux.do/api/user",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if user_response.status_code != 200:
                print(f"获取用户信息失败: {user_response.text}")
                raise HTTPException(
                    status_code=400,
                    detail="Failed to get user info"
                )
                
            linuxdo_user = user_response.json()
            print(f"获取到用户信息: {linuxdo_user}")

        # 3. 查找或创建用户，处理用户名重复
        base_username = linuxdo_user["username"]
        username = base_username
        suffix = 1
        
        while True:
            existing_user = db.query(User).filter(User.username == username).first()
            if not existing_user:
                break
            username = f"{base_username}{suffix}"
            suffix += 1

        # 查找邮箱对应的用户
        db_user = db.query(User).filter(User.email == linuxdo_user["email"]).first()
        
        if not db_user:
            # 创建新用户，使用处理后的唯一用户名
            db_user = User(
                username=username,  # 使用处理后的唯一用户名
                email=linuxdo_user["email"],
                hashed_password=get_password_hash(secrets.token_urlsafe(32)),
                role=UserRole.USER,
                is_active=True,
                created_at=datetime.now(TIMEZONE)
            )
            db.add(db_user)
            
            print(f"创建新用户: {db_user.username}")
            
            # 设置基本使用限制
            await ensure_user_limits(db_user.id, db)

        # 4. 生成访问令牌
        access_token = create_access_token(
            data={"sub": db_user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        db.commit()
        
        print("登录成功，生成访问令牌")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "role": db_user.role,
            "is_active": db_user.is_active,
            "vip_until": db_user.vip_until
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"处理回调时出错: {str(e)}")
        print(f"错误详情:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"OAuth callback failed: {str(e)}"
        )
    finally:
        print("========== Linux.do 回调处理结束 ==========\n")


@router.get("/api/auth/github/login")
async def github_login():
    """生成 GitHub OAuth 登录 URL"""
    oauth_url = f"{GITHUB_OAUTH_URL}?client_id={GITHUB_CLIENT_ID}&scope=user:email"
    return {"url": oauth_url}

@router.get("/api/auth/github/callback")
async def github_callback(
    code: str,
    db: Session = Depends(get_db)
):
    try:
        print("\n========== 开始处理 GitHub 回调 ==========")
        print(f"收到授权码: {code}")

        # 创建一个不验证SSL证书的客户端 
        async with httpx.AsyncClient(verify=False) as client:
            # 1. 获取访问令牌
            token_response = await client.post(
                GITHUB_TOKEN_URL,
                headers={"Accept": "application/json"},
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code
                }
            )
            
            if token_response.status_code != 200:
                print(f"获取令牌失败: {token_response.text}")
                raise HTTPException(
                    status_code=400,
                    detail="Failed to get access token"
                )
                
            token_data = token_response.json()
            access_token = token_data["access_token"]
            print("成功获取访问令牌")

            # 2. 获取用户信息
            user_response = await client.get(
                GITHUB_USER_API,
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/json"
                }
            )
            
            if user_response.status_code != 200:
                print(f"获取用户信息失败: {user_response.text}")
                raise HTTPException(
                    status_code=400,
                    detail="Failed to get user info"
                )
                
            github_user = user_response.json()
            print(f"获取到用户信息: {github_user}")

            # 获取用户邮箱
            if not github_user.get("email"):
                email_response = await client.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json"  
                    }
                )
                if email_response.status_code == 200:
                    emails = email_response.json()
                    primary_email = next(
                        (email["email"] for email in emails if email["primary"]),
                        None
                    )
                    if primary_email:
                        github_user["email"] = primary_email

        # 3. 处理用户名重复
        base_username = github_user["login"]
        username = base_username
        suffix = 1
        
        while True:
            existing_user = db.query(User).filter(User.username == username).first()
            if not existing_user:
                break
            username = f"{base_username}{suffix}"
            suffix += 1

        # 查找或创建用户
        db_user = db.query(User).filter(User.email == github_user["email"]).first()
        if not db_user:
            # 创建新用户，使用处理后的唯一用户名
            db_user = User(
                username=username,  # 使用处理后的唯一用户名
                email=github_user["email"], 
                hashed_password=get_password_hash(secrets.token_urlsafe(32)),
                role=UserRole.USER,
                is_active=True,
                created_at=datetime.now(TIMEZONE)
            )
            db.add(db_user)
            print(f"创建新用户: {db_user.username}")
            
            # 设置基本使用限制
            await ensure_user_limits(db_user.id, db)
            
        # 4. 生成访问令牌
        access_token = create_access_token(
            data={"sub": db_user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        db.commit()
        
        print("登录成功,生成访问令牌")
        
        # 确保 VIP 时间使用正确的时区
        vip_until = db_user.vip_until
        if vip_until and vip_until.tzinfo is None:
            vip_until = vip_until.replace(tzinfo=timezone.utc)
            
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "role": db_user.role,
            "is_active": db_user.is_active,
            "vip_until": vip_until
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"处理回调时出错: {str(e)}")
        print(f"错误详情:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"OAuth callback failed: {str(e)}"
        )
    finally:
        print("========== GitHub 回调处理结束 ==========\n")


# 发送重置密码验证码
@router.post("/api/reset-password/send-code")
async def send_reset_code(
    email_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        print("\n========== 开始处理发送验证码请求 ==========")
        email = email_data.get("email")
        print(f"目标邮箱: {email}")

        if not email:
            raise HTTPException(status_code=400, detail="邮箱地址不能为空")

        # 检查用户是否存在
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="未找到该邮箱对应的用户")

        # 获取系统设置
        settings = db.query(SystemSettings).first()
        if not settings or not settings.smtp:
            print("错误: 未找到系统设置")
            raise HTTPException(status_code=400, detail="系统邮箱未配置")

        print("系统SMTP设置:")
        print(f"- Host: {settings.smtp.get('host')}")
        print(f"- Port: {settings.smtp.get('port')}")
        print(f"- User: {settings.smtp.get('user')}")
        print(f"- From: {settings.smtp.get('from')}")

        # 生成6位数验证码
        code = ''.join(random.choices(string.digits, k=6))
        print(f"生成的验证码: {code}")

        # 保存验证码和过期时间
        verification_codes[email] = {
            "code": code,
            "expires": datetime.now(timezone.utc) + timedelta(minutes=15),
            "type": "reset_password"
        }

        # 构建邮件内容
        html_content = f"""
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
            <h2 style="color: #333;">密码重置验证码</h2>
            <p>您好，</p>
            <p>您正在尝试重置密码。您的验证码是：</p>
            <div style="background-color: #f4f4f4; padding: 10px; margin: 20px 0; text-align: center;">
                <span style="font-size: 24px; font-weight: bold; letter-spacing: 5px;">{code}</span>
            </div>
            <p>此验证码将在15分钟后过期。如果这不是您本人的操作，请忽略此邮件。</p>
            <p style="color: #666; margin-top: 30px;">此邮件由系统自动发送，请勿回复。</p>
        </div>
        """

        # 创建邮件消息
        msg = MIMEText(html_content, 'html', 'utf-8')
        msg['Subject'] = '密码重置验证码'
        msg['From'] = settings.smtp['from']
        msg['To'] = email

        print("\n尝试发送邮件...")
        try:
            # 使用 SMTP 并启用 STARTTLS
            server = smtplib.SMTP(settings.smtp['host'], settings.smtp['port'])
            server.starttls()  # 启用 TLS
            print("SMTP 连接并启用 TLS 成功")
            
            server.login(settings.smtp['user'], settings.smtp['pass'])
            print("SMTP 登录成功")
            
            server.send_message(msg)
            print("邮件发送成功")
            
            server.quit()
            print("SMTP 连接已关闭")
            
        except Exception as smtp_error:
            print(f"SMTP错误: {str(smtp_error)}")
            print(f"堆栈跟踪:\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"邮件发送失败: {str(smtp_error)}")

        print("\n验证码发送处理完成")
        return {"message": "验证码已发送到您的邮箱"}

    except HTTPException as he:
        print(f"HTTP异常: {str(he)}")
        raise
    except Exception as e:
        print(f"未预期的错误: {str(e)}")
        print(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print("========== 发送验证码请求处理结束 ==========\n")

# 验证验证码并重置密码
@router.post("/api/reset-password/verify")
async def verify_reset_code(
    reset_data: dict,
    db: Session = Depends(get_db)
):
    try:
        print("\n========== 开始处理密码重置请求 ==========")
        email = reset_data.get("email")
        code = reset_data.get("code")
        new_password = reset_data.get("newPassword")

        print(f"邮箱: {email}")
        print(f"验证码: {code}")

        if not all([email, code, new_password]):
            raise HTTPException(status_code=400, detail="请提供所有必需的信息")

        # 验证验证码
        verification = verification_codes.get(email)
        if not verification:
            print("验证码不存在")
            raise HTTPException(status_code=400, detail="验证码不存在或已过期")

        if verification['type'] != 'reset_password':
            print("验证码类型错误")
            raise HTTPException(status_code=400, detail="无效的验证码类型")

        if verification['expires'] < datetime.now(timezone.utc):
            verification_codes.pop(email, None)
            print("验证码已过期")
            raise HTTPException(status_code=400, detail="验证码已过期")

        if verification['code'] != code:
            print("验证码不匹配")
            raise HTTPException(status_code=400, detail="验证码错误")

        # 更新用户密码
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print("用户不存在")
            raise HTTPException(status_code=404, detail="未找到用户")

        # 更新密码
        user.hashed_password = get_password_hash(new_password)
        print("密码已更新")

        try:
            db.commit()
            # 清除验证码
            verification_codes.pop(email, None)
            print("数据库更新成功，验证码已清除")
            return {"message": "密码重置成功"}
        except Exception as db_error:
            db.rollback()
            print(f"数据库更新失败: {str(db_error)}")
            raise HTTPException(status_code=500, detail="重置密码失败")

    except HTTPException as he:
        print(f"HTTP异常: {str(he)}")
        raise
    except Exception as e:
        print(f"未预期的错误: {str(e)}")
        print(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print("========== 密码重置请求处理结束 ==========\n")

# 管理员测试 SMTP 设置
@router.post("/api/admin/smtp/test")
async def test_smtp_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """测试 SMTP 设置是否正常工作"""
    try:
        print("\n========== 开始 SMTP 测试 ==========")
        settings = db.query(SystemSettings).first()
        if not settings or not settings.smtp:
            raise HTTPException(status_code=400, detail="SMTP not configured")

        smtp_settings = settings.smtp
        test_email = current_user.email

        print(f"SMTP 配置:")
        print(f"- Host: {smtp_settings['host']}")
        print(f"- Port: {smtp_settings['port']}")
        print(f"- User: {smtp_settings['user']}")
        print(f"- From: {smtp_settings['from']}")
        print(f"测试邮件接收地址: {test_email}")

        # 创建测试邮件
        msg = MIMEText('This is a test email from the system.', 'plain', 'utf-8')
        msg['Subject'] = 'SMTP Test Email'
        msg['From'] = smtp_settings['from']
        msg['To'] = test_email

        try:
            # 使用 SMTP 并启用 STARTTLS
            server = smtplib.SMTP(smtp_settings['host'], smtp_settings['port'])
            server.starttls()
            print("SMTP 连接并启用 TLS 成功")
            
            server.login(smtp_settings['user'], smtp_settings['pass'])
            print("SMTP 登录成功")
            
            server.send_message(msg)
            print("测试邮件发送成功")
            
            server.quit()
            print("SMTP 连接已关闭")
            
            return {"message": "SMTP test successful"}
        except Exception as smtp_error:
            print(f"SMTP错误: {str(smtp_error)}")
            print(f"堆栈跟踪:\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"SMTP test failed: {str(smtp_error)}")

    except Exception as e:
        print(f"测试过程出错: {str(e)}")
        print(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print("========== SMTP 测试结束 ==========\n")


# 发送重置密码验证码
@router.post("/api/reset-password/send-code")
async def send_reset_code(
    email_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        print("\n========== 开始处理发送验证码请求 ==========")
        email = email_data.get("email")
        print(f"目标邮箱: {email}")

        if not email:
            raise HTTPException(status_code=400, detail="邮箱地址不能为空")

        # 检查用户是否存在
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="未找到该邮箱对应的用户")

        # 获取系统设置
        settings = db.query(SystemSettings).first()
        if not settings or not settings.smtp:
            print("错误: 未找到系统设置")
            raise HTTPException(status_code=400, detail="系统邮箱未配置")

        print("系统SMTP设置:")
        print(f"- Host: {settings.smtp.get('host')}")
        print(f"- Port: {settings.smtp.get('port')}")
        print(f"- User: {settings.smtp.get('user')}")
        print(f"- From: {settings.smtp.get('from')}")

        # 生成6位数验证码
        code = ''.join(random.choices(string.digits, k=6))
        print(f"生成的验证码: {code}")

        # 保存验证码和过期时间
        verification_codes[email] = {
            "code": code,
            "expires": datetime.now(timezone.utc) + timedelta(minutes=15),
            "type": "reset_password"
        }

        # 构建邮件内容
        html_content = f"""
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
            <h2 style="color: #333;">密码重置验证码</h2>
            <p>您好，</p>
            <p>您正在尝试重置密码。您的验证码是：</p>
            <div style="background-color: #f4f4f4; padding: 10px; margin: 20px 0; text-align: center;">
                <span style="font-size: 24px; font-weight: bold; letter-spacing: 5px;">{code}</span>
            </div>
            <p>此验证码将在15分钟后过期。如果这不是您本人的操作，请忽略此邮件。</p>
            <p style="color: #666; margin-top: 30px;">此邮件由系统自动发送，请勿回复。</p>
        </div>
        """

        # 创建邮件消息
        msg = MIMEText(html_content, 'html', 'utf-8')
        msg['Subject'] = '密码重置验证码'
        msg['From'] = settings.smtp['from']
        msg['To'] = email

        print("\n尝试发送邮件...")
        try:
            # 使用 SMTP 并启用 STARTTLS
            server = smtplib.SMTP(settings.smtp['host'], settings.smtp['port'])
            server.starttls()  # 启用 TLS
            print("SMTP 连接并启用 TLS 成功")
            
            server.login(settings.smtp['user'], settings.smtp['pass'])
            print("SMTP 登录成功")
            
            server.send_message(msg)
            print("邮件发送成功")
            
            server.quit()
            print("SMTP 连接已关闭")
            
        except Exception as smtp_error:
            print(f"SMTP错误: {str(smtp_error)}")
            print(f"堆栈跟踪:\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"邮件发送失败: {str(smtp_error)}")

        print("\n验证码发送处理完成")
        return {"message": "验证码已发送到您的邮箱"}

    except HTTPException as he:
        print(f"HTTP异常: {str(he)}")
        raise
    except Exception as e:
        print(f"未预期的错误: {str(e)}")
        print(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print("========== 发送验证码请求处理结束 ==========\n")

# 验证验证码并重置密码
@router.post("/api/reset-password/verify")
async def verify_reset_code(
    reset_data: dict,
    db: Session = Depends(get_db)
):
    try:
        print("\n========== 开始处理密码重置请求 ==========")
        email = reset_data.get("email")
        code = reset_data.get("code")
        new_password = reset_data.get("newPassword")

        print(f"邮箱: {email}")
        print(f"验证码: {code}")

        if not all([email, code, new_password]):
            raise HTTPException(status_code=400, detail="请提供所有必需的信息")

        # 验证验证码
        verification = verification_codes.get(email)
        if not verification:
            print("验证码不存在")
            raise HTTPException(status_code=400, detail="验证码不存在或已过期")

        if verification['type'] != 'reset_password':
            print("验证码类型错误")
            raise HTTPException(status_code=400, detail="无效的验证码类型")

        if verification['expires'] < datetime.now(timezone.utc):
            verification_codes.pop(email, None)
            print("验证码已过期")
            raise HTTPException(status_code=400, detail="验证码已过期")

        if verification['code'] != code:
            print("验证码不匹配")
            raise HTTPException(status_code=400, detail="验证码错误")

        # 更新用户密码
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print("用户不存在")
            raise HTTPException(status_code=404, detail="未找到用户")

        # 更新密码
        user.hashed_password = get_password_hash(new_password)
        print("密码已更新")

        try:
            db.commit()
            # 清除验证码
            verification_codes.pop(email, None)
            print("数据库更新成功，验证码已清除")
            return {"message": "密码重置成功"}
        except Exception as db_error:
            db.rollback()
            print(f"数据库更新失败: {str(db_error)}")
            raise HTTPException(status_code=500, detail="重置密码失败")

    except HTTPException as he:
        print(f"HTTP异常: {str(he)}")
        raise
    except Exception as e:
        print(f"未预期的错误: {str(e)}")
        print(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print("========== 密码重置请求处理结束 ==========\n")

# 管理员测试 SMTP 设置
@router.post("/api/admin/smtp/test")
async def test_smtp_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """测试 SMTP 设置是否正常工作"""
    try:
        print("\n========== 开始 SMTP 测试 ==========")
        settings = db.query(SystemSettings).first()
        if not settings or not settings.smtp:
            raise HTTPException(status_code=400, detail="SMTP not configured")

        smtp_settings = settings.smtp
        test_email = current_user.email

        print(f"SMTP 配置:")
        print(f"- Host: {smtp_settings['host']}")
        print(f"- Port: {smtp_settings['port']}")
        print(f"- User: {smtp_settings['user']}")
        print(f"- From: {smtp_settings['from']}")
        print(f"测试邮件接收地址: {test_email}")

        # 创建测试邮件
        msg = MIMEText('This is a test email from the system.', 'plain', 'utf-8')
        msg['Subject'] = 'SMTP Test Email'
        msg['From'] = smtp_settings['from']
        msg['To'] = test_email

        try:
            # 使用 SMTP 并启用 STARTTLS
            server = smtplib.SMTP(smtp_settings['host'], smtp_settings['port'])
            server.starttls()
            print("SMTP 连接并启用 TLS 成功")
            
            server.login(smtp_settings['user'], smtp_settings['pass'])
            print("SMTP 登录成功")
            
            server.send_message(msg)
            print("测试邮件发送成功")
            
            server.quit()
            print("SMTP 连接已关闭")
            
            return {"message": "SMTP test successful"}
        except Exception as smtp_error:
            print(f"SMTP错误: {str(smtp_error)}")
            print(f"堆栈跟踪:\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"SMTP test failed: {str(smtp_error)}")

    except Exception as e:
        print(f"测试过程出错: {str(e)}")
        print(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        print("========== SMTP 测试结束 ==========\n")




@router.get("/api/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前登录用户的详细信息"""
    # 从数据库获取最新的用户信息
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 从 SystemSettings 获取签到配置
    settings = db.query(SystemSettings).first()
    signin_enabled = settings.signin_enabled if settings else False
    signin_reward_type = settings.signin_reward_type if settings else "coin"
    signin_reward_amount = settings.signin_reward_amount if settings else 0
    
    # 确保时区信息的一致性
    today = datetime.now(TIMEZONE).date()
    # 转换为 naive datetime 用于数据库查询
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # 检查今天是否已签到
    signed = db.query(SigninLog).filter(
        SigninLog.user_id == user.id,
        func.date(SigninLog.created_at) >= today_start,
        func.date(SigninLog.created_at) <= today_end
    ).first() is not None

    # 确保 VIP 时间有正确的时区信息
    vip_until = user.vip_until
    if vip_until:
        if vip_until.tzinfo is None:
            vip_until = vip_until.replace(tzinfo=TIMEZONE)
        else:
            vip_until = vip_until.astimezone(TIMEZONE)

    # 构建响应数据
    response_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "is_banned": user.is_banned,
        "vip_until": vip_until,
        "coins": user.coins or 0,
        "signin_enabled": signin_enabled,
        "today_signed": signed,
        "signin_reward_type": signin_reward_type,
        "signin_reward_amount": signin_reward_amount
    }
    
    return response_data

@router.post("/api/users/send-verification-code")
async def send_verification_code(
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # 检查系统设置
        settings = db.query(SystemSettings).first()
        if not settings:
            raise HTTPException(status_code=400, detail="System settings not found")
            
        if not settings.requireEmailVerification:
            raise HTTPException(status_code=400, detail="Email verification is disabled")

        # 检查是否启用了白名单
        if settings.enable_email_whitelist:
            # 获取所有活跃的白名单规则
            rules = db.query(EmailWhitelistRule).filter(
                EmailWhitelistRule.is_active == True
            ).all()
            
            # 如果白名单启用但没有规则，拒绝所有邮箱
            if not rules:
                raise HTTPException(
                    status_code=403,
                    detail="Email whitelist is enabled but no rules are defined. Please contact administrator."
                )
            
            # 检查邮箱是否匹配任何规则
            is_whitelisted = False
            for rule in rules:
                if email.endswith(rule.pattern):
                    is_whitelisted = True
                    break
                    
            if not is_whitelisted:
                raise HTTPException(
                    status_code=403,
                    detail="This email domain is not whitelisted"
                )

        # 清理过期的验证码
        cleanup_expired_codes()
        
        # 生成6位数验证码
        code = ''.join(random.choices(string.digits, k=6))
        
        # 保存验证码,5分钟后过期
        verification_codes[email] = {
            "code": code,
            "expires": datetime.now(timezone.utc) + timedelta(minutes=5)
        }
        
        # 使用系统配置的SMTP设置
        smtp_settings = settings.smtp
        if not smtp_settings:
            raise HTTPException(status_code=400, detail="SMTP not configured")

        try:
            # 创建MIMEText对象
            msg = MIMEText(f'您的验证码是: {code}', 'plain', 'utf-8')
            msg['Subject'] = '注册验证码'
            msg['From'] = smtp_settings['from']
            msg['To'] = email
            
            # 连接SMTP服务器并发送
            server = smtplib.SMTP_SSL(smtp_settings['host'])
            server.login(smtp_settings['user'], smtp_settings['pass'])
            server.send_message(msg)
            server.quit()
            
            return {"message": "Verification code sent"}
            
        except Exception as e:
            print(f"SMTP Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
            
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        verification_codes.pop(email, None)  # 清理验证码
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
    
@router.post("/api/users/password-reset")
async def request_password_reset(
    reset_request: PasswordReset,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == reset_request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(hours=24)
    
    try:
        db.commit()
        background_tasks.add_task(send_reset_email, reset_request.email, token)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Password reset email sent"}

@router.post("/api/users/password-reset/confirm")
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.reset_token == reset_confirm.token,
        User.reset_token_expiry > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user.hashed_password = get_password_hash(reset_confirm.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Password reset successful"}


@router.get("/api/user/coins/logs", response_model=CoinStatsResponse)
async def get_user_coin_logs(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页记录数"),
    type: Optional[str] = Query(None, description="类型过滤：admin/consume/signin/income"), 
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 计算分页偏移量
        skip = (page - 1) * page_size
        
        # 构建基础查询
        query = db.query(CoinLog).filter(CoinLog.user_id == current_user.id)
        
        # 应用过滤条件
        if type:
            query = query.filter(CoinLog.type == type)
        if start_date:
            query = query.filter(CoinLog.created_at >= start_date)
        if end_date:
            query = query.filter(CoinLog.created_at <= end_date)
            
        # 计算各类型总额
        total_income = db.query(func.sum(CoinLog.amount))\
            .filter(
                CoinLog.user_id == current_user.id,
                CoinLog.amount > 0,
                CoinLog.type == 'income'
            ).scalar() or 0
            
        total_expense = db.query(func.sum(CoinLog.amount))\
            .filter(
                CoinLog.user_id == current_user.id,
                CoinLog.amount < 0,
                CoinLog.type == 'consume'
            ).scalar() or 0
            
        total_admin = db.query(func.sum(CoinLog.amount))\
            .filter(
                CoinLog.user_id == current_user.id,
                CoinLog.type == 'admin'
            ).scalar() or 0
            
        total_signin = db.query(func.sum(CoinLog.amount))\
            .filter(
                CoinLog.user_id == current_user.id,
                CoinLog.type == 'signin'
            ).scalar() or 0

        # 获取总记录数
        total_records = query.count()
        
        # 获取分页数据
        logs = query.order_by(CoinLog.created_at.desc())\
            .offset(skip)\
            .limit(page_size)\
            .all()
            
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "total_admin": total_admin,
            "total_signin": total_signin,
            "current_balance": current_user.coins or 0,
            "logs": logs,
            "total": total_records,
            "page": page,
            "page_size": page_size
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取金币记录失败: {str(e)}"
        )







@router.post("/api/signin")
async def user_signin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 检查签到设置
    settings = db.query(SystemSettings).first()
    if not settings or not settings.signin_enabled:
        raise HTTPException(status_code=400, detail="Signin is disabled")
        
    # 检查今天是否已签到
    today = datetime.now(TIMEZONE).date()
    signed = db.query(SigninLog).filter(
        SigninLog.user_id == current_user.id,
        func.date(SigninLog.created_at) == today
    ).first()
    
    if signed:
        raise HTTPException(status_code=400, detail="Already signed in today")
        
    # 记录签到
    signin_log = SigninLog(
        user_id=current_user.id,
        reward_type=settings.signin_reward_type,
        reward_amount=settings.signin_reward_amount
    )
    db.add(signin_log)
    
    # 发放奖励
    if settings.signin_reward_type == "coin":
        # 确保 coins 不是 None
        if current_user.coins is None:
            current_user.coins = 0
        current_user.coins += settings.signin_reward_amount
        
        # 记录金币变动
        coin_log = CoinLog(
            user_id=current_user.id,
            amount=settings.signin_reward_amount,
            type="signin",
            description="Daily signin reward"
        )
        db.add(coin_log)
    elif settings.signin_reward_type == "vip":
        # 处理VIP时间，确保时区信息正确
        now = datetime.now(TIMEZONE)
        if not current_user.vip_until:
            current_user.vip_until = now
        else:
            # 确保 vip_until 有时区信息
            if current_user.vip_until.tzinfo is None:
                current_user.vip_until = current_user.vip_until.replace(tzinfo=TIMEZONE)
            if current_user.vip_until < now:
                current_user.vip_until = now
                
        current_user.vip_until += timedelta(days=settings.signin_reward_amount)
        
    try:
        db.commit()
        return {
            "message": "Signin successful",
            "reward_type": settings.signin_reward_type,
            "reward_amount": settings.signin_reward_amount
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/users/invite-code")
async def generate_invite_code(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成邀请码 - 每个用户只能生成一个"""
    # 检查系统是否启用邀请功能
    settings = db.query(SystemSettings).first()
    if not settings or not settings.invite_enabled:
        raise HTTPException(status_code=400, detail="Invite system is disabled")
    
    # 检查用户是否已经生成过邀请码
    existing_code = db.query(InviteCode).filter(
        InviteCode.user_id == current_user.id,
    ).first()
    
    if existing_code:
        return {"code": existing_code.code}  # 如果已有邀请码就返回现有的
        
    # 生成新的邀请码
    timestamp = datetime.now().strftime('%y%m%d%H%M%S')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    code = f"{random_part}{timestamp[-4:]}"  # 组合成8位邀请码
    
    invite_code = InviteCode(
        code=code,
        user_id=current_user.id
    )
    
    db.add(invite_code)
    try:
        db.commit()
        db.refresh(invite_code)
        return {"code": code}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/users/invite-stats", response_model=InviteStatsResponse)
async def get_invite_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取邀请统计信息"""
    # 统计总邀请数
    total_invites = db.query(InviteReward)\
        .filter(InviteReward.inviter_id == current_user.id)\
        .count()
    
    # 按类型统计总奖励
    rewards = {
        "vip": 0,
        "coin": 0
    }
    
    inviter_rewards = db.query(InviteReward)\
        .filter(InviteReward.inviter_id == current_user.id)\
        .all()
        
    for reward in inviter_rewards:
        if reward.inviter_reward_type == "vip":
            rewards["vip"] += reward.inviter_reward_amount
        else:
            rewards["coin"] += reward.inviter_reward_amount
    
    # 获取最近的邀请记录
    recent_invites = db.query(InviteReward, User)\
        .join(User, InviteReward.invitee_id == User.id)\
        .filter(InviteReward.inviter_id == current_user.id)\
        .order_by(InviteReward.created_at.desc())\
        .limit(10)\
        .all()
    
    recent_invites_list = [
        {
            "invitee_username": user.username,
            "reward_type": reward.inviter_reward_type,
            "reward_amount": reward.inviter_reward_amount,
            "created_at": reward.created_at
        }
        for reward, user in recent_invites
    ]
    
    return {
        "total_invites": total_invites,
        "total_rewards": rewards,
        "recent_invites": recent_invites_list
    }

@router.get("/api/users/inviter")
async def get_inviter_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取邀请人信息"""
    # 查找当前用户是否被邀请（从 InviteReward 表中查询）
    invite_record = db.query(InviteReward, User)\
        .join(User, InviteReward.inviter_id == User.id)\
        .filter(InviteReward.invitee_id == current_user.id)\
        .first()
    
    if not invite_record:
        return {"inviter": None}
        
    reward, inviter = invite_record
    
    return {
        "inviter": {
            "username": inviter.username,
            "invite_time": reward.created_at,
            "reward": {
                "type": reward.inviter_reward_type,
                "amount": reward.inviter_reward_amount
            }
        }
    }


@router.get("/api/admin/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    users = db.query(User).offset(skip).limit(limit).all()
    # 确保返回的用户对象中所有必要字段都有值
    for user in users:
        if user.is_banned is None:
            user.is_banned = False
        if user.coins is None:
            user.coins = 0
    return users


# 添加管理员创建用户的路由
@router.post("/api/admin/users", response_model=UserResponse)
async def create_user_admin(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    # 检查用户名是否已存在
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 检查邮箱是否已存在
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,  # 现在可以直接使用 user.role
        is_active=True,
        is_banned=False
    )
    
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {str(e)}")  # 添加错误日志
        raise HTTPException(status_code=400, detail=str(e))
    
    return db_user

@router.put("/api/admin/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    # 检查用户是否存在
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 获取要更新的字段
    update_data = user_update.dict(exclude_unset=True)
    
    # 如果要更新邮箱,先检查是否已存在
    if "email" in update_data:
        existing_user = db.query(User).filter(
            User.email == update_data["email"],
            User.id != user_id  # 排除当前用户
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
    
    # 如果要更新密码,进行哈希处理
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
    # 确保 is_banned 字段有值
    if db_user.is_banned is None:
        db_user.is_banned = False

    # 更新用户字段
    for key, value in update_data.items():
        setattr(db_user, key, value)

    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return db_user

@router.delete("/api/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        db.delete(db_user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "User deleted successfully"}

# 添加封禁/解封路由
@router.patch("/api/admin/users/{user_id}/ban")
async def toggle_user_ban(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # 不允许封禁管理员
    if db_user.role == UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="Cannot ban admin users")
        
    db_user.is_banned = not db_user.is_banned
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return {
        "message": f"User is now {'banned' if db_user.is_banned else 'unbanned'}"
    }

@router.put("/api/admin/users/{user_id}/vip")  # 改为使用 PUT
async def update_user_vip(
    user_id: int,
    vip_update: VipUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    try:
        print(f"Received VIP update request for user {user_id}: {vip_update}")
        
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # 处理 VIP 时间
        now = datetime.now(TIMEZONE)
        
        if vip_update.operation == "add":
            # 如果没有 VIP 或已过期，从当前时间开始计算
            if not db_user.vip_until or db_user.vip_until.replace(tzinfo=TIMEZONE) < now:
                db_user.vip_until = now
            db_user.vip_until += timedelta(days=vip_update.days)
            
        elif vip_update.operation == "subtract":
            # 如果有 VIP 且未过期
            if db_user.vip_until:
                vip_until = db_user.vip_until.replace(tzinfo=TIMEZONE)
                if vip_until > now:
                    db_user.vip_until -= timedelta(days=vip_update.days)
                    # 如果减去后的时间早于当前时间，则设置为已过期
                    if db_user.vip_until.replace(tzinfo=TIMEZONE) < now:
                        db_user.vip_until = now
                else:
                    raise HTTPException(status_code=400, detail="User does not have active VIP")
            else:
                raise HTTPException(status_code=400, detail="User does not have active VIP")
        else:
            raise HTTPException(status_code=400, detail="Invalid operation")

        # 获取系统设置的VIP限制值
        settings = db.query(SystemSettings).first()
        if not settings:
            raise HTTPException(status_code=400, detail="System settings not found")

        # 更新用户限制
        if db_user.vip_until.replace(tzinfo=TIMEZONE) > now:  # 如果仍然是 VIP
            # 删除现有限制
            db.query(UserLimit).filter(UserLimit.user_id == user_id).delete()
            
            # 创建新的 VIP 限制
            new_limits = [
                UserLimit(
                    user_id=user_id,
                    limit_type=LimitType.RPM,
                    limit_value=settings.vipRpmLimit
                ),
                UserLimit(
                    user_id=user_id,
                    limit_type=LimitType.RTM,
                    limit_value=settings.vipRtmLimit
                ),
                UserLimit(
                    user_id=user_id,
                    limit_type=LimitType.DAILY,
                    limit_value=settings.vipDailyLimit
                )
            ]
            db.add_all(new_limits)

        db.commit()
        return {
            "message": f"VIP status updated successfully ({vip_update.operation})",
            "userId": db_user.id,
            "username": db_user.username,
            "role": db_user.role.value,
            "isVIP": db_user.vip_until.replace(tzinfo=TIMEZONE) > now if db_user.vip_until else False,
            "vipUntil": db_user.vip_until
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in update_user_vip: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))



# 管理员操作用户金币
@router.post("/api/admin/users/{user_id}/coins")
async def update_user_coins(
    user_id: int,
    amount: int = Query(..., description="金币变动数量"),  # 正数增加,负数减少
    description: str = Query(..., description="变动说明"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 确保 coins 字段有初始值
    if user.coins is None:
        user.coins = 0
    
    # 检查减少金币时余额是否足够
    if amount < 0 and user.coins + amount < 0:
        raise HTTPException(status_code=400, detail="Insufficient coins")
        
    user.coins += amount
    
    # 记录变动
    coin_log = CoinLog(
        user_id=user_id,
        amount=amount,
        type="admin",
        description=description
    )
    db.add(coin_log)
    
    try:
        db.commit()
        db.refresh(user)
        return {"message": "Coins updated successfully", "current_coins": user.coins}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))




# 修改搜索接口
@router.get("/api/admin/users/search")
async def search_users(
    query: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    search = f"%{query}%"
    users = db.query(User).filter(
        or_(
            User.username.ilike(search),
            User.email.ilike(search)
        )
    ).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "is_banned": user.is_banned,
            "vip_until": user.vip_until,
            "coins": user.coins or 0  # 添加金币字段，确保值为数字
        }
        for user in users
    ]


@router.get("/api/admin/users/stats")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    try:
        now = datetime.now(TIMEZONE)
        today = now.date()
        today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=TIMEZONE)
        today_end = datetime.combine(today, datetime.max.time()).replace(tzinfo=TIMEZONE)

        # 获取总用户数
        total_users = db.query(User).count()

        # 获取有效VIP用户数 (只统计未过期的VIP用户)
        total_vip_users = db.query(User).filter(
            and_(
                User.vip_until.isnot(None),
                User.vip_until > now
            )
        ).count()

        # 获取今日新注册用户数
        today_new_users = db.query(User).filter(
            and_(
                User.created_at >= today_start,
                User.created_at <= today_end
            )
        ).count()

        # 获取今日新增VIP用户数
        today_new_vip_users = db.query(User).filter(
            and_(
                User.vip_until.isnot(None),
                User.vip_until > now,
                User.vip_until >= today_start,
                User.vip_until <= today_end + timedelta(days=1)
            )
        ).count()

        return {
            "total_users": total_users,
            "total_vip_users": total_vip_users,
            "today_new_users": today_new_users,
            "today_new_vip_users": today_new_vip_users,
            "stats_time": now.isoformat()
        }

    except Exception as e:
        print(f"Error getting user stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取用户统计数据失败: {str(e)}"
        )





# 在后端添加文件上传路由
@router.post("/api/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 创建上传目录
        upload_dir = Path("uploads/files")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        uploaded_files = []
        for file in files:
            # 生成唯一文件名和ID
            file_ext = Path(file.filename).suffix
            file_id = secrets.token_hex(8)
            unique_filename = f"{file_id}{file_ext}"
            file_path = upload_dir / unique_filename
            
            # 保存文件
            with file_path.open("wb") as buffer:
                content = await file.read()
                buffer.write(content)
                
            # 保存文件记录
            file_record = UploadedFile(
                id=file_id,
                user_id=current_user.id,
                filename=file.filename,
                url=f"/uploads/files/{unique_filename}",
                type=file.content_type
            )
            db.add(file_record)
            
            # 构建响应信息
            file_info = {
                "id": file_id,
                "name": file.filename,
                "url": f"/uploads/files/{unique_filename}",
                "type": file.content_type
            }
            uploaded_files.append(file_info)
            
        db.commit()
        
        return {
            "message": "Files uploaded successfully",
            "files": uploaded_files
        }
        
    except Exception as e:
        if 'db' in locals():
            db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )
