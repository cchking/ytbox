from class_model import *
from func import *

from fastapi import APIRouter
router = APIRouter() 



@router.get("/api/system/settings/public")
async def get_public_system_settings(
    db: Session = Depends(get_db)
):
    """获取系统公开设置"""
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)
        db.commit()
        
    return {
        "allowRegistration": settings.allowRegistration,
        "requireEmailVerification": settings.requireEmailVerification,
        "allowLogin": settings.allowLogin,
        "signin_enabled": settings.signin_enabled,
        "signin_reward_type": settings.signin_reward_type,
        "signin_reward_amount": settings.signin_reward_amount,
        "invite_enabled": settings.invite_enabled,
        "card_purchase_url": settings.card_purchase_url,
        "card_purchase_description": settings.card_purchase_description
    }






# 添加新的路由用于管理健康检查设置
@router.get("/api/admin/health-check/settings")
async def get_health_check_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """获取健康检查设置"""
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
        
    return {
        "enable_health_check": settings.enable_health_check,
        "health_check_interval": settings.health_check_interval,
        "health_check_batch_size": settings.health_check_batch_size
    }

# @router.put("/api/admin/health-check/settings")
# async def update_health_check_settings(
#     settings_update: dict,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(check_admin_permission)
# ):
#     """更新健康检查设置"""
#     try:
#         settings = db.query(SystemSettings).first()
#         if not settings:
#             settings = SystemSettings()
#             db.add(settings)
            
#         # 验证和更新间隔时间
#         if "health_check_interval" in settings_update:
#             interval = settings_update["health_check_interval"]
#             if interval < 1:
#                 raise HTTPException(
#                     status_code=400,
#                     detail="Health check interval must be at least 1 minute"
#                 )
#             settings.health_check_interval = interval
            
#         # 验证和更新批量大小
#         if "health_check_batch_size" in settings_update:
#             batch_size = settings_update["health_check_batch_size"]
#             if batch_size < 1:
#                 raise HTTPException(
#                     status_code=400,
#                     detail="Health check batch size must be at least 1"
#                 )
#             settings.health_check_batch_size = batch_size
            
#         # 更新启用状态
#         if "enable_health_check" in settings_update:
#             settings.enable_health_check = settings_update["enable_health_check"]
            
#         db.commit()
#         db.refresh(settings)
        
#         # 如果禁用了健康检查，停止当前的健康检查任务
#         if not settings.enable_health_check and hasattr(app.state, 'health_check_task'):
#             app.state.health_check_task.cancel()
#             try:
#                 await app.state.health_check_task
#             except asyncio.CancelledError:
#                 pass
                
#         # 如果启用了健康检查，重新启动任务
#         elif settings.enable_health_check:
#             if hasattr(app.state, 'health_check_task'):
#                 app.state.health_check_task.cancel()
#                 try:
#                     await app.state.health_check_task
#                 except asyncio.CancelledError:
#                     pass
#             app.state.health_check_task = asyncio.create_task(scheduled_health_check())
            
#         return {
#             "message": "Health check settings updated successfully",
#             "settings": {
#                 "enable_health_check": settings.enable_health_check,
#                 "health_check_interval": settings.health_check_interval,
#                 "health_check_batch_size": settings.health_check_batch_size
#             }
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error updating health check settings: {str(e)}"
#         )


@router.put("/api/admin/invite/settings")
async def update_invite_settings(
    settings: InviteSettings,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """更新邀请奖励设置"""
    system_settings = db.query(SystemSettings).first()
    if not system_settings:
        system_settings = SystemSettings()
        db.add(system_settings)
        
    system_settings.invite_enabled = settings.invite_enabled
    system_settings.inviter_reward_type = settings.inviter_reward_type
    system_settings.inviter_reward_amount = settings.inviter_reward_amount
    system_settings.invitee_reward_type = settings.invitee_reward_type 
    system_settings.invitee_reward_amount = settings.invitee_reward_amount
    
    try:
        db.commit()
        return {
            "message": "Invite settings updated successfully",
            "settings": settings
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/admin/settings/smtp/test")
async def test_smtp_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    settings = db.query(SystemSettings).first()
    if not settings or not settings.smtp:
        raise HTTPException(status_code=400, detail="SMTP settings not configured")

    try:
        print("Testing SMTP connection...")
        smtp_settings = settings.smtp
        print(f"SMTP Settings: {smtp_settings}")

        with smtplib.SMTP(smtp_settings['host'], smtp_settings['port']) as server:
            print("Server connected")
            server.starttls()
            print("STARTTLS completed")
            server.login(smtp_settings['user'], smtp_settings['pass'])
            print("Login successful")
            
            msg = MIMEText('This is a test email from the system.')
            msg['Subject'] = 'SMTP Test'
            msg['From'] = smtp_settings['from']
            msg['To'] = current_user.email
            server.send_message(msg)
            print("Test email sent")
            
            try:
                server.quit()
            except Exception as quit_error:
                print(f"Error during SMTP quit (ignorable): {str(quit_error)}")
                # 忽略关闭连接时的错误
                pass
            
        return {"message": "SMTP test successful"}
    except Exception as e:
        if "Test email sent" in str(e):
            # 如果邮件已发送成功，就返回成功
            return {"message": "SMTP test successful"}
        print(f"SMTP test error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"SMTP test failed: {str(e)}")



@router.get("/api/frontend-settings")
async def get_frontend_settings(db: Session = Depends(get_db)):
    """
    获取前端设置，包括logo、标题、VIP权益说明和使用指南
    这是一个公开的API，不需要认证
    """
    settings = db.query(SystemSettings).first()
    if not settings:
        return {
            "logo": None,
            "title": None,
            "vip_benefits": None,
            "user_guide": None
        }
    
    return {
        "logo": settings.frontend_logo,
        "title": settings.frontend_title,
        "vip_benefits": settings.frontend_vip_benefits,
        "user_guide": settings.frontend_user_guide
    }

# 上传Logo
@router.post("/api/admin/frontend-settings/logo")
async def upload_frontend_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """上传前端Logo"""
    try:
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Only image files are allowed"
            )

        # 创建上传目录
        upload_dir = Path("uploads/frontend")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        file_ext = Path(file.filename).suffix.lower()
        file_name = f"logo_{secrets.token_hex(8)}{file_ext}"
        file_path = upload_dir / file_name

        # 保存文件
        with file_path.open("wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # 更新设置
        settings = db.query(SystemSettings).first()
        if not settings:
            settings = SystemSettings()
            db.add(settings)

        # 删除旧logo文件
        if settings.frontend_logo:
            old_logo_path = Path("uploads") / Path(settings.frontend_logo).relative_to('/')
            if old_logo_path.exists():
                old_logo_path.unlink()

        # 更新logo路径
        settings.frontend_logo = f"/uploads/frontend/{file_name}"
        db.commit()

        return {
            "message": "Logo uploaded successfully",
            "logo_url": settings.frontend_logo
        }

    except Exception as e:
        # 清理上传的文件
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/admin/frontend-settings")
async def update_frontend_settings(
    settings: FrontendSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """更新前端设置"""
    db_settings = db.query(SystemSettings).first()
    if not db_settings:
        db_settings = SystemSettings()
        db.add(db_settings)

    # 只更新提供的字段
    update_data = settings.dict(exclude_unset=True)
    
    if 'title' in update_data:
        db_settings.frontend_title = update_data['title']
    if 'vip_benefits' in update_data:
        db_settings.frontend_vip_benefits = update_data['vip_benefits']
    if 'user_guide' in update_data:
        db_settings.frontend_user_guide = update_data['user_guide']

    try:
        db.commit()
        return {
            "message": "Frontend settings updated successfully",
            "settings": {
                "logo": db_settings.frontend_logo,
                "title": db_settings.frontend_title,
                "vip_benefits": db_settings.frontend_vip_benefits,
                "user_guide": db_settings.frontend_user_guide
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))




@router.post("/api/admin/settings/card-purchase")
async def update_card_purchase_settings(
    url: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)

    settings.card_purchase_url = url
    settings.card_purchase_description = description
    
    try:
        db.commit()
        return {
            "message": "Card purchase settings updated successfully",
            "url": url,
            "description": description
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# 更新签到配置
@router.put("/api/admin/signin/settings")
async def update_signin_settings(
    enabled: bool,
    reward_type: str,
    reward_amount: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    settings = db.query(SigninSettings).first()
    if not settings:
        settings = SigninSettings()
        db.add(settings)
        
    settings.enabled = enabled
    settings.reward_type = reward_type
    settings.reward_amount = reward_amount
    
    try:
        db.commit()
        return {"message": "Signin settings updated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))



#设置白名单
@router.post("/api/admin/email-whitelist/rules", response_model=dict)
async def create_whitelist_rule(
    rule: WhitelistRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """创建新的白名单规则"""
    # 检查模式是否已存在
    existing_rule = db.query(EmailWhitelistRule).filter(
        EmailWhitelistRule.pattern == rule.pattern
    ).first()
    
    if existing_rule:
        raise HTTPException(
            status_code=400,
            detail="此邮箱模式已存在"
        )
    
    db_rule = EmailWhitelistRule(
        pattern=rule.pattern,
        description=rule.description,
        created_by=current_user.id
    )
    
    db.add(db_rule)
    try:
        db.commit()
        db.refresh(db_rule)
        return {
            "message": "白名单规则创建成功",
            "rule": {
                "id": db_rule.id,
                "pattern": db_rule.pattern,
                "description": db_rule.description,
                "is_active": db_rule.is_active,
                "created_at": db_rule.created_at
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/admin/email-whitelist/rules")
async def get_whitelist_rules(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """获取所有白名单规则"""
    rules = db.query(EmailWhitelistRule)\
        .offset(skip)\
        .limit(limit)\
        .all()
        
    return [
        {
            "id": rule.id,
            "pattern": rule.pattern,
            "description": rule.description,
            "is_active": rule.is_active,
            "created_at": rule.created_at,
            "created_by": rule.created_by
        }
        for rule in rules
    ]

@router.put("/api/admin/email-whitelist/rules/{rule_id}")
async def update_whitelist_rule(
    rule_id: int,
    rule: WhitelistRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """更新白名单规则"""
    db_rule = db.query(EmailWhitelistRule).filter(
        EmailWhitelistRule.id == rule_id
    ).first()
    
    if not db_rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    # 如果更新模式，检查是否与其他规则冲突
    if rule.pattern and rule.pattern != db_rule.pattern:
        existing_rule = db.query(EmailWhitelistRule).filter(
            EmailWhitelistRule.pattern == rule.pattern,
            EmailWhitelistRule.id != rule_id
        ).first()
        
        if existing_rule:
            raise HTTPException(
                status_code=400,
                detail="此邮箱模式已存在"
            )
    
    # 更新规则
    for key, value in rule.dict(exclude_unset=True).items():
        setattr(db_rule, key, value)
        
    try:
        db.commit()
        db.refresh(db_rule)
        return {
            "message": "规则更新成功",
            "rule": {
                "id": db_rule.id,
                "pattern": db_rule.pattern,
                "description": db_rule.description,
                "is_active": db_rule.is_active,
                "created_at": db_rule.created_at
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/api/admin/email-whitelist/rules/{rule_id}")
async def delete_whitelist_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """删除白名单规则"""
    db_rule = db.query(EmailWhitelistRule).filter(
        EmailWhitelistRule.id == rule_id
    ).first()
    
    if not db_rule:
        raise HTTPException(status_code=404, detail="规则不存在")
        
    try:
        db.delete(db_rule)
        db.commit()
        return {"message": "规则删除成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))




# 7. 修改系统设置相关API
@router.put("/api/admin/email-whitelist/toggle")
async def toggle_email_whitelist(
    enabled: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """启用/禁用邮箱白名单功能"""
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)
    
    settings.enable_email_whitelist = enabled
    try:
        db.commit()
        return {
            "message": f"邮箱白名单功能已{'启用' if enabled else '禁用'}"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))



@router.put("/api/admin/settings")
async def update_system_settings(
    settings_update: SystemSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)

    update_data = settings_update.dict(exclude_unset=True)
    
    try:
        # 更新系统设置
        for key, value in update_data.items():
            if key == 'smtp' and value is not None:
                smtp_data = {
                    'host': value['host'],
                    'port': value['port'],
                    'user': value['user'],
                    'pass': value['pass_'],
                    'from': value['from_']
                }
                setattr(settings, key, smtp_data)
            else:
                setattr(settings, key, value)

        # 同步更新所有用户的限制
        users = db.query(User).all()
        now = datetime.now(TIMEZONE)  # 使用带时区的当前时间
        
        for user in users:
            # 检查VIP状态
            is_vip = False
            if user.vip_until:
                # 确保 vip_until 有时区信息
                if user.vip_until.tzinfo is None:
                    user_vip_until = user.vip_until.replace(tzinfo=TIMEZONE)
                else:
                    user_vip_until = user.vip_until.astimezone(TIMEZONE)
                is_vip = user_vip_until > now
            
            # 如果是管理员，也视为VIP
            is_vip = is_vip or user.role == UserRole.ADMIN
            
            # 获取对应的限制值
            rpm_limit = settings.vipRpmLimit if is_vip else settings.rpmLimit
            rtm_limit = settings.vipRtmLimit if is_vip else settings.rtmLimit
            daily_limit = settings.vipDailyLimit if is_vip else settings.dailyLimit
            
            # 更新用户限制
            await sync_user_limit(db, user.id, LimitType.RPM, rpm_limit)
            await sync_user_limit(db, user.id, LimitType.RTM, rtm_limit)
            await sync_user_limit(db, user.id, LimitType.DAILY, daily_limit)

        db.commit()
        db.refresh(settings)
        return settings
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/admin/settings", response_model=SystemSettingsResponse)
async def get_system_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    settings = db.query(SystemSettings).first()
    if not settings:
        # 如果没有设置，创建默认设置
        settings = SystemSettings()
        settings.updated_at = datetime.now(TIMEZONE)  # 明确设置时区
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    # 确保 updated_at 有时区信息
    if settings.updated_at and settings.updated_at.tzinfo is None:
        settings.updated_at = settings.updated_at.replace(tzinfo=TIMEZONE)
    
    return settings
