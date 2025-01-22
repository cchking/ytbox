from class_model import *
from func import *

from fastapi import APIRouter
router = APIRouter() 


# 修改健康检查趋势API
@router.get("/api/models/health/trend")
async def get_models_health_trend(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取模型健康状态趋势，同时基于间隔时间触发新的检测"""
    try:
        print("\n=== 获取健康检查趋势数据 ===")
        
        # 1. 检查是否启用健康检测
        settings = db.query(SystemSettings).first()
        if not settings or not settings.enable_health_check:
            print("健康检测功能未启用")
            return {
                "enabled": False,
                "message": "Health check is disabled"
            }

        now = datetime.now(TIMEZONE)

        # 2. 检查是否需要进行新的检测
        last_check = db.query(ModelHealthCheck)\
            .order_by(ModelHealthCheck.check_time.desc())\
            .first()

        should_check = not last_check or \
            (now - last_check.check_time.replace(tzinfo=TIMEZONE)).total_seconds() / 60 >= settings.health_check_interval

        if should_check:
            minutes_since_last_check = (now - last_check.check_time.replace(tzinfo=TIMEZONE)).total_seconds() / 60 if last_check else float('inf')
            print(f"距离上次检查已超过{round(minutes_since_last_check, 2)}分钟，开始新的检测...")
            
            # 执行健康检测
            await check_all_models(db, settings.health_check_batch_size)
        else:
            minutes_since_last_check = (now - last_check.check_time.replace(tzinfo=TIMEZONE)).total_seconds() / 60
            print(f"距离上次检查才{round(minutes_since_last_check, 2)}分钟，无需重新检测")

        # 3. 获取并返回检测结果
        available_models = db.query(AIModel).filter(
            AIModel.is_deleted == False,
            AIModel.is_active == True
        ).order_by(
            AIModel.sort_order.asc(),
            AIModel.name.asc()
        ).all()

        results = []
        for model in available_models:
            health_records = db.query(ModelHealthCheck)\
                .filter(ModelHealthCheck.model_id == model.id)\
                .order_by(ModelHealthCheck.check_time.desc())\
                .limit(24)\
                .all()

            if health_records:
                health_records.reverse()
                total_checks = len(health_records)
                success_checks = sum(1 for check in health_records if check.status == "success")
                success_rate = (success_checks / total_checks * 100) if total_checks > 0 else 0
                avg_latency = sum(check.latency for check in health_records if check.latency is not None) / total_checks if total_checks > 0 else 0

                channel = db.query(Channel)\
                    .filter(Channel.id == health_records[-1].channel_id)\
                    .first()

                results.append({
                    "model_name": model.name,
                    "channel_name": channel.channel_name if channel else "Unknown",
                    "current_status": health_records[-1].status,
                    "current_latency": round(health_records[-1].latency, 2),
                    "last_check_time": health_records[-1].check_time.replace(tzinfo=TIMEZONE).isoformat(),
                    "success_rate": round(success_rate, 1),
                    "avg_latency": round(avg_latency, 2),
                    "total_checks": total_checks,
                    "trend": [
                        {
                            "timestamp": check.check_time.replace(tzinfo=TIMEZONE).isoformat(),
                            "status": check.status,
                            "latency": round(check.latency, 2),
                            "error_message": check.error_message
                        }
                        for check in health_records
                    ]
                })

        return {
            "enabled": True,
            "timestamp": now.isoformat(),
            "models": results,
            "last_check": last_check.check_time.replace(tzinfo=TIMEZONE).isoformat() if last_check else None,
            "next_check_in": settings.health_check_interval - minutes_since_last_check if not should_check else 0,
            "just_checked": should_check
        }

    except Exception as e:
        print(f"获取健康趋势时出错: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error getting health trend: {str(e)}"
        )




@router.get("/api/models", response_model=List[ModelResponse])
async def list_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("\n========== 开始获取模型列表 ==========")
    try:
        # 首先检查所有模型的sort_order值
        all_models = db.query(AIModel.id, AIModel.name, AIModel.sort_order).all()
        print("\n数据库中所有模型的sort_order值:")
        for m in all_models:
            print(f"ID: {m.id}, Name: {m.name}, Sort Order: {m.sort_order}")

        channels = db.query(Channel).filter(Channel.is_active == True).all()
        print(f"\n找到活跃渠道数量: {len(channels)}")
        
        all_model_names = set()
        for channel in channels:
            if channel.models:
                try:
                    channel_models = json.loads(channel.models)
                    all_model_names.update(channel_models)
                    if channel.redirect_mapping:
                        mapping = json.loads(channel.redirect_mapping)
                        all_model_names.update(mapping.keys())
                except json.JSONDecodeError:
                    continue

        if all_model_names:
            query = db.query(AIModel).filter(
                AIModel.name.in_(all_model_names),
                AIModel.is_deleted == False,
                AIModel.is_active == True
            ).order_by(
                AIModel.sort_order.asc().nullsfirst(),  # 修改排序方式
                AIModel.name.asc()
            )
            
            # 打印SQL查询语句
            print("\nSQL查询:")
            print(query.statement.compile(compile_kwargs={"literal_binds": True}))
            
            models = query.all()
            
            print("\n查询结果:")
            for model in models:
                print(f"ID: {model.id}, Name: {model.name}, Sort Order: {model.sort_order}")
            
            return models
            
        return []
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        print(traceback.format_exc())
        raise


@router.post("/api/models/{model_id}/use")
async def use_model(
    model_id: int,
    request_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    if not check_vip_access(current_user, model):
        raise HTTPException(
            status_code=403,
            detail="This model requires VIP access"
        )

    # Get available channels
    active_channels = [
        channel for channel in model.channels 
        if channel.is_active
    ]
    
    if not active_channels:
        raise HTTPException(
            status_code=400,
            detail="No active channels available for this model"
        )

    # Choose channel based on weight
    total_weight = sum(channel.weight for channel in active_channels)
    random_value = random.uniform(0, total_weight)
    current_weight = 0
    
    selected_channel = active_channels[0]
    for channel in active_channels:
        current_weight += channel.weight
        if current_weight >= random_value:
            selected_channel = channel
            break

    # TODO: Implement actual API call logic
    return {
        "message": "Model used successfully",
        "channel_id": selected_channel.id,
        "model_name": model.name,
    }



# 获取已删除模型列表的路由
@router.get("/api/admin/models-trash", response_model=List[ModelResponse])
async def get_deleted_models(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    models = db.query(AIModel)\
        .filter(AIModel.is_deleted == True)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return models

# 软删除模型的路由
@router.post("/api/admin/models/{model_id}/delete")
async def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    db_model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")

    db_model.is_deleted = True
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Model soft deleted successfully"}

# 恢复已删除模型的路由（保持不变）
@router.post("/api/admin/models/{model_id}/restore")
async def restore_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    db_model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if not db_model.is_deleted:
        raise HTTPException(status_code=400, detail="Model is not deleted")
    
    db_model.is_deleted = False
    
    try:
        db.commit()
        db.refresh(db_model)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Model restored successfully"}


@router.get("/api/user/available-models")
async def get_user_available_models(
    type: str = Query(..., regex="^(all|pulled|private)$", description="模型类型：all/pulled/private"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户可用的模型（包括拉取的市场模型和私人模型）"""
    try:
        models = []

        # 获取拉取的模型
        if type in ["all", "pulled"]:
            pulled_models = db.query(MarketModel, ModelPull)\
                .join(ModelPull, MarketModel.id == ModelPull.model_id)\
                .filter(
                    ModelPull.user_id == current_user.id,
                    MarketModel.status == "approved"
                ).all()
                
            for model, pull in pulled_models:
                models.append({
                    "id": f"@{model.id}/{model.name}",
                    "name": f"@{model.id}/{model.name}",#model.name
                    "description": model.description,
                    "icon": model.icon,
                    "type": "pulled",
                    "usage_type": model.usage_type,
                    "usage_price": model.usage_price,
                    "pull_info": {
                        "pulled_at": pull.created_at,
                        "pull_type": pull.pull_type,
                    }
                })

        # 获取私人模型
        if type in ["all", "private"]:
            private_models = db.query(PrivateModel)\
                .filter(PrivateModel.creator_id == current_user.id)\
                .all()
                
            for model in private_models:
                models.append({
                    "id": f"@p/{model.name}",
                    "name": model.name,
                    "description": model.description,
                    "icon": model.icon,
                    "type": "private",
                    "usage_type": "free",  # 私人模型默认免费
                    "usage_price": 0,
                    "created_at": model.created_at
                })

        # 按创建/拉取时间倒序排序
        models.sort(key=lambda x: (
            x.get("pull_info", {}).get("pulled_at") or x.get("created_at")
        ), reverse=True)

        return {
            "total": len(models),
            "items": models
        }

    except Exception as e:
        print(f"获取用户模型时出错: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"获取模型列表失败: {str(e)}"
        )



# Add route to update model sort order
@router.put("/api/admin/models/{model_id}/sort-order")
async def update_model_sort_order(
    model_id: int,
    sort_order: int = Query(..., description="New sort order value"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    model.sort_order = sort_order
    try:
        db.commit()
        return {"message": "Sort order updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Batch update sort orders
@router.put("/api/admin/models/sort-orders")
async def update_model_sort_orders(
    sort_orders: Dict[int, int],  # Dict of model_id: sort_order
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    try:
        for model_id, sort_order in sort_orders.items():
            model = db.query(AIModel).filter(AIModel.id == model_id).first()
            if model:
                model.sort_order = sort_order
        
        db.commit()
        return {"message": "Sort orders updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/api/admin/users/{user_id}/model-limits", response_model=ModelLimitResponse)
async def set_user_model_limit(
    user_id: int,
    limit: ModelLimitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    # 检查用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 检查模型是否存在
    model = db.query(AIModel).filter(AIModel.id == limit.model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # 更新或创建模型限制
    db_limit = db.query(UserModelLimit).filter(
        UserModelLimit.user_id == user_id,
        UserModelLimit.model_id == limit.model_id
    ).first()
    
    if db_limit:
        db_limit.daily_limit = limit.daily_limit
        db_limit.updated_at = datetime.now(TIMEZONE)
    else:
        db_limit = UserModelLimit(
            user_id=user_id,
            model_id=limit.model_id,
            daily_limit=limit.daily_limit
        )
        db.add(db_limit)
    
    try:
        db.commit()
        db.refresh(db_limit)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return db_limit


# 设置模型价格
@router.post("/api/admin/models/{model_id}/price")
async def set_model_price(
    model_id: int,
    price: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    # 更新或创建价格记录
    if model.price:
        model.price.price = price
    else:
        model_price = ModelPrice(model_id=model_id, price=price)
        db.add(model_price)
        
    try:
        db.commit()
        return {"message": "Price updated successfully"}
    except Exception as e:
        db.rollback() 
        raise HTTPException(status_code=400, detail=str(e))




@router.post("/api/admin/models", response_model=ModelResponse)
async def create_model(
   name: str = Form(...),
   company: str = Form(...),
   tags: str = Form(...),
   description: str = Form(None),
   group: str = Form(...),
   is_active: bool = Form(True),
   channel_ids: Optional[str] = Form(None),
   icon: UploadFile = File(None),
   db: Session = Depends(get_db),
   current_user: User = Depends(check_admin_permission)
):
   try:
       model_group = ModelGroup(group.lower())
   except ValueError:
       raise HTTPException(
           status_code=400, 
           detail=f"Invalid group value. Must be one of: {[g.value for g in ModelGroup]}"
       )

   icon_path = None
   if icon:
       try:
           if not icon.content_type.startswith('image/'):
               raise HTTPException(status_code=400, detail="Only image files allowed")
           
           file_ext = Path(icon.filename).suffix.lower()
           if file_ext not in ['.jpg', '.jpeg', '.png', '.svg']:
               raise HTTPException(status_code=400, detail="Only JPG/PNG/SVG allowed")
               
           file_name = f"{secrets.token_hex(8)}{file_ext}"
           file_path = UPLOAD_DIR / file_name
           
           UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
           
           with file_path.open("wb") as buffer:
               content = await icon.read()
               buffer.write(content)
               
           icon_path = f"/uploads/model-icons/{file_name}"
           
       except Exception as e:
           raise HTTPException(status_code=400, detail=f"Error processing icon: {str(e)}")

   db_model = AIModel(
       name=name,
       company=company,
       tags=tags,
       description=description,
       group=model_group,
       icon=icon_path,
       is_active=is_active,
       is_deleted=False,
   )
   
   db.add(db_model)
   db.commit()
   db.refresh(db_model)

   # 处理渠道绑定
   if channel_ids:
       try:
           channel_ids = json.loads(channel_ids)
           for channel_id in channel_ids:
               binding = ModelChannelBinding(
                   model_id=db_model.id,
                   channel_id=channel_id
               )
               db.add(binding)
           db.commit()
           db.refresh(db_model)
       except Exception as e:
           db.rollback()
           raise HTTPException(status_code=400, detail=f"Error binding channels: {str(e)}")

   return db_model


@router.post("/api/admin/models/{model_id}/restore")
async def restore_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    db_model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if not db_model.is_deleted:
        raise HTTPException(status_code=400, detail="Model is not deleted")
    
    # 恢复删除的模型
    db_model.is_deleted = False
    
    try:
        db.commit()
        db.refresh(db_model)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Model restored successfully"}


@router.put("/api/admin/models/{model_id}", response_model=ModelResponse)
async def update_model(
   model_id: int,
   name: str = Form(...),
   company: str = Form(...),
   tags: str = Form(...),
   description: Optional[str] = Form(None),
   group: str = Form(...),
   is_active: bool = Form(True),
   sort_order: int = Form(0),
   channel_ids: Optional[str] = Form(None),
   coinPrice: Optional[int] = Form(None),
   icon: Optional[UploadFile] = File(None),
   db: Session = Depends(get_db),
   current_user: User = Depends(check_admin_permission)
):
   db_model = db.query(AIModel).filter(AIModel.id == model_id).first()
   if not db_model:
       raise HTTPException(status_code=404, detail="Model not found")

   try:
       model_group = ModelGroup(group.lower())
   except ValueError:
       raise HTTPException(
           status_code=400,
           detail=f"Invalid group value. Must be one of: {[g.value for g in ModelGroup]}"
       )

   if icon:
       try:
           if not icon.content_type.startswith('image/'):
               raise HTTPException(status_code=400, detail="Only image files allowed")

           file_ext = Path(icon.filename).suffix.lower()
           file_name = f"{secrets.token_hex(8)}{file_ext}"
           file_path = UPLOAD_DIR / file_name

           if db_model.icon:
               old_icon_path = UPLOAD_DIR / Path(db_model.icon).name
               if old_icon_path.exists():
                   old_icon_path.unlink()

           with file_path.open("wb") as buffer:
               content = await icon.read()
               buffer.write(content)

           db_model.icon = f"/uploads/model-icons/{file_name}"
       except Exception as e:
           raise HTTPException(status_code=400, detail=f"Error processing icon: {str(e)}")

   db_model.name = name
   db_model.company = company
   db_model.tags = tags
   db_model.description = description
   db_model.group = model_group
   db_model.is_active = is_active
   db_model.sort_order = sort_order

   # 更新价格
   if model_group == ModelGroup.COIN:
       if coinPrice is None:
           raise HTTPException(status_code=400, detail="Coin model requires price")
           
       model_price = db.query(ModelPrice).filter(
           ModelPrice.model_id == model_id
       ).first()
       
       if model_price:
           model_price.price = coinPrice
       else:
           model_price = ModelPrice(model_id=model_id, price=coinPrice)
           db.add(model_price)
   else:
       db.query(ModelPrice).filter(ModelPrice.model_id == model_id).delete()

   # 更新渠道绑定
   if channel_ids is not None:
       # 删除现有绑定
       db.query(ModelChannelBinding).filter(
           ModelChannelBinding.model_id == model_id
       ).delete()
       
       # 添加新的绑定
       channel_ids = json.loads(channel_ids)
       for channel_id in channel_ids:
           binding = ModelChannelBinding(
               model_id=model_id,
               channel_id=channel_id
           )
           db.add(binding)

   try:
       db.commit()
       db.refresh(db_model)
       return db_model
   except Exception as e:
       db.rollback()
       raise HTTPException(status_code=400, detail=str(e))

# 切换模型状态
@router.patch("/api/admin/models/{model_id}/toggle")
async def toggle_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    db_model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    db_model.is_active = not db_model.is_active
    try:
        db.commit()
        db.refresh(db_model)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": f"Model is now {'active' if db_model.is_active else 'inactive'}"}
