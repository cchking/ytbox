from class_model import *
from func import *

from fastapi import APIRouter
router = APIRouter() 
@router.put("/api/chats/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: int,
    chat: ChatUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id
    ).first()
    
    if not db_chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    for key, value in chat.dict(exclude_unset=True).items():
        setattr(db_chat, key, value)

    db.commit()
    db.refresh(db_chat)
    return db_chat
@router.post("/api/chats/{chat_id}/messages", response_model=MessageResponse)
async def create_message(
    chat_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 检查聊天是否属于当前用户
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id
    ).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # 获取聊天历史
    chat_history = db.query(Message).filter(Message.chat_id == chat_id).all()
    
    # 构建完整的对话历史
    messages = []
    for msg in chat_history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": message.content})

    # 选择一个可用的渠道
    available_channels = db.query(Channel).filter(Channel.is_active == True).all()
    if not available_channels:
        raise HTTPException(status_code=400, detail="No active channels available")
    
    selected_channel = random.choice(available_channels)
    
    try:
        # 调用外部 API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{selected_channel.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {selected_channel.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": selected_channel.channel_model_name,
                    "messages": messages
                }
            )
            api_response = response.json()
            assistant_message = api_response['choices'][0]['message']['content']
    except Exception as e:
        print(f"API 调用错误: {str(e)}")  # 添加错误日志
        raise HTTPException(status_code=500, detail=str(e))

    # 保存用户消息
    user_message = Message(
        chat_id=chat_id,
        role="user",
        content=message.content,
        model_name=None
    )
    db.add(user_message)

    # 保存助手回复
    assistant_msg = Message(
        chat_id=chat_id,
        role="assistant",
        content=assistant_message,
        model_name=selected_channel.channel_model_name
    )
    db.add(assistant_msg)
    
    try:
        db.commit()
        db.refresh(assistant_msg)
    except Exception as e:
        print(f"数据库操作错误: {str(e)}")  # 添加错误日志
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save messages to database")
        
    return assistant_msg








@router.post("/api/chats", response_model=ChatResponse)
async def create_chat(
    chat: ChatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_chat = Chat(
        name=chat.name,
        user_id=current_user.id,
        folder_id=chat.folder_id
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

@router.get("/api/chats", response_model=List[ChatResponse])
async def get_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Chat).filter(Chat.user_id == current_user.id).all()

@router.put("/api/chats/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: int,
    chat: ChatUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id
    ).first()
    
    if not db_chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    for key, value in chat.dict(exclude_unset=True).items():
        setattr(db_chat, key, value)

    db.commit()
    db.refresh(db_chat)
    return db_chat

@router.delete("/api/chats/{chat_id}")
async def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    db.delete(chat)
    db.commit()
    
    return {"message": "Chat deleted"}

@router.post("/api/chats/{chat_id}/messages", response_model=MessageResponse)
async def create_message(
    chat_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 检查聊天是否属于当前用户
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id
    ).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # 获取聊天历史
    chat_history = db.query(Message).filter(Message.chat_id == chat_id).all()
    
    # 构建完整的对话历史
    messages = []
    for msg in chat_history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": message.content})

    # 选择一个可用的渠道
    available_channels = db.query(Channel).filter(Channel.is_active == True).all()
    if not available_channels:
        raise HTTPException(status_code=400, detail="No active channels available")
    
    selected_channel = random.choice(available_channels)
    
    try:
        # 调用外部 API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{selected_channel.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {selected_channel.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": selected_channel.channel_model_name,
                    "messages": messages
                },
                timeout=60.0  # 设置合理的超时时间
            )
            
            # 检查响应状态码
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', {}).get('message', 'Unknown error')
                except:
                    error_message = f"API request failed with status code: {response.status_code}"
                raise HTTPException(status_code=response.status_code, detail=error_message)
                
            api_response = response.json()
            assistant_message = api_response['choices'][0]['message']['content']
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request timeout")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    # 保存用户消息
    user_message = Message(
        chat_id=chat_id,
        role="user",
        content=message.content
    )
    db.add(user_message)

    # 保存助手回复
    assistant_msg = Message(
        chat_id=chat_id,
        role="assistant",
        content=assistant_message,
        model_name=selected_channel.channel_model_name
    )
    db.add(assistant_msg)
    
    try:
        db.commit()
        db.refresh(assistant_msg)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save messages to database")
        
    return assistant_msg

@router.get("/api/chats/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 验证聊天所属权
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # 获取所有消息
    messages = db.query(Message).filter(Message.chat_id == chat_id).all()
    
    # 准备响应数据
    response_messages = []
    for msg in messages:
        # 获取模型信息及其图标
        model_icon = None
        if msg.model_name:
            model = db.query(AIModel).filter(AIModel.name == msg.model_name).first()
            if model:
                model_icon = model.icon

        message_dict = {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at,
            "model_name": msg.model_name,
            "model_icon": model_icon  # 添加模型图标
        }
        
        response_messages.append(message_dict)
    
    return response_messages

@router.post("/api/chats/{chat_id}/messages/stream")
async def create_streaming_message(
    chat_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        print("\n========== 开始处理流式消息请求 ==========")
        start_time = time.time()
        accumulated_content = ""
        assistant_message = None
        channel_id = None
        api_base_url = None
        api_key = None
        model_type = None
        model_id = None
        market_model = None

        # 获取请求数据
        request_data = await request.json()
        content = request_data.get('content', '')
        requested_model = request_data.get('model')
        images = request_data.get('images', [])
        files = request_data.get('files', [])  
        edit_message_id = request_data.get('edit_message_id')
        regenerate_message_id = request_data.get('regenerate_message_id')

        # 处理内容格式化
        if images or files:  
            formatted_content = []
            for image in images:
                image_url = image.get('url')
                if image_url and image_url.startswith('/uploads/'):
                    base_url = str(request.base_url).rstrip('/')
                    full_image_url = f"{base_url}{image_url}"
                else:
                    full_image_url = image_url
                    
                formatted_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": full_image_url,
                        "detail": image.get('detail', 'auto')
                    }
                })
            
            for file in files:
                file_url = file.get('file_url', {}).get('url')
                if file_url and file_url.startswith('/uploads/'):
                    base_url = str(request.base_url).rstrip('/')
                    full_file_url = f"{base_url}{file_url}"
                else:
                    full_file_url = file_url
                    
                formatted_content.append({
                    "type": "file",
                    "file_url": {
                        "url": full_file_url
                    }
                })
            
            if content:
                formatted_content.append({
                    "type": "text",
                    "text": content
                })
            content_for_model = json.dumps(formatted_content)
        else:
            content_for_model = content

        user_id = current_user.id
        chat_metrics = ChatMetrics(model=requested_model)

        try:
            # 基础检查
            if not requested_model:
                raise HTTPException(
                    status_code=400,
                    detail={"error": {"type": "missing_model", "message": "Missing model"}}
                )

            # 解析模型名称格式
            base_model_name = None
            if requested_model.startswith('@'):
                parts = requested_model.split('/')
                if len(parts) == 2:
                    prefix, base_model_name = parts
                    if prefix.startswith('@p'):
                        model_type = 'private'
                        model_id = base_model_name
                    else:
                        model_type = 'market'
                        model_id = prefix[1:]  # 去掉@获取ID
            else:
                model_type = 'system'
                base_model_name = requested_model

            print(f"模型类型: {model_type}")
            print(f"模型ID/名称: {model_id if model_id else base_model_name}")

            # 根据模型类型处理API配置
            if model_type == 'market':
                market_model = db.query(MarketModel).filter(
                    MarketModel.id == int(model_id),
                    MarketModel.status == "approved"
                ).first()
                
                if not market_model:
                    raise HTTPException(
                        status_code=404,
                        detail={"error": {"type": "model_not_found", "message": "Market model not found"}}
                    )

                # 检查是否已拉取
                pull_record = db.query(ModelPull).filter(
                    ModelPull.model_id == int(model_id),
                    ModelPull.user_id == current_user.id
                ).first()

                if not pull_record:
                    raise HTTPException(
                        status_code=403,
                        detail={"error": {"type": "access_denied", "message": "You need to pull this model first"}}
                    )

                if market_model.usage_type == ModelUsageType.COIN:
                    # 检查用户金币是否足够
                    if current_user.coins < market_model.usage_price:
                        raise HTTPException(
                            status_code=402,
                            detail={
                                "error": {
                                    "type": "insufficient_coins",
                                    "message": f"Insufficient coins. Required: {market_model.usage_price}"
                                }
                            }
                        )

                api_base_url = market_model.api_base_url
                api_key = market_model.api_key

                # 提前记录使用情况和扣除金币
                try:
                    # 记录使用情况
                    usage = ModelUsage(
                        model_id=int(model_id),
                        user_id=user_id,
                        usage_price=market_model.usage_price if market_model.usage_type == ModelUsageType.COIN else 0
                    )
                    db.add(usage)
                    market_model.usage_count += 1

                    # 如果是金币模型，扣除金币
                    if market_model.usage_type == ModelUsageType.COIN:
                        current_user.coins -= market_model.usage_price
                        coin_log = CoinLog(
                            user_id=user_id,
                            amount=-market_model.usage_price,
                            type="consume",
                            description=f"使用模型: {market_model.name}"
                        )
                        db.add(coin_log)

                    db.commit()
                    print(f"已记录市场模型使用和扣除金币")

                except Exception as usage_error:
                    db.rollback()
                    print(f"记录使用或扣除金币失败: {str(usage_error)}")
                    print(f"错误详情: {traceback.format_exc()}")
                    raise

            elif model_type == 'private':
                private_model = db.query(PrivateModel).filter(
                    PrivateModel.name == model_id,
                    PrivateModel.creator_id == current_user.id
                ).first()
                
                if not private_model:
                    raise HTTPException(
                        status_code=404,
                        detail={"error": {"type": "model_not_found", "message": "Private model not found"}}
                    )
                    
                api_base_url = private_model.api_base_url
                api_key = private_model.api_key

            else:  # system model
                model = db.query(AIModel).filter(AIModel.name == requested_model).first()
                if not model:
                    raise HTTPException(
                        status_code=404,
                        detail={"error": {"type": "model_not_found", "message": f"Model {requested_model} not found"}}
                    )

                if not check_vip_access(current_user, model):
                    raise HTTPException(
                        status_code=403,
                        detail={"error": {"type": "access_denied", "message": "This model requires VIP access"}}
                    )

                check_result, error_message = await check_user_limits(user_id, model.id, db)
                if not check_result:
                    raise HTTPException(
                        status_code=429,
                        detail={"error": {"type": "rate_limit", "message": error_message}}
                    )

                channel = await select_channel(db, requested_model)
                if not channel:
                    raise HTTPException(
                        status_code=400,
                        detail={"error": {"type": "no_channel", "message": "No available channels"}}
                    )

                channel_id = channel.id
                api_base_url = channel.base_url
                api_key = channel.api_key

            # 检查聊天所属权
            chat = db.query(Chat).filter(
                Chat.id == chat_id,
                Chat.user_id == current_user.id
            ).first()
            if not chat:
                raise HTTPException(
                    status_code=404,
                    detail={"error": {"type": "not_found", "message": "Chat not found"}}
                )

            # 检查系统设置和违禁词
            settings = db.query(SystemSettings).first()
            if not settings:
                raise HTTPException(
                    status_code=500,
                    detail={"error": {"type": "settings_error", "message": "System settings not found"}}
                )

            if settings.enableForbiddenWords:
                has_forbidden, matched_words = check_forbidden_words(content, db)
                if has_forbidden:
                    await log_dangerous_chat_with_context(
                        db=db,
                        user_id=user_id,
                        content=content,
                        matched_words=matched_words,
                        chat_id=chat_id,
                        ip_address=request.client.host,
                        user_agent=request.headers.get("user-agent", ""),
                        request_data={
                            "chat_id": chat_id,
                            "is_ai_response": False,
                            "original_request": content
                        }
                    )
                    
                    raise HTTPException(
                        status_code=400,
                        detail={"error": {"type": "forbidden_words", "message": f"Message contains forbidden words: {matched_words}"}}
                    )

            # 处理重新生成和编辑消息
            original_message = None
            if regenerate_message_id:
                regenerate_message = db.query(Message).filter(
                    Message.id == regenerate_message_id,
                    Message.chat_id == chat_id,
                    Message.role == "assistant"
                ).with_for_update().first()

                if not regenerate_message:
                    raise HTTPException(
                        status_code=404,
                        detail={"error": {"type": "not_found", "message": "Message to regenerate not found"}}
                    )

                regenerate_timestamp = regenerate_message.created_at
                original_message = db.query(Message).filter(
                    Message.chat_id == chat_id,
                    Message.role == "user",
                    Message.created_at < regenerate_timestamp
                ).order_by(Message.created_at.desc()).with_for_update().first()

                if not original_message:
                    raise HTTPException(
                        status_code=404,
                        detail={"error": {"type": "not_found", "message": "Previous user message not found"}}
                    )

                db.query(Message).filter(
                    Message.chat_id == chat_id,
                    Message.created_at >= regenerate_timestamp
                ).delete(synchronize_session='fetch')

                content = original_message.content
                try:
                    parsed_content = json.loads(content)
                    content_for_model = content
                except json.JSONDecodeError:
                    content_for_model = content
                    
                db.commit()

            elif edit_message_id:
                original_message = db.query(Message).filter(
                    Message.id == edit_message_id,
                    Message.chat_id == chat_id,
                    Message.role == "user"
                ).first()

                if not original_message:
                    raise HTTPException(
                        status_code=404,
                        detail={"error": {"type": "not_found", "message": "Original message not found"}}
                    )

                db.query(Message).filter(
                    Message.chat_id == chat_id,
                    Message.created_at > original_message.created_at
                ).delete(synchronize_session=False)

                original_message.content = content_for_model
                original_message.created_at = datetime.now(TIMEZONE)
                db.commit()

            else:
                original_message = Message(
                    chat_id=chat_id,
                    role="user",
                    content=content_for_model,
                    created_at=datetime.now(TIMEZONE)
                )
                db.add(original_message)
                db.commit()
                db.refresh(original_message)

            # 获取聊天历史
            chat_history = db.query(Message).filter(
                Message.chat_id == chat_id,
                Message.created_at <= original_message.created_at
            ).order_by(Message.created_at.asc()).all()

            messages = []
            for msg in chat_history:
                try:
                    parsed_content = json.loads(msg.content)
                    if isinstance(parsed_content, list):
                        messages.append({
                            "role": msg.role,
                            "content": parsed_content
                        })
                    else:
                        messages.append({
                            "role": msg.role,
                            "content": msg.content
                        })
                except json.JSONDecodeError:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })

            try:
                print("计算历史消息的 tokens...")
                chat_metrics.calculate_history_tokens(messages)
                print(f"提示词 tokens 数量: {chat_metrics.prompt_tokens}")
            except Exception as e:
                print(f"计算 tokens 时出错: {str(e)}")
                print(f"错误详情: {traceback.format_exc()}")

            # 创建助手消息
            assistant_message = Message(
                chat_id=chat_id,
                role="assistant",
                content="",
                model_name=requested_model,
                created_at=datetime.now(TIMEZONE)
            )
            db.add(assistant_message)
            db.commit()
            db.refresh(assistant_message)

            # 创建 OpenAI 客户端
            client = OpenAI(
                base_url=f"{api_base_url}/v1",
                api_key=api_key
            )

            print("\n发送请求到模型:")
            print(f"- Base URL: {api_base_url}")
            print(f"- Model: {base_model_name or requested_model}")
            try:
                response = client.chat.completions.create(
                    model=base_model_name or requested_model,
                    messages=messages,
                    stream=True
                )
                async def iterate_openai_response():
                    nonlocal accumulated_content
                    try:
                        for chunk in response:
                            if chunk:
                                chunk_dict = {
                                    "id": chunk.id,
                                    "object": chunk.object,
                                    "created": chunk.created,
                                    "model": chunk.model,
                                    "choices": [{
                                        "index": choice.index,
                                        "delta": {
                                            "content": choice.delta.content,
                                            "role": choice.delta.role
                                        } if choice.delta else {},
                                        "finish_reason": choice.finish_reason
                                    } for choice in chunk.choices],
                                    "usage": chunk.usage.model_dump() if chunk.usage else None
                                }
                                
                                if chunk.choices[0].delta and chunk.choices[0].delta.content:
                                    accumulated_content += chunk.choices[0].delta.content
                                    if not chat_metrics.has_received_first_token:
                                        chat_metrics.record_first_token()

                                yield f"data: {json.dumps(chunk_dict)}\n\n"
                                
                        yield "data: [DONE]\n\n"

                    except Exception as stream_error:
                        print(f"流处理异常: {str(stream_error)}")
                        print(f"错误详情: {traceback.format_exc()}")
                        yield "data: [DONE]\n\n"
                    
                    finally:
                        # 保存回复内容和更新统计
                        if accumulated_content:
                            try:
                                new_db = SessionLocal()
                                try:
                                    # 计算完成后的tokens
                                    chat_metrics.update_completion(accumulated_content)
                                    
                                    # 重新查询消息和设置
                                    current_settings = new_db.query(SystemSettings).first()
                                    assistant_msg = new_db.query(Message).filter(
                                        Message.id == assistant_message.id
                                    ).first()

                                    # 检查是否需要检查AI输出的违禁词
                                    if current_settings and current_settings.enableForbiddenWords:
                                        has_forbidden, matched_words = await check_ai_output_forbidden_words(accumulated_content, new_db)
                                        if has_forbidden:
                                            await log_dangerous_chat_with_context(
                                                db=new_db,
                                                user_id=user_id,
                                                content=accumulated_content,
                                                matched_words=matched_words,
                                                chat_id=chat_id,
                                                ip_address=request.client.host,
                                                user_agent=request.headers.get("user-agent", ""),
                                                request_data={
                                                    "chat_id": chat_id,
                                                    "is_ai_response": True,
                                                    "model": requested_model,
                                                    "original_request": content
                                                }
                                            )

                                    # 更新助手消息内容
                                    if assistant_msg:
                                        assistant_msg.content = accumulated_content
                                        new_db.add(assistant_msg)
                                        new_db.commit()

                                    # 记录API使用日志
                                    metrics = chat_metrics.get_metrics()
                                    await log_ai_request(
                                        db=new_db,
                                        user_id=user_id,
                                        model_name=requested_model,
                                        channel_id=channel_id,
                                        streaming=True,
                                        first_token_latency=metrics["first_token_latency"],
                                        total_latency=metrics["total_latency"],
                                        prompt_tokens=chat_metrics.prompt_tokens,
                                        completion_tokens=chat_metrics.completion_tokens,
                                        request_text=content,
                                        response_text=accumulated_content,
                                        error=None
                                    )
                                    
                                except Exception as db_error:
                                    new_db.rollback()
                                    print(f"数据库操作失败: {str(db_error)}")
                                    print(f"错误详情: {traceback.format_exc()}")
                                finally:
                                    new_db.close()
                                    
                            except Exception as final_error:
                                print(f"最终处理失败: {str(final_error)}")
                                print(f"错误详情: {traceback.format_exc()}")

                return StreamingResponse(
                    iterate_openai_response(),
                    media_type="text/event-stream"
                )

            except Exception as api_error:
                error_message = str(api_error)
                error_response = getattr(api_error, 'response', None)
                error_status = getattr(error_response, 'status_code', 500) if error_response else 500
                error_detail = None

                try:
                    if error_response:
                        error_detail = error_response.json()
                except:
                    error_detail = error_message

                # 记录错误到数据库
                try:
                    metrics = chat_metrics.get_metrics()
                    await log_ai_request(
                        db=db,
                        user_id=user_id,
                        model_name=requested_model,
                        channel_id=channel_id,
                        streaming=True,
                        first_token_latency=metrics["first_token_latency"],
                        total_latency=metrics["total_latency"],
                        prompt_tokens=chat_metrics.prompt_tokens,
                        completion_tokens=0,
                        request_text=content,
                        response_text="[API Error Response]",
                        error=json.dumps({
                            "message": error_message,
                            "status": error_status,
                            "detail": error_detail
                        })
                    )
                except Exception as log_error:
                    print(f"记录API错误日志失败: {str(log_error)}")

                # 更新助手消息内容为错误信息
                if assistant_message:
                    try:
                        error_formatted = f"API Error: {error_message}"
                        if error_detail:
                            error_formatted += f"\n\nDetails: {json.dumps(error_detail, indent=2, ensure_ascii=False)}"
                        
                        assistant_message.content = f"```\n{error_formatted}\n```"
                        db.add(assistant_message)
                        db.commit()
                    except Exception as msg_error:
                        print(f"更新错误消息失败: {str(msg_error)}")
                        db.rollback()

                raise HTTPException(
                    status_code=error_status,
                    detail={
                        "error": {
                            "message": error_message,
                            "details": error_detail
                        }
                    }
                )

        except HTTPException as he:
            raise he
        except Exception as e:
            print(f"请求处理失败: {str(e)}")
            print(f"错误详情: {traceback.format_exc()}")
            
            error_json = {
                "error": {
                    "type": "internal_error",
                    "message": str(e)
                }
            }

            if assistant_message:
                try:
                    error_formatted = f"Internal Error: {str(e)}"
                    assistant_message.content = f"```\n{error_formatted}\n```"
                    db.add(assistant_message)
                    db.commit()
                except Exception as msg_error:
                    print(f"保存错误消息失败: {str(msg_error)}")
                    db.rollback()

            raise HTTPException(status_code=500, detail=error_json)

    except Exception as e:
        print(f"流式消息处理失败: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        raise

@router.post("/api/chats/with-prompt/{prompt_type}/{prompt_id}")
async def create_chat_with_prompt(
    prompt_type: str,
    prompt_id: int,
    chat_data: ChatWithPromptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    根据提示词类型创建聊天
    prompt_type: 'private' 或 'product' 用于区分提示词类型
    """
    if prompt_type not in ['private', 'product']:
        raise HTTPException(
            status_code=400,
            detail="无效的提示词类型，必须是 'private'(私有) 或 'product'(商品)"
        )

    # 获取提示词
    if prompt_type == 'private':
        prompt = db.query(PrivatePrompt).filter(
            PrivatePrompt.id == prompt_id,
            PrivatePrompt.user_id == current_user.id
        ).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="未找到该私有提示词")

    else:  # product type
        prompt = db.query(PromptProduct).filter(
            PromptProduct.id == prompt_id,
            PromptProduct.status == "approved"
        ).first()
        
        if not prompt:
            raise HTTPException(
                status_code=404,
                detail="未找到该商品提示词或提示词未审核通过"
            )

        # 检查商品提示词的访问权限
        has_access = (
            prompt.creator_id == current_user.id or
            current_user.role == UserRole.ADMIN or
            db.query(PromptPurchase).filter(
                PromptPurchase.user_id == current_user.id,
                PromptPurchase.product_id == prompt_id
            ).first() is not None
        )

        if not has_access:
            raise HTTPException(
                status_code=403,
                detail="您需要先购买此提示词才能使用"
            )

    try:
        # 创建新的聊天
        chat = Chat(
            name=chat_data.name,
            user_id=current_user.id,
            folder_id=chat_data.folder_id
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)

        # 添加系统消息
        system_message = Message(
            chat_id=chat.id,
            role="system",
            content=prompt.content
        )
        db.add(system_message)
        db.commit()

        return {
            "message": "Chat created successfully",
            "chat_id": chat.id,
            "chat_name": chat.name,
            "prompt_content": prompt.content
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/chats", response_model=List[ChatResponse])
async def get_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Chat).filter(Chat.user_id == current_user.id).all()


@router.delete("/api/chats/{chat_id}")
async def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 验证聊天是否属于当前用户
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # 删除聊天及其关联的消息
    db.delete(chat)
    db.commit()
    
    return {"message": "Chat deleted"}



# Chat Routes
@router.post("/api/chats", response_model=ChatResponse)
async def create_chat(
    chat: ChatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_chat = Chat(
        name=chat.name,
        user_id=current_user.id,
        folder_id=chat.folder_id
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat







@router.post("/api/folders", response_model=FolderResponse)
async def create_folder(
    folder: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_folder = Folder(
        name=folder.name,
        user_id=current_user.id
    )
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    return db_folder

@router.get("/api/folders", response_model=List[FolderResponse])
async def get_folders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Folder).filter(Folder.user_id == current_user.id).all()

@router.put("/api/folders/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: int,
    folder: FolderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.user_id == current_user.id
    ).first()
    
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    for key, value in folder.dict(exclude_unset=True).items():
        setattr(db_folder, key, value)

    db.commit()
    db.refresh(db_folder)
    return db_folder

@router.delete("/api/folders/{folder_id}")
async def delete_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.user_id == current_user.id
    ).first()
    
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # 将属于这个文件夹的聊天移到未分类
    chats = db.query(Chat).filter(Chat.folder_id == folder_id).all()
    for chat in chats:
        chat.folder_id = None

    db.delete(db_folder)
    db.commit()
    return {"message": "Folder deleted"}

@router.post("/api/admin/users/{user_id}/limits", response_model=LimitResponse)
async def set_user_limit(
    user_id: int,
    limit: LimitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    # 检查用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 更新或创建限制
    db_limit = db.query(UserLimit).filter(
        UserLimit.user_id == user_id,
        UserLimit.limit_type == limit.limit_type
    ).first()
    
    if db_limit:
        db_limit.limit_value = limit.limit_value
        db_limit.updated_at = datetime.now(TIMEZONE)
    else:
        db_limit = UserLimit(
            user_id=user_id,
            limit_type=limit.limit_type,
            limit_value=limit.limit_value
        )
        db.add(db_limit)
    
    try:
        db.commit()
        db.refresh(db_limit)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return db_limit
