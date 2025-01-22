from class_model import *
from func import *

from fastapi import APIRouter
router = APIRouter() 



@router.get("/api/market/models")
async def list_market_models(
    page: int = Query(1, description="当前页码"),
    search: Optional[str] = None,
    distribution_type: Optional[str] = None,
    usage_type: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取模型列表"""
    try:
        # 设置每页数量
        page_size = 20
        offset = (page - 1) * page_size

        # 构建基础查询
        query = db.query(MarketModel, User.username.label('creator_username'))\
            .join(User, MarketModel.creator_id == User.id)

        # 应用搜索过滤
        if search:
            query = query.filter(
                or_(
                    MarketModel.name.ilike(f"%{search}%"),
                    MarketModel.description.ilike(f"%{search}%")
                )
            )

        # 应用分发方式过滤
        if distribution_type:
            query = query.filter(MarketModel.distribution_type == distribution_type)

        # 应用使用方式过滤
        if usage_type:
            query = query.filter(MarketModel.usage_type == usage_type)

        # 获取总数
        total_count = query.count()

        # 应用排序
        if sort_by:
            order_column = getattr(MarketModel, sort_by)
            if sort_order == "desc":
                order_column = order_column.desc()
            query = query.order_by(order_column)

        # 应用分页
        results = query.offset(offset).limit(page_size).all()

        # 处理响应数据
        models = []
        for model, creator_username in results:
            model_dict = {
                "id": model.id,
                "name": model.name,
                "description": model.description,
                "creator_id": model.creator_id,
                "creator_username": creator_username,
                "distribution_type": model.distribution_type,
                "pull_price": model.pull_price,
                "usage_type": model.usage_type,
                "usage_price": model.usage_price,
                "pull_count": model.pull_count,
                "usage_count": model.usage_count,
                "rating": model.rating,
                "status": model.status,
                "created_at": model.created_at,
                "updated_at": model.updated_at,
                 "icon": model.icon
            }
            models.append(model_dict)

        return {
            "total": total_count,
            "data": models
        }

    except Exception as e:
        print(f"获取模型列表出错: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"获取模型列表失败: {str(e)}"
        )

@router.post("/api/market/models", response_model=MarketModelResponse)
async def create_market_model(
    name: str = Form(...),
    description: str = Form(...),
    distribution_type: str = Form(...),
    usage_type: str = Form(...),
    pull_price: int = Form(0),
    usage_price: int = Form(0),
    api_base_url: Optional[str] = Form(None),  # 新增参数
    api_key: Optional[str] = Form(None),       # 新增参数
    icon: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """发布新模型"""
    # 处理图标上传
    icon_path = None
    if icon:
        try:
            if not icon.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail="Only image files allowed"
                )
            
            file_ext = Path(icon.filename).suffix
            file_name = f"{secrets.token_hex(8)}{file_ext}"
            file_path = UPLOAD_DIR / file_name
            
            with file_path.open("wb") as buffer:
                content = await icon.read()
                buffer.write(content)
                
            icon_path = f"/uploads/model-icons/{file_name}"
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error processing icon: {str(e)}"
            )
    
    # 创建模型记录
    db_model = MarketModel(
        name=name,
        description=description,
        creator_id=current_user.id,
        distribution_type=distribution_type,
        usage_type=usage_type,
        pull_price=pull_price,
        usage_price=usage_price,
        api_base_url=api_base_url,  # 新增字段
        api_key=api_key,            # 新增字段
        icon=icon_path,
        status='pending'
    )
    
    db.add(db_model)
    try:
        db.commit()
        db.refresh(db_model)
        
        # 添加创建者用户名到响应数据
        response_data = db_model.__dict__
        response_data['creator_username'] = current_user.username
        
        # 出于安全考虑，在响应中移除API密钥
        response_data.pop('api_key', None)
        
        return response_data
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/market/models/{model_id}")
async def get_market_model_detail(
    model_id: int,
    page: int = Query(1, ge=1, description="当前页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取市场模型详情和错误日志"""
    try:
        # 获取模型基本信息
        model = db.query(MarketModel).filter(
            MarketModel.id == model_id
        ).first()
        
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        # 获取创建者信息
        creator = db.query(User).filter(User.id == model.creator_id).first()
            
        # 获取用户交互信息
        user_pull = db.query(ModelPull).filter(
            ModelPull.model_id == model_id,
            ModelPull.user_id == current_user.id
        ).first()
        
        # 获取用户评价
        user_review = db.query(ModelReview).filter(
            ModelReview.model_id == model_id,
            ModelReview.user_id == current_user.id
        ).first()

        # 构建错误日志查询
        log_query = db.query(AIRequestLog)\
            .filter(
                AIRequestLog.model_name == f"@{model_id}/{model.name}",
                AIRequestLog.error.isnot(None)  # 只查询有错误的记录
            )

        # 应用日期过滤
        if start_date:
            log_query = log_query.filter(AIRequestLog.created_at >= start_date)
        if end_date:
            log_query = log_query.filter(AIRequestLog.created_at <= end_date)

        # 计算统计数据（包括所有请求，不只是错误请求）
        total_requests = db.query(AIRequestLog)\
            .filter(AIRequestLog.model_name == f"@{model_id}/{model.name}")\
            .count()
            
        avg_latency = db.query(func.avg(AIRequestLog.total_latency))\
            .filter(AIRequestLog.model_name == f"@{model_id}/{model.name}")\
            .scalar() or 0
            
        total_tokens = db.query(func.sum(AIRequestLog.total_tokens))\
            .filter(AIRequestLog.model_name == f"@{model_id}/{model.name}")\
            .scalar() or 0
            
        error_count = log_query.count()  # 错误请求数量

        # 获取分页错误日志数据
        offset = (page - 1) * page_size
        error_logs = log_query.order_by(AIRequestLog.created_at.desc())\
            .offset(offset)\
            .limit(page_size)\
            .all()

        # 处理错误日志数据
        log_items = []
        for log in error_logs:
            log_dict = {
                "id": log.id,
                "user_id": log.user_id,
                "streaming": log.streaming,
                "first_token_latency": log.first_token_latency,
                "total_latency": log.total_latency,
                "prompt_tokens": log.prompt_tokens,
                "completion_tokens": log.completion_tokens,
                "total_tokens": log.total_tokens,
                "response_text": log.response_text,
                "error": log.error,
                "created_at": log.created_at
            }
            log_items.append(log_dict)

        # 构建完整的响应数据
        response_data = {
            "id": model.id,
            "name": model.name,
            "description": model.description,
            "creator": {
                "id": creator.id,
                "username": creator.username
            },
            "distribution_type": model.distribution_type,
            "pull_price": model.pull_price,
            "usage_type": model.usage_type,
            "usage_price": model.usage_price,
            "icon": model.icon,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
            "stats": {
                "rating": model.rating,
                "pull_count": model.pull_count,
                "usage_count": model.usage_count,
                "monthly_usage": db.query(ModelUsage).filter(
                    ModelUsage.model_id == model_id,
                    ModelUsage.created_at >= (datetime.now(TIMEZONE) - timedelta(days=30))
                ).count()
            },
            "user_interaction": {
                "has_pulled": user_pull is not None,
                "user_review": {
                    "id": user_review.id,
                    "rating": user_review.rating,
                    "comment": user_review.comment,
                    "created_at": user_review.created_at
                } if user_review else None
            },
            "logs": {
                "total": error_count,  # 总数改为错误日志数量
                "page": page,
                "page_size": page_size,
                "has_more": error_count > (offset + page_size),
                "stats": {
                    "total_requests": total_requests,
                    "avg_latency": float(avg_latency),
                    "total_tokens": int(total_tokens),
                    "error_count": error_count
                },
                "items": log_items  # 只包含错误日志
            }
        }

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting model detail: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取模型详情失败: {str(e)}"
        )

@router.put("/api/market/models/{model_id}")
async def update_market_model(
    model_id: int,
    name: str = Form(...),
    description: str = Form(...),
    distribution_type: str = Form(...),
    usage_type: str = Form(...),
    pull_price: int = Form(0),
    usage_price: int = Form(0),
    api_base_url: str = Form(...),
    api_key: Optional[str] = Form(None),
    icon: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 获取模型
    db_model = db.query(MarketModel).filter(
        MarketModel.id == model_id,
        MarketModel.creator_id == current_user.id  # 确保是创建者
    ).first()
    
    if not db_model:
        raise HTTPException(
            status_code=404, 
            detail="Model not found or you don't have permission"
        )

    # 处理图标
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

    # 更新其他字段
    db_model.name = name
    db_model.description = description
    db_model.distribution_type = distribution_type
    db_model.pull_price = pull_price
    db_model.usage_type = usage_type
    db_model.usage_price = usage_price
    db_model.api_base_url = api_base_url
    if api_key:
        db_model.api_key = api_key

    # 设置状态为待审核
    db_model.status = "pending"
    
    try:
        db.commit()
        db.refresh(db_model)
        return db_model
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/market/models/{model_id}/list")
async def list_market_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上架市场模型"""
    # 获取模型
    model = db.query(MarketModel).filter(MarketModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    # 检查权限：必须是管理员或模型创建者 
    if current_user.role != UserRole.ADMIN and model.creator_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only list your own models"
        )
    
    # 检查当前状态
    if model.status != "delisted":
        raise HTTPException(status_code=400, detail="Model is not delisted")
    
    # 更新状态为待审核 
    model.status = "pending"  # 修改这里,重新上架时设为待审核状态
    model.updated_at = datetime.now(TIMEZONE)

    try:
        db.commit()
        return {"message": "Model listed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/market/models/{model_id}/delist")
async def delist_market_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """下架市场模型 - 允许管理员或创建者操作"""
    # 获取模型
    model = db.query(MarketModel).filter(MarketModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # 权限检查：必须是管理员或模型创建者
    if current_user.role != UserRole.ADMIN and model.creator_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delist your own models"
        )
    
    # 检查当前状态
    if model.status == "delisted":
        raise HTTPException(status_code=400, detail="Model is already delisted")
    
    # 更新状态为下架
    model.status = "delisted"
    model.updated_at = datetime.now(TIMEZONE)
    
    try:
        db.commit()
        return {
            "message": "Model delisted successfully",
            "model": {
                "id": model.id,
                "name": model.name,
                "status": model.status,
                "updated_at": model.updated_at
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/market/models/{model_id}/pull")
async def pull_model(
    model_id: int,
    pull_data: ModelPullRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """拉取模型"""
    model = db.query(MarketModel).filter(MarketModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    # 检查模型状态 - 只允许已审核通过的模型被拉取
    if model.status != "approved":
        raise HTTPException(
            status_code=403,
            detail="This model is not available for pulling. Only approved models can be pulled."
        )
        
    # 检查是否已拉取
    existing_pull = db.query(ModelPull).filter(
        ModelPull.model_id == model_id,
        ModelPull.user_id == current_user.id
    ).first()
    
    if existing_pull:
        raise HTTPException(status_code=400, detail="Already pulled this model")
    
    # 处理不同的拉取方式
    if model.distribution_type == ModelDistributionType.COIN_PULL:
        # 检查金币余额
        if current_user.coins < model.pull_price:
            raise HTTPException(
                status_code=402,
                detail=f"Insufficient coins. Required: {model.pull_price}"
            )
            
        # 扣除金币
        current_user.coins -= model.pull_price
        
        # 记录金币变动
        coin_log = CoinLog(
            user_id=current_user.id,
            amount=-model.pull_price,
            type="consume",
            description=f"Pull model: {model.name}"
        )
        db.add(coin_log)
        
        # 给创建者加金币
        creator = db.query(User).filter(User.id == model.creator_id).first()
        if creator:
            creator.coins = (creator.coins or 0) + model.pull_price
            creator_coin_log = CoinLog(
                user_id=creator.id,
                amount=model.pull_price,
                type="income",
                description=f"Model pull income: {model.name}"
            )
            db.add(creator_coin_log)
            
    elif model.distribution_type == ModelDistributionType.KEY_PULL:
        if not pull_data.key_code:
            raise HTTPException(
                status_code=400,
                detail="Key code is required"
            )
            
        # 验证兑换码
        key = db.query(ModelKey).filter(
            ModelKey.model_id == model_id,
            ModelKey.key_code == pull_data.key_code,
            ModelKey.used_by.is_(None)
        ).first()
        
        if not key:
            raise HTTPException(
                status_code=400,
                detail="Invalid or used key code"
            )
            
        # 标记兑换码为已使用
        key.used_by = current_user.id
        key.used_at = datetime.now(TIMEZONE)
    
    # 创建拉取记录
    pull = ModelPull(
        model_id=model_id,
        user_id=current_user.id,
        pull_type=model.distribution_type,
        pull_price=model.pull_price if model.distribution_type == ModelDistributionType.COIN_PULL else 0,
        key_code=pull_data.key_code if model.distribution_type == ModelDistributionType.KEY_PULL else None
    )
    
    db.add(pull)
    
    # 更新拉取计数
    model.pull_count += 1
    
    try:
        db.commit()
        return {"message": "Model pulled successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/market/models/{model_id}/use")
async def use_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """使用模型"""
    # 检查是否已拉取
    pull_record = db.query(ModelPull).filter(
        ModelPull.model_id == model_id,
        ModelPull.user_id == current_user.id
    ).first()
    
    if not pull_record:
        raise HTTPException(
            status_code=403,
            detail="You need to pull this model first"
        )
    
    model = db.query(MarketModel).filter(MarketModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    # 处理使用费用
    if model.usage_type == ModelUsageType.COIN:
        # 检查金币余额
        if current_user.coins < model.usage_price:
            raise HTTPException(
                status_code=402,
                detail=f"Insufficient coins. Required: {model.usage_price}"
            )
            
        # 扣除金币
        current_user.coins -= model.usage_price
        
        # 记录金币变动
        coin_log = CoinLog(
            user_id=current_user.id,
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
    
    # 记录使用
    usage = ModelUsage(
        model_id=model_id,
        user_id=current_user.id,
        usage_price=model.usage_price if model.usage_type == ModelUsageType.COIN else 0
    )
    
    db.add(usage)
    
    # 更新使用计数
    model.usage_count += 1
    
    try:
        db.commit()
        return {"message": "Model used successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/market/models/{model_id}/review")
async def review_model(
    model_id: int,
    review: ModelReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """评价模型"""
    # 检查是否已拉取模型
    pull_record = db.query(ModelPull).filter(
        ModelPull.model_id == model_id,
        ModelPull.user_id == current_user.id
    ).first()
    
    if not pull_record:
        raise HTTPException(
            status_code=403,
            detail="You need to pull this model before reviewing"
        )
    
    # 检查是否已评价
    existing_review = db.query(ModelReview).filter(
        ModelReview.model_id == model_id,
        ModelReview.user_id == current_user.id
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="You have already reviewed this model"
        )
    
    # 创建评价
    db_review = ModelReview(
        model_id=model_id,
        user_id=current_user.id,
        rating=review.rating,
        comment=review.comment
    )
    
    db.add(db_review)
    
    # 更新模型平均评分
    model = db.query(MarketModel).filter(MarketModel.id == model_id).first()
    reviews = db.query(ModelReview).filter(ModelReview.model_id == model_id).all()
    model.rating = sum(r.rating for r in reviews) / len(reviews)
    
    try:
        db.commit()
        return {"message": "Review submitted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/market/models/{model_id}/reviews")
async def get_model_reviews(
    model_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    rating: Optional[int] = Query(None, ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 检查模型是否存在
        model = db.query(MarketModel).filter(MarketModel.id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        # 构建基础查询
        query = db.query(
            ModelReview,
            User.username
        ).join(User, ModelReview.user_id == User.id)\
        .filter(ModelReview.model_id == model_id)

        # 评分过滤
        if rating:
            query = query.filter(ModelReview.rating == rating)

        # 计算总数和评分分布
        total_reviews = query.count()
        rating_distribution = {}
        for r in range(1, 6):
            count = db.query(ModelReview).filter(
                ModelReview.model_id == model_id,
                ModelReview.rating == r
            ).count()
            rating_distribution[r] = count

        # 应用分页
        offset = (page - 1) * page_size
        reviews = query.order_by(ModelReview.created_at.desc())\
            .offset(offset)\
            .limit(page_size)\
            .all()

        # 构建响应数据
        review_items = []
        for review, username in reviews:
            # 获取所有评论，不过滤 parent_id
            comments = db.query(
                ModelReviewComment.id,
                ModelReviewComment.user_id,
                ModelReviewComment.content,
                ModelReviewComment.created_at,
                ModelReviewComment.parent_id,
                User.username.label('commenter_username')
            ).join(
                User,
                ModelReviewComment.user_id == User.id
            ).filter(
                ModelReviewComment.review_id == review.id
            ).order_by(
                ModelReviewComment.created_at.asc()
            ).all()

            # 组织评论成树形结构
            comment_tree = organize_comments(comments)

            review_items.append({
                "id": review.id,
                "user_id": review.user_id,
                "username": username,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at,
                "comments": comment_tree
            })

        return {
            "total": total_reviews,
            "items": review_items,
            "average_rating": model.rating if model.rating is not None else 0.0,
            "rating_distribution": rating_distribution
        }

    except Exception as e:
        print(f"Error getting reviews: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"获取评论列表失败: {str(e)}"
        )

@router.get("/api/market/user/models")
async def get_user_models(
    type: str = Query(..., regex="^(created|pulled)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的模型（创建的或拉取的）"""
    if type == "created":
        query = db.query(MarketModel).filter(
            MarketModel.creator_id == current_user.id
        )
    else:  # pulled
        query = db.query(MarketModel)\
            .join(ModelPull, MarketModel.id == ModelPull.model_id)\
            .filter(ModelPull.user_id == current_user.id)
    
    models = query.all()
    
    return models


@router.get("/api/market/models/{model_id}/keys")
async def get_model_keys(
    model_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取模型的兑换码列表"""
    # 计算偏移量
    skip = (page - 1) * page_size
    
    # 查询指定模型的兑换码
    keys = db.query(ModelKey).filter(
        ModelKey.model_id == model_id
    ).offset(skip).limit(page_size).all()
    
    # 获取总数
    total = db.query(ModelKey).filter(
        ModelKey.model_id == model_id
    ).count()
    
    # 返回标准化的分页响应
    return {
        "items": keys,
        "total": total
    }

@router.post("/api/market/models/{model_id}/keys/generate")
async def generate_model_keys(
    model_id: int,
    request: KeysGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """为模型生成兑换码"""
    # 检查模型是否存在并且属于当前用户
    model = db.query(MarketModel).filter(
        MarketModel.id == model_id,
        MarketModel.creator_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=404, 
            detail="Model not found or you don't have permission"
        )
    
    # 生成指定数量的兑换码
    new_keys = []
    for _ in range(request.count):
        key_code = f"MDL-{secrets.token_hex(8).upper()}"
        new_key = ModelKey(
            model_id=model_id,
            key_code=key_code,
            created_at=datetime.now(TIMEZONE)
        )
        new_keys.append(new_key)
    
    try:
        db.add_all(new_keys)
        db.commit()
        
        # 返回生成的兑换码列表
        return {
            "message": f"Successfully generated {request.count} keys",
            "keys": [{"key_code": key.key_code} for key in new_keys]
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/market/reviews/{review_id}/comments")
async def create_review_comment(
    review_id: int,
    comment: ReviewCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建评论回复"""
    try:
        # 检查评论是否存在
        review = db.query(ModelReview).filter(ModelReview.id == review_id).first()
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # 如果有 parent_id，验证父评论是否存在且属于同一个评论
        if comment.parent_id:
            parent_comment = db.query(ModelReviewComment).filter(
                ModelReviewComment.id == comment.parent_id,
                ModelReviewComment.review_id == review_id
            ).first()
            
            if not parent_comment:
                raise HTTPException(
                    status_code=404, 
                    detail="Parent comment not found or does not belong to this review"
                )

        # 创建新评论
        new_comment = ModelReviewComment(
            user_id=current_user.id,
            review_id=review_id,
            content=comment.content,  # 使用 content
            parent_id=comment.parent_id
        )
        
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        return {
            "id": new_comment.id,
            "user_id": new_comment.user_id,
            "username": current_user.username,
            "content": new_comment.content,
            "created_at": new_comment.created_at,
            "parent_id": new_comment.parent_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error creating comment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/market/reviews/{review_id}/comments")
async def get_review_comments(
    review_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """获取评论的回复列表"""
    # 检查评论是否存在
    review = db.query(ModelReview).filter(ModelReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # 获取评论列表
    comments = db.query(ModelReviewComment, User.username)\
        .join(User, ModelReviewComment.user_id == User.id)\
        .filter(ModelReviewComment.review_id == review_id)\
        .order_by(ModelReviewComment.created_at.asc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return {
        "items": [
            {
                "id": comment.id,
                "content": comment.content,
                "created_at": comment.created_at,
                "user_id": comment.user_id,
                "username": username,
                "parent_id": comment.parent_id
            }
            for comment, username in comments
        ],
        "total": db.query(ModelReviewComment)\
            .filter(ModelReviewComment.review_id == review_id)\
            .count()
    }

# 删除评论的路由
@router.delete("/api/market/comments/{comment_id}")
async def delete_review_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除评论"""
    comment = db.query(ModelReviewComment).filter(
        ModelReviewComment.id == comment_id,
        ModelReviewComment.user_id == current_user.id  # 只能删除自己的评论
    ).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or no permission")
    
    try:
        db.delete(comment)
        db.commit()
        return {"message": "Comment deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# 管理员接口
@router.get("/api/admin/market/stats")
async def get_market_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """获取市场统计数据"""
    # 计算总模型数
    total_models = db.query(MarketModel).count()
    
    # 计算今日新增模型数
    today = datetime.now(TIMEZONE).date()
    new_models_today = db.query(MarketModel)\
        .filter(func.date(MarketModel.created_at) == today)\
        .count()
    
    # 计算总拉取次数
    total_pulls = db.query(ModelPull).count()
    
    # 计算总使用次数
    total_usages = db.query(ModelUsage).count()
    
    # 计算总交易金额
    total_coin_pulls = db.query(func.sum(ModelPull.pull_price))\
        .filter(ModelPull.pull_type == ModelDistributionType.COIN_PULL)\
        .scalar() or 0
        
    total_coin_usages = db.query(func.sum(ModelUsage.usage_price))\
        .filter(ModelUsage.usage_price > 0)\
        .scalar() or 0
    
    return {
        "total_models": total_models,
        "new_models_today": new_models_today,
        "total_pulls": total_pulls,
        "total_usages": total_usages,
        "total_coin_transactions": total_coin_pulls + total_coin_usages
    }

@router.post("/api/admin/market/models/{model_id}/audit")
async def audit_market_model(
    model_id: int,
    action: str = Query(..., regex="^(approve|reject)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """审核模型"""
    model = db.query(MarketModel).filter(MarketModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    if model.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Model is already {model.status}"
        )
    
    model.status = "approved" if action == "approve" else "rejected"
    
    try:
        db.commit()
        return {"message": f"Model {action}d successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/admin/market/models/{model_id}/test")
async def test_market_model(
   model_id: int,
   data: dict = Body(..., description="测试内容"),
   db: Session = Depends(get_db),
   current_user: User = Depends(check_admin_permission)
):
   """管理员测试市场模型的路由"""
   content = data.get("content")
   if not content:
       raise HTTPException(status_code=400, detail="Missing content field")
       
   print(f"\n========== 开始测试市场模型 {model_id} ==========")
   start_time = time.time()
   
   try:
       # 获取模型信息
       model = db.query(MarketModel).filter(MarketModel.id == model_id).first()
       if not model:
           raise HTTPException(status_code=404, detail="模型不存在")

       if not model.api_base_url or not model.api_key:
           raise HTTPException(status_code=400, detail="模型未配置 API 信息")

       print(f"模型信息:")
       print(f"- 名称: {model.name}")
       print(f"- API地址: {model.api_base_url}")
       
       # 构建请求配置
       request_url = f"{model.api_base_url}/v1/chat/completions"
       request_headers = {
           "Authorization": f"Bearer {model.api_key}",
           "Content-Type": "application/json"
       }
       
       # 构建测试消息
       messages = [
           {"role": "user", "content": content}
       ]
       
       request_data = {
           "model": model.name,
           "messages": messages
       }
       
       print("\n发送测试请求:")
       print(f"- URL: {request_url}")
       print(f"- 内容: {content}")

       # 发送测试请求
       async with httpx.AsyncClient() as client:
           try:
               print("\n等待AI响应...")
               response = await client.post(
                   request_url,
                   headers=request_headers,
                   json=request_data,
                   timeout=30.0
               )
               
               end_time = time.time()
               latency = round((end_time - start_time) * 1000)  # 计算延迟（毫秒）
               
               response.raise_for_status()  # 检查响应状态
               response_data = response.json()
               
               assistant_message = ""
               if response_data.get("choices"):
                   assistant_message = response_data["choices"][0].get("message", {}).get("content", "")
               
               print("\n请求成功:")
               print(f"- 状态码: {response.status_code}")
               print(f"- 响应延迟: {latency}ms")
               print(f"- 响应内容: {assistant_message[:200]}...")
               
               return {
                   "status": "success",
                   "model": model.name,
                   "latency": latency,
                   "request": content,
                   "response": assistant_message,
                   "raw_response": response_data,
               }
               
           except httpx.HTTPStatusError as e:
               end_time = time.time()
               latency = round((end_time - start_time) * 1000)
               
               print(f"\nAPI返回错误:")
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
                   detail={
                       "message": str(error_detail),
                       "latency": latency
                   }
               )
               
           except httpx.RequestError as e:
               end_time = time.time()
               latency = round((end_time - start_time) * 1000)
               
               print(f"\n请求错误: {str(e)}")
               print(f"错误类型: {type(e).__name__}")
               print(f"响应延迟: {latency}ms")
               
               raise HTTPException(
                   status_code=status.HTTP_502_BAD_GATEWAY,
                   detail={
                       "message": f"请求失败: {str(e)}",
                       "latency": latency
                   }
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
           detail={
               "message": str(e),
               "latency": latency
           }
       )
       
   finally:
       print("\n========== 测试结束 ==========\n")

# 创建新评论
@router.post("/api/market/models/{model_id}/reviews")
async def create_model_review(
    model_id: int,
    review: ModelReviewCreate,  # 使用定义的模型
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建模型评价"""
    try:
        # 检查模型是否存在
        model = db.query(MarketModel).filter(MarketModel.id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        # 检查用户是否已经评价过
        existing_review = db.query(ModelReview).filter(
            ModelReview.model_id == model_id,
            ModelReview.user_id == current_user.id
        ).first()
        
        if existing_review:
            raise HTTPException(
                status_code=400,
                detail="You have already reviewed this model"
            )

        # 检查用户是否有权评价（是否已拉取模型）
        pull_record = db.query(ModelPull).filter(
            ModelPull.model_id == model_id,
            ModelPull.user_id == current_user.id
        ).first()

        if not pull_record:
            raise HTTPException(
                status_code=403,
                detail="You need to pull the model before reviewing"
            )

        # 创建新评价
        new_review = ModelReview(
            model_id=model_id,
            user_id=current_user.id,
            rating=review.rating,
            comment=review.comment
        )
        db.add(new_review)

        # 更新模型平均评分
        reviews = db.query(ModelReview).filter(ModelReview.model_id == model_id).all()
        model.rating = sum(r.rating for r in reviews + [new_review]) / (len(reviews) + 1)

        db.commit()
        db.refresh(new_review)

        return {
            "message": "Review submitted successfully",
            "review": {
                "id": new_review.id,
                "rating": new_review.rating,
                "comment": new_review.comment,
                "created_at": new_review.created_at
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error creating review: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create review: {str(e)}"
        )

# 获取模型的评论列表
@router.post("/api/market/reviews/{review_id}/comments", response_model=dict)
async def create_review_comment(
    review_id: int,
    comment: ReviewCommentCreate,
    parent_id: Optional[int] = None,  # 添加 parent_id 参数
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建评论回复"""
    try:
        # 检查评论是否存在
        review = db.query(ModelReview).filter(ModelReview.id == review_id).first()
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # 如果有 parent_id，验证父评论是否存在且属于同一个评论
        if parent_id:
            parent_comment = db.query(ModelReviewComment).filter(
                ModelReviewComment.id == parent_id,
                ModelReviewComment.review_id == review_id
            ).first()
            
            if not parent_comment:
                raise HTTPException(
                    status_code=404, 
                    detail="Parent comment not found or does not belong to this review"
                )

        # 创建新评论
        new_comment = ModelReviewComment(
            user_id=current_user.id,
            review_id=review_id,
            content=comment.content,
            parent_id=parent_id  # 使用传入的 parent_id
        )
        
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        return {
            "id": new_comment.id,
            "user_id": new_comment.user_id,
            "username": current_user.username,
            "content": new_comment.content,
            "created_at": new_comment.created_at,
            "parent_id": new_comment.parent_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def organize_comments(comments):
    """将评论组织成树形结构"""
    # 创建评论字典，用 ID 作为键
    comment_dict = {}
    for comment in comments:
        comment_dict[comment.id] = {
            "id": comment.id,
            "user_id": comment.user_id,
            "username": comment.commenter_username,
            "content": comment.content,
            "created_at": comment.created_at,
            "parent_id": comment.parent_id,
            "children": []
        }

    # 构建树形结构
    root_comments = []
    for comment_id, comment in comment_dict.items():
        # 如果评论有父评论
        if comment['parent_id'] is not None:
            # 找到父评论并添加到其子评论列表中
            parent = comment_dict.get(comment['parent_id'])
            if parent:
                parent['children'].append(comment)
        else:
            # 没有父评论，则为顶层评论
            root_comments.append(comment)

    return root_comments

# 删除评论路由
@router.delete("/api/market/comments/{comment_id}")
async def delete_review_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除评论"""
    try:
        # 查找评论
        comment = db.query(ModelReviewComment).filter(
            ModelReviewComment.id == comment_id
        ).first()
        
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # 检查权限（只能删除自己的评论或管理员可以删除所有评论）
        if comment.user_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="No permission to delete this comment")
        
        # 删除评论及其所有子评论
        def delete_comment_tree(comment_id):
            # 递归删除子评论
            child_comments = db.query(ModelReviewComment).filter(
                ModelReviewComment.parent_id == comment_id
            ).all()
            
            for child in child_comments:
                delete_comment_tree(child.id)
            
            # 删除当前评论
            db.query(ModelReviewComment).filter(
                ModelReviewComment.id == comment_id
            ).delete()
        
        delete_comment_tree(comment_id)
        
        db.commit()
        return {"message": "Comment deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting comment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 删除评论（用户删除自己的评论或管理员删除任意评论）
@router.delete("/api/market/models/{model_id}/reviews/{review_id}")
async def delete_model_review(
    model_id: int,
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除模型评论"""
    try:
        # 获取评论
        review = db.query(ModelReview).filter(
            ModelReview.id == review_id,
            ModelReview.model_id == model_id
        ).first()

        if not review:
            raise HTTPException(status_code=404, detail="评论不存在")

        # 检查权限
        if review.user_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="没有权限删除此评论"
            )

        # 删除评论
        db.delete(review)

        # 更新模型的平均评分
        remaining_reviews = db.query(ModelReview).filter(
            ModelReview.model_id == model_id
        ).all()

        model = db.query(MarketModel).filter(MarketModel.id == model_id).first()
        if remaining_reviews:
            model.rating = sum(r.rating for r in remaining_reviews) / len(remaining_reviews)
        else:
            model.rating = 0

        db.commit()
        return {"message": "评论已删除"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"删除评论失败: {str(e)}"
        )




@router.post("/api/admin/market/models/{model_id}/list")
async def list_market_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """重新上架已下架的市场模型"""
    try:
        # 查找模型
        model = db.query(MarketModel).filter(MarketModel.id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
            
        # 检查当前状态是否是已下架
        if model.status != "delisted":
            raise HTTPException(
                status_code=400,
                detail="Only delisted models can be listed"
            )
            
        # 将模型状态设置为待审核，需要重新通过审核
        model.status = "pending"
        # 更新时间
        model.updated_at = datetime.now(TIMEZONE)
        
        try:
            db.commit()
            return {
                "message": "Model listed successfully",
                "model": {
                    "id": model.id,
                    "name": model.name,
                    "status": model.status,
                    "updated_at": model.updated_at
                }
            }
        except Exception as db_error:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(db_error)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list model: {str(e)}"
        )



# API路由
@router.post("/api/private-models", response_model=PrivateModelResponse)
async def create_private_model(
    name: str = Form(...),
    description: str = Form(...),
    api_base_url: str = Form(...),
    api_key: str = Form(...),
    icon: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建私有模型"""
    try:
        # 处理图标上传
        icon_path = None
        if icon:
            if not icon.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail="Only image files allowed"
                )
            
            file_ext = Path(icon.filename).suffix.lower()
            file_name = f"{secrets.token_hex(8)}{file_ext}"
            file_path = UPLOAD_DIR / file_name
            
            with file_path.open("wb") as buffer:
                content = await icon.read()
                buffer.write(content)
                
            icon_path = f"/uploads/model-icons/{file_name}"

        # 创建模型记录
        model = PrivateModel(
            name=name,
            description=description,
            creator_id=current_user.id,
            api_base_url=api_base_url,
            api_key=api_key,
            icon=icon_path
        )
        
        db.add(model)
        db.commit()
        db.refresh(model)
        
        return model
        
    except Exception as e:
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/private-models", response_model=List[PrivateModelResponse])
async def get_private_models(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的私有模型列表"""
    models = db.query(PrivateModel)\
        .filter(PrivateModel.creator_id == current_user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return models

@router.get("/api/private-models/{model_id}", response_model=PrivateModelResponse)
async def get_private_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取私有模型详情"""
    model = db.query(PrivateModel).filter(
        PrivateModel.id == model_id,
        PrivateModel.creator_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    return model

@router.delete("/api/private-models/{model_id}")
async def delete_private_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除私有模型"""
    model = db.query(PrivateModel).filter(
        PrivateModel.id == model_id,
        PrivateModel.creator_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    try:
        # 删除图标文件
        if model.icon:
            icon_path = UPLOAD_DIR / Path(model.icon).name
            if icon_path.exists():
                icon_path.unlink()
                
        db.delete(model)
        db.commit()
        return {"message": "Model deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/admin/market/models/{model_id}/delist")
async def delist_market_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """下架市场模型"""
    try:
        # 查找模型
        model = db.query(MarketModel).filter(MarketModel.id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
            
        # 检查当前状态是否允许下架
        if model.status == "delisted":
            raise HTTPException(
                status_code=400,
                detail="Model is already delisted"
            )
            
        # 更新模型状态为已下架
        model.status = "delisted"
        # 记录更新时间
        model.updated_at = datetime.now(TIMEZONE)
        
        try:
            db.commit()
            return {
                "message": "Model delisted successfully",
                "model": {
                    "id": model.id,
                    "name": model.name,
                    "status": model.status,
                    "updated_at": model.updated_at
                }
            }
        except Exception as db_error:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(db_error)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delist model: {str(e)}"
        )

@router.post("/api/private-models/{model_id}/publish")
async def publish_to_market(
    model_id: int,
    name: str = Form(...),
    description: str = Form(...),
    api_base_url: str = Form(...),
    api_key: str = Form(...),
    distribution_type: str = Form(...),
    usage_type: str = Form(...),
    pull_price: int = Form(0),
    usage_price: int = Form(0),
    icon: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """将私有模型发布到市场"""
    # 验证私有模型存在并属于当前用户
    private_model = db.query(PrivateModel).filter(
        PrivateModel.id == model_id,
        PrivateModel.creator_id == current_user.id
    ).first()
    
    if not private_model:
        raise HTTPException(status_code=404, detail="Private model not found")
        
    try:
        # 处理图标
        icon_path = None
        if icon:
            if not icon.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail="Only image files allowed"
                )
                
            file_ext = Path(icon.filename).suffix.lower()
            file_name = f"{secrets.token_hex(8)}{file_ext}"
            file_path = UPLOAD_DIR / file_name
            
            with file_path.open("wb") as buffer:
                content = await icon.read()
                buffer.write(content)
                
            icon_path = f"/uploads/model-icons/{file_name}"
            
        # 创建市场模型
        market_model = MarketModel(
            name=name,
            description=description,
            creator_id=current_user.id,
            icon=icon_path,
            distribution_type=distribution_type,
            pull_price=pull_price,
            usage_type=usage_type,
            usage_price=usage_price,
            api_base_url=api_base_url,
            api_key=api_key,
            status='pending'  # 新发布的模型需要审核
        )
        
        db.add(market_model)
        db.commit()
        db.refresh(market_model)
        
        return {
            "message": "Model published successfully",
            "model": {
                "id": market_model.id,
                "name": market_model.name,
                "status": market_model.status
            }
        }
        
    except Exception as e:
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/private-models/{model_id}")
async def update_private_model(
    model_id: int,
    name: str = Form(...),
    description: str = Form(...),
    api_base_url: str = Form(...),
    api_key: str = Form(...),
    icon: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新私有模型"""
    model = db.query(PrivateModel).filter(
        PrivateModel.id == model_id,
        PrivateModel.creator_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    try:
        # 处理新图标
        if icon:
            if not icon.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail="Only image files allowed"
                )
            
            # 删除旧图标
            if model.icon:
                old_icon_path = UPLOAD_DIR / Path(model.icon).name
                if old_icon_path.exists():
                    old_icon_path.unlink()
            
            # 保存新图标
            file_ext = Path(icon.filename).suffix.lower()
            file_name = f"{secrets.token_hex(8)}{file_ext}"
            file_path = UPLOAD_DIR / file_name
            
            with file_path.open("wb") as buffer:
                content = await icon.read()
                buffer.write(content)
                
            model.icon = f"/uploads/model-icons/{file_name}"

        # 更新其他字段
        model.name = name
        model.description = description
        model.api_base_url = api_base_url
        model.api_key = api_key
        
        db.commit()
        db.refresh(model)
        return model
        
    except Exception as e:
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

