from class_model import *
from func import *

from fastapi import APIRouter
router = APIRouter() 


@router.post("/api/cogview/generations", response_model=ImageGenerationResponse)
async def generate_image(
    request: ImageGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """图像生成接口"""
    try:
        # 检查生成限制
        allowed, error_message = await check_generation_limit(current_user, "image", db)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=error_message
            )

        # 随机获取一个 API key
        api_key = get_random_api_key('cogview')
        
        # 初始化智谱AI客户端
        client = ZhipuAI(api_key=api_key)
        
        # 构建请求参数
        generation_params = {
            "model": request.model,
            "prompt": request.prompt,
        }
        
        # 添加可选参数
        if request.size:
            generation_params["size"] = request.size
            
        if request.user_id:
            generation_params["user_id"] = request.user_id
            
        # 调用API生成图像
        response = client.images.generations(**generation_params)
        
        # 记录生成日志
        log = ImageGenerationLog(
            user_id=current_user.id,
            model=request.model,
            prompt=request.prompt,
            size=request.size or ImageSize.SQUARE,
            image_url=response.data[0].url if response.data else None
        )
        db.add(log)
        
        # 如果是消耗金币的模型，扣除金币
        if request.model == "cogview-3-plus":
            coin_cost = 10  # 设置合适的金币消耗
            if current_user.coins < coin_cost:
                raise HTTPException(
                    status_code=402,
                    detail=f"需要{coin_cost}金币，但余额不足"
                )
                
            current_user.coins -= coin_cost
            coin_log = CoinLog(
                user_id=current_user.id,
                amount=-coin_cost,
                type="consume",
                description=f"使用 {request.model} 生成图像"
            )
            db.add(coin_log)
        
        try:
            db.commit()
        except Exception as db_error:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"数据库操作失败: {str(db_error)}"
            )
            
        # 构建响应
        return {
            "created": int(datetime.now().timestamp()),
            "data": [{
                "url": img_data.url
            } for img_data in response.data],
            "content_filter": response.content_filter if hasattr(response, 'content_filter') else None
        }
        
    except Exception as e:
        # 记录错误日志
        error_log = ImageGenerationLog(
            user_id=current_user.id,
            model=request.model,
            prompt=request.prompt,
            size=request.size or ImageSize.SQUARE,
            error=str(e)
        )
        db.add(error_log)
        try:
            db.commit()
        except:
            db.rollback()
            
        raise HTTPException(
            status_code=500,
            detail=f"图像生成失败: {str(e)}"
        )

@router.get("/api/cogview/logs")
async def get_generation_logs(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的图像生成历史"""
    try:
        logs = db.query(ImageGenerationLog)\
            .filter(ImageGenerationLog.user_id == current_user.id)\
            .order_by(ImageGenerationLog.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
            
        return {
            "total": db.query(ImageGenerationLog)\
                .filter(ImageGenerationLog.user_id == current_user.id)\
                .count(),
            "items": logs
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取生成历史失败: {str(e)}"
        )

@router.post("/api/cogvideo/generations", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
    request_fastapi: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """视频生成接口"""
    request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user.id}"
    
    print(f"[{request_id}] ====== 开始处理视频生成请求 ======")
    print(f"[{request_id}] 用户信息: id={current_user.id}, username={current_user.username}")
    print(f"[{request_id}] 请求参数:", request.dict())

    try:
        # 检查生成限制
        print(f"[{request_id}] 检查生成限制...")
        allowed, error_message = await check_generation_limit(current_user, "video", db)
        if not allowed:
            print(f"[{request_id}] ❌ 超出生成限制: {error_message}")
            raise HTTPException(
                status_code=429,
                detail=error_message
            )

        api_key = get_random_api_key('cogvideo')
        print(f"[{request_id}] ✓ 已获取API key")
        
        if not request.prompt and not request.image_url:
            print(f"[{request_id}] ❌ 参数验证失败: prompt和image_url都为空")
            raise HTTPException(
                status_code=400,
                detail="prompt和image_url至少需要提供一个"
            )
            
        if request.image_id:
            print(f"[{request_id}] 获取图片信息: image_id={request.image_id}")
            file_record = db.query(UploadedFile).filter(
                UploadedFile.id == request.image_id,
                UploadedFile.user_id == current_user.id
            ).first()
            if not file_record:
                print(f"[{request_id}] ❌ 找不到图片: image_id={request.image_id}")
                raise HTTPException(
                    status_code=404,
                    detail="找不到指定的图片"
                )
            request.image_url = file_record.url
            print(f"[{request_id}] ✓ 获取到图片URL: {request.image_url}")

        if request.image_url:
            if request.duration and request.duration not in [5, 10]:
                print(f"[{request_id}] ❌ 无效的duration值: {request.duration}")
                raise HTTPException(
                    status_code=400,
                    detail="duration只能是5或10"
                )
            if request.fps and request.fps not in [30, 60]:
                print(f"[{request_id}] ❌ 无效的fps值: {request.fps}")
                raise HTTPException(
                    status_code=400,
                    detail="fps只能是30或60"
                )
        
        client = ZhipuAI(api_key=api_key)
        print(f"[{request_id}] ✓ 智谱AI客户端初始化完成")
        
        generation_params = {
            "model": request.model,
        }
        
        if request.prompt:
            generation_params["prompt"] = request.prompt
        if request.image_url:
            # 处理图片URL
            if request.image_url.startswith('/uploads/'):
                base_url = str(request_fastapi.base_url).rstrip('/')
                full_image_url = f"{base_url}{request.image_url}"
            else:
                full_image_url = request.image_url
            generation_params["image_url"] = full_image_url
            print(f"[{request_id}] 转换后的图片URL: {full_image_url}")
            
        if request.quality and request.model != "cogvideox-flash":
            generation_params["quality"] = request.quality
        if request.with_audio:
            generation_params["with_audio"] = request.with_audio
        if request.size:
            generation_params["size"] = request.size
        if request.duration:
            generation_params["duration"] = request.duration
        if request.fps:
            generation_params["fps"] = request.fps
            
        print(f"[{request_id}] 调用API参数:", generation_params)
            
        try:
            print(f"[{request_id}] 正在调用智谱AI API...")
            response = client.videos.generations(**generation_params)
            print(f"[{request_id}] ✓ API调用成功, 响应:", response)
        except Exception as api_error:
            print(f"[{request_id}] ❌ API调用失败: {str(api_error)}")
            raise
        
        print(f"[{request_id}] 记录生成日志...")
        log = VideoGenerationLog(
            user_id=current_user.id,
            model=request.model,
            prompt=request.prompt,
            image_url=request.image_url,
            image_id=request.image_id,
            size=request.size,
            quality=request.quality,
            with_audio=request.with_audio,
            duration=request.duration,
            fps=request.fps,
            task_id=response.id,
            request_id=response.request_id,
            status=response.task_status
        )
        db.add(log)
        
        if request.model == "cogvideox":
            coin_cost = 20
            print(f"[{request_id}] 检查金币余额: 当前={current_user.coins}, 需要={coin_cost}")
            if current_user.coins < coin_cost:
                print(f"[{request_id}] ❌ 金币不足")
                raise HTTPException(
                    status_code=402,
                    detail=f"需要{coin_cost}金币，但余额不足"
                )
            
            current_user.coins -= coin_cost
            coin_log = CoinLog(
                user_id=current_user.id,
                amount=-coin_cost,
                type="consume",
                description=f"使用 {request.model} 生成视频"
            )
            db.add(coin_log)
            print(f"[{request_id}] ✓ 已扣除金币: {coin_cost}")
        
        try:
            db.commit()
            print(f"[{request_id}] ✓ 数据库提交成功")
        except Exception as db_error:
            db.rollback()
            print(f"[{request_id}] ❌ 数据库操作失败: {str(db_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"数据库操作失败: {str(db_error)}"
            )
        
        print(f"[{request_id}] 启动后台任务检查视频状态...")
        background_tasks.add_task(
            check_video_status,
            response.id,
            db,
            client
        )
        
        print(f"[{request_id}] ====== 请求处理完成 ======")
        return response
        
    except Exception as e:
        print(f"[{request_id}] ❌ 处理失败: {str(e)}")
        error_log = VideoGenerationLog(
            user_id=current_user.id,
            model=request.model,
            prompt=request.prompt,
            image_url=request.image_url,
            image_id=request.image_id,
            size=request.size,
            quality=request.quality,
            with_audio=request.with_audio,
            duration=request.duration,
            fps=request.fps,
            error=str(e),
            status="FAIL"
        )
        db.add(error_log)
        try:
            db.commit()
            print(f"[{request_id}] ✓ 错误日志记录成功")
        except Exception as db_error:
            db.rollback()
            print(f"[{request_id}] ❌ 错误日志记录失败: {str(db_error)}")
            
        raise HTTPException(
            status_code=500,
            detail=f"视频生成失败: {str(e)}"
        )

@router.get("/api/cogvideo/logs")
async def get_video_generation_logs(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的视频生成历史"""
    try:
        logs = db.query(VideoGenerationLog)\
            .filter(VideoGenerationLog.user_id == current_user.id)\
            .order_by(VideoGenerationLog.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
            
        return {
            "total": db.query(VideoGenerationLog)\
                .filter(VideoGenerationLog.user_id == current_user.id)\
                .count(),
            "items": logs
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取生成历史失败: {str(e)}"
        )




# 管理员接口
@router.get("/api/admin/cogview/stats")
async def get_generation_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """获取图像生成统计信息"""
    try:
        # 获取总生成次数
        total_generations = db.query(ImageGenerationLog).count()
        
        # 获取每个模型的使用次数
        model_stats = db.query(
            ImageGenerationLog.model,
            func.count(ImageGenerationLog.id).label("count")
        ).group_by(ImageGenerationLog.model).all()
        
        # 获取今日生成次数
        today = datetime.now(TIMEZONE).date()
        today_generations = db.query(ImageGenerationLog)\
            .filter(func.date(ImageGenerationLog.created_at) == today)\
            .count()
            
        # 获取错误率
        error_count = db.query(ImageGenerationLog)\
            .filter(ImageGenerationLog.error.isnot(None))\
            .count()
            
        return {
            "total_generations": total_generations,
            "today_generations": today_generations,
            "error_rate": error_count / total_generations if total_generations > 0 else 0,
            "model_usage": {
                model: count for model, count in model_stats
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取统计信息失败: {str(e)}"
        )

