from class_model import *
from func import *

from fastapi import APIRouter
router = APIRouter() 
@router.post("/api/admin/channels/{channel_id}/test")
async def test_channel(
    channel_id: int,
    model_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """测试渠道可用性"""
    print(f"\n========== 开始测试渠道 {channel_id} ==========")
    start_time = time.time()  # 记录开始时间
    
    try:
        # 获取渠道信息
        channel = db.query(Channel).filter(Channel.id == channel_id).first()
        if not channel:
            print(f"错误: 找不到渠道 ID {channel_id}")
            raise HTTPException(status_code=404, detail="Channel not found")
            
        print(f"渠道信息:")
        print(f"- 名称: {channel.channel_name}")
        print(f"- 基础URL: {channel.base_url}")
        print(f"- 组织: {channel.organization}")
        print(f"- 支持的模型: {channel.models}")
        print(f"- 重定向映射: {channel.redirect_mapping}")
        
        # 解析渠道支持的模型列表
        try:
            channel_models = json.loads(channel.models) if channel.models else []
        except json.JSONDecodeError:
            channel_models = []
            
        print(f"渠道支持的模型: {channel_models}")
        
        # 验证请求的模型是否受支持
        if model_name not in channel_models:
            if not channel.redirect_mapping or model_name not in json.loads(channel.redirect_mapping or "{}"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Model {model_name} is not supported by this channel"
                )
        
        # 获取实际使用的模型（考虑重定向）
        actual_model = model_name
        if channel.redirect_mapping:
            try:
                mapping = json.loads(channel.redirect_mapping)
                if model_name in mapping:
                    actual_model = mapping[model_name]
                    print(f"模型重定向: {model_name} -> {actual_model}")
            except json.JSONDecodeError:
                print("解析重定向映射失败")
        
        print(f"\n测试模型: {model_name} (实际使用: {actual_model})")
        
        # 构建请求配置
        request_url = f"{channel.base_url}/v1/chat/completions"
        request_headers = {
            "Authorization": f"Bearer {channel.api_key}",
            "Content-Type": "application/json"
        }
        request_data = {
            "model": actual_model,
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 1
        }
        
        print("\n发送测试请求:")
        print(f"- URL: {request_url}")
        print(f"- 模型: {actual_model}")

        # 发送测试请求
        async with httpx.AsyncClient() as client:
            try:
                print("\n等待上游API响应...")
                response = await client.post(
                    request_url,
                    headers=request_headers,
                    json=request_data,
                    timeout=30.0
                )
                
                end_time = time.time()  # 记录结束时间
                latency = round((end_time - start_time) * 1000)  # 计算延迟（毫秒）
                
                response.raise_for_status()
                print("\n请求成功:")
                print(f"- 状态码: {response.status_code}")
                print(f"- 响应延迟: {latency}ms")
                print(f"- 响应内容: {response.text[:200]}...")
                
                return {
                    "status": "success",
                    "message": "Channel test successful",
                    "model_tested": actual_model,
                    "latency": latency,  # 添加延迟信息
                    "response": response.json()
                }
                
            except httpx.HTTPStatusError as e:
                end_time = time.time()
                latency = round((end_time - start_time) * 1000)
                
                print(f"\n上游API返回错误:")
                print(f"- 状态码: {e.response.status_code}")
                print(f"- 响应内容: {e.response.text}")
                print(f"- 响应延迟: {latency}ms")
                
                error_response = e.response
                error_status = error_response.status_code
                
                try:
                    error_json = error_response.json()
                    if isinstance(error_json, dict) and 'error' in error_json and 'message' in error_json['error']:
                        error_detail = error_json['error']['message']
                    else:
                        error_detail = error_json
                except:
                    error_detail = error_response.text
                    
                raise HTTPException(
                    status_code=error_status,
                    detail=error_detail
                )
                
            except httpx.RequestError as e:
                end_time = time.time()
                latency = round((end_time - start_time) * 1000)
                
                print(f"\n请求错误: {str(e)}")
                print(f"错误类型: {type(e).__name__}")
                print(f"响应延迟: {latency}ms")
                
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Request failed: {str(e)}"
                )
                
    except HTTPException:
        raise
        
    except Exception as e:
        end_time = time.time()
        latency = round((end_time - start_time) * 1000)
        
        print(f"\n发生未预期的错误:")
        print(f"- 错误类型: {type(e).__name__}")
        print(f"- 错误信息: {str(e)}")
        print(f"- 响应延迟: {latency}ms")
        traceback.print_exc()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
        
    finally:
        print("\n========== 测试结束 ==========\n")



@router.delete("/api/admin/channels/{channel_id}")  # 使用DELETE方法
async def delete_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    db_channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not db_channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    try:
        db.delete(db_channel)
        db.commit()
        return {"message": "Channel deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    



@router.put("/api/admin/channels/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    channel_update: ChannelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    db_channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not db_channel:
        raise HTTPException(status_code=404, detail="找不到指定的渠道")

    # 获取需要更新的数据
    update_data = channel_update.dict(exclude_unset=True)
    
    # 单独处理 API 密钥的更新
    if "api_key" in update_data:
        if not update_data["api_key"]:
            del update_data["api_key"]
    
    # 处理模型列表的更新
    if "models" in update_data and update_data["models"] is not None:
        # 为新的模型创建记录
        for model_name in update_data["models"]:
            existing_model = db.query(AIModel).filter(AIModel.name == model_name).first()
            if not existing_model:
                new_model = AIModel(
                    name=model_name,
                    company="OpenAI" if "gpt" in model_name.lower() else "Unknown",
                    tags="chat,ai",
                    description=f"Model {model_name}",
                    group=ModelGroup.FREE,
                    is_active=True,
                    is_deleted=False
                )
                db.add(new_model)
        
        # 更新渠道的模型列表
        update_data["models"] = json.dumps(update_data["models"])
    
    # 处理模型映射的更新
    if "redirect_mapping" in update_data and update_data["redirect_mapping"]:
        # 验证 redirect_mapping 是否为有效的 JSON 字符串
        try:
            json.loads(update_data["redirect_mapping"])
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="模型映射必须是有效的 JSON 字符串"
            )
    
    # 更新渠道属性
    for key, value in update_data.items():
        setattr(db_channel, key, value)

    try:
        db.commit()
        db.refresh(db_channel)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    # 在返回响应前处理模型列表
    response_data = db_channel.__dict__
    response_data['models'] = json.loads(db_channel.models)
    return response_data



@router.post("/api/admin/channels", response_model=ChannelResponse)
async def create_channel(
    channel: ChannelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    if not channel.api_key:
        raise HTTPException(
            status_code=400,
            detail="创建新渠道时必须提供 API 密钥"
        )
    
    # 先处理模型
    if channel.models:
        for model_name in channel.models:
            # 检查模型是否已存在
            existing_model = db.query(AIModel).filter(AIModel.name == model_name).first()
            if not existing_model:
                # 创建新模型
                new_model = AIModel(
                    name=model_name,
                    company="OpenAI" if "gpt" in model_name.lower() else "Unknown",
                    tags="chat,ai",
                    description=f"Model {model_name}",
                    group=ModelGroup.FREE,
                    is_active=True,
                    is_deleted=False
                )
                db.add(new_model)
    
    # 将模型列表转换为JSON字符串
    models_json = json.dumps(channel.models) if channel.models else "[]"
    
    db_channel = Channel(
        channel_name=channel.channel_name,
        channel_model_name=channel.channel_model_name,
        models=models_json,
        base_url=channel.base_url,
        api_key=channel.api_key,
        weight=channel.weight,
        is_active=channel.is_active,
        organization=channel.organization,
        target_model_id=channel.target_model_id,
        redirect_mapping=channel.redirect_mapping
    )
    
    db.add(db_channel)
    try:
        db.commit()
        db.refresh(db_channel)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    # 在返回响应前处理模型列表
    response_data = db_channel.__dict__
    response_data['models'] = json.loads(db_channel.models)
    return response_data




@router.get("/api/admin/channels", response_model=List[ChannelResponse])
async def get_channels(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    # 添加一些调试日志
    channels = db.query(Channel).offset(skip).limit(limit).all()
    print(f"Found {len(channels)} channels in database")
    
    # 处理每个渠道的返回数据
    response_channels = []
    for channel in channels:
        # 将 SQLAlchemy 模型转换为字典
        channel_dict = {
            "id": channel.id,
            "channel_name": channel.channel_name,
            "channel_model_name": channel.channel_model_name,
            "base_url": channel.base_url,
            "weight": channel.weight,
            "is_active": channel.is_active,
            "created_at": channel.created_at,
            "organization": channel.organization,
            "target_model_id": channel.target_model_id,
            "redirect_mapping": channel.redirect_mapping,
            "models": json.loads(channel.models) if channel.models else []
        }
        response_channels.append(channel_dict)
    
    print(f"Processed {len(response_channels)} channels for response")
    return response_channels



@router.post("/api/admin/models/{model_id}/channels")
async def bind_model_channels(
    model_id: int,
    channel_ids: List[int], # 接收一个渠道ID列表
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    try:
        # 验证模型存在
        model = db.query(AIModel).filter(AIModel.id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="模型不存在")
            
        # 验证所有提供的渠道ID都存在
        existing_channels = db.query(Channel).filter(Channel.id.in_(channel_ids)).all()
        if len(existing_channels) != len(channel_ids):
            raise HTTPException(status_code=400, detail="存在无效的渠道ID")

        # 清除现有绑定
        db.query(ModelChannelBinding).filter(
            ModelChannelBinding.model_id == model_id
        ).delete(synchronize_session=False)
        
        # 创建新的绑定
        bindings = []
        for channel_id in channel_ids:
            binding = ModelChannelBinding(
                model_id=model_id,
                channel_id=channel_id,
                created_at=datetime.now(TIMEZONE)
            )
            bindings.append(binding)
        
        db.add_all(bindings)
        db.commit()
        
        return {
            "message": "渠道绑定更新成功",
            "model_id": model_id,
            "channel_ids": channel_ids
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"绑定渠道出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"绑定渠道失败: {str(e)}")




@router.get("/api/admin/models/{model_id}/channels")
async def get_model_channels(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """获取模型绑定的渠道"""
    try:
        bindings = db.query(ModelChannelBinding, Channel)\
            .join(Channel)\
            .filter(ModelChannelBinding.model_id == model_id)\
            .all()
            
        return [
            {
                "channel_id": channel.id,
                "channel_name": channel.channel_name,
                "bound_at": binding.created_at
            }
            for binding, channel in bindings
        ]
        
    except Exception as e:
        print(f"获取模型渠道时出错: {str(e)}")
        raise HTTPException(status_code=500, detail="获取渠道绑定时发生错误")



@router.post("/api/admin/models/{model_id}/channels", response_model=ChannelResponse)
async def add_model_channel(
    model_id: int,
    channel: ChannelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    db_model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    db_channel = Channel(
        model_id=model_id,
        **channel.dict()
    )
    db.add(db_channel)
    try:
        db.commit()
        db.refresh(db_channel)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_channel



@router.patch("/api/admin/channels/{channel_id}/toggle")
async def toggle_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    db_channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not db_channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    db_channel.is_active = not db_channel.is_active
    try:
        db.commit()
        db.refresh(db_channel)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": f"Channel is now {'active' if db_channel.is_active else 'inactive'}"}






@router.get("/api/admin/channels/search")
async def search_channels(
    query: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """
    搜索渠道
    支持模糊搜索渠道名称、模型名称和代理地址
    """
    try:
        base_query = db.query(Channel)
        
        if query:
            search = f"%{query}%"
            base_query = base_query.filter(
                or_(
                    Channel.channel_name.ilike(search),
                    Channel.channel_model_name.ilike(search),
                    Channel.base_url.ilike(search),
                    Channel.models.ilike(search)
                )
            )
        
        channels = base_query.all()
        
        # 处理返回数据
        result = []
        for channel in channels:
            channel_data = {
                "id": channel.id,
                "channel_name": channel.channel_name,
                "channel_model_name": channel.channel_model_name,
                "base_url": channel.base_url,
                "weight": channel.weight,
                "is_active": channel.is_active,
                "organization": channel.organization,
                "models": json.loads(channel.models) if channel.models else [],
                "redirect_mapping": channel.redirect_mapping
            }
            result.append(channel_data)
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.get("/api/admin/channels/stats")
async def get_channels_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    try:
        # 获取所有渠道
        channels = db.query(Channel).all()
        
        # 计算活跃渠道数
        active_channels = len([c for c in channels if c.is_active])
        
        # 计算唯一模型数
        unique_models = set()
        for channel in channels:
            if channel.models:
                try:
                    models = json.loads(channel.models)
                    unique_models.update(models)
                except json.JSONDecodeError:
                    continue
                    
        # 计算权重分布
        total_weight = sum(c.weight for c in channels if c.is_active)
        weight_distribution = [
            {
                "channelId": c.id,
                "percentage": (c.weight / total_weight * 100) if total_weight > 0 else 0
            }
            for c in channels if c.is_active
        ]
        
        return {
            "activeChannels": active_channels,
            "totalChannels": len(channels),
            "uniqueModels": {
                "total": len(unique_models),
                "models": list(unique_models)
            },
            "weightDistribution": weight_distribution
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取渠道统计失败: {str(e)}"
        )






@router.get("/api/admin/channel-models")
async def get_channel_models(db: Session = Depends(get_db)):
    models = db.query(AIModel)\
        .options(
            selectinload(AIModel.channel_bindings),
            selectinload(AIModel.price)
        )\
        .filter(AIModel.is_deleted == False)\
        .order_by(AIModel.sort_order.asc(), AIModel.name.asc())\
        .all()
    
    # 添加调试日志
    for model in models:
        print(f"Model {model.name} price: {model.price.price if model.price else 'No price'}")
    
    return models
