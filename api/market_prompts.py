from class_model import *
from func import *

from fastapi import APIRouter
router = APIRouter() 



# 修改后端路由函数
@router.get("/api/prompt-market/my-prompts")
async def get_my_prompts(
    type: PromptType = Query(PromptType.ALL, description="提示词类型：created(创建的)/purchased(购买的)/all(全部)"),
    status: Optional[str] = Query(None, description="商品状态：pending/approved/rejected/delisted"),
    skip: int = Query(0, description="Skip N items"),
    limit: int = Query(10, description="Limit to N items"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户的提示词商品，支持按类型筛选
    """
    try:
        result = {
            "total": 0,
            "items": []
        }

        # 处理创建的商品
        if type in [PromptType.CREATED, PromptType.ALL]:
            created_query = db.query(PromptProduct).filter(
                PromptProduct.creator_id == current_user.id
            )
            
            if status:
                created_query = created_query.filter(PromptProduct.status == status)
            
            if type == PromptType.CREATED:
                # 如果只要创建的商品，直接应用分页
                created_products = created_query.order_by(PromptProduct.created_at.desc())\
                    .offset(skip)\
                    .limit(limit)\
                    .all()
                result["total"] = created_query.count()
            else:
                # 如果是获取全部，先获取所有创建的商品
                created_products = created_query.all()
                result["total"] += created_query.count()
            
            # 处理创建的商品数据
            for product in created_products:
                # 获取标签
                tags = db.query(Tag).join(PromptProductTag)\
                    .filter(PromptProductTag.product_id == product.id).all()
                
                # 获取销售数据
                sales_count = db.query(PromptPurchase)\
                    .filter(PromptPurchase.product_id == product.id)\
                    .count()
                
                # 确保日期是带时区的
                created_at = product.created_at
                if created_at and created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=TIMEZONE)
                
                product_data = {
                    "id": product.id,
                    "title": product.title,
                    "description": product.description,
                    "content": product.content,
                    "price": product.price,
                    "status": product.status,
                    "likes": product.likes,
                    "dislikes": product.dislikes,
                    "created_at": created_at.isoformat() if created_at else None,
                    "sales_count": sales_count,
                    "type": "created",
                    "tags": [
                        {
                            "id": tag.id,
                            "name": tag.name,
                            "color": tag.color
                        }
                        for tag in tags
                    ]
                }
                result["items"].append(product_data)

        # 处理购买的商品
        if type in [PromptType.PURCHASED, PromptType.ALL]:
            purchased_query = db.query(
                PromptPurchase,
                PromptProduct,
                User.username.label('creator_username')
            ).join(
                PromptProduct,
                PromptPurchase.product_id == PromptProduct.id
            ).join(
                User,
                PromptProduct.creator_id == User.id
            ).filter(
                PromptPurchase.user_id == current_user.id
            )
            
            if status:
                purchased_query = purchased_query.filter(PromptProduct.status == status)
            
            if type == PromptType.PURCHASED:
                purchased_items = purchased_query.order_by(PromptPurchase.created_at.desc())\
                    .offset(skip)\
                    .limit(limit)\
                    .all()
                result["total"] = purchased_query.count()
            else:
                purchased_items = purchased_query.all()
                result["total"] += purchased_query.count()
            
            for purchase, product, creator_username in purchased_items:
                # 获取标签
                tags = db.query(Tag).join(PromptProductTag)\
                    .filter(PromptProductTag.product_id == product.id).all()

                # 确保日期是带时区的
                purchase_created_at = purchase.created_at
                if purchase_created_at and purchase_created_at.tzinfo is None:
                    purchase_created_at = purchase_created_at.replace(tzinfo=TIMEZONE)
                    
                product_created_at = product.created_at
                if product_created_at and product_created_at.tzinfo is None:
                    product_created_at = product_created_at.replace(tzinfo=TIMEZONE)
                
                purchase_data = {
                    "id": product.id,
                    "title": product.title,
                    "description": product.description,
                    "content": product.content,
                    "price": product.price,
                    "status": product.status,
                    "likes": product.likes,
                    "dislikes": product.dislikes,
                    "creator_username": creator_username,
                    "created_at": product_created_at.isoformat() if product_created_at else None,
                    "purchase_info": {
                        "id": purchase.id,
                        "created_at": purchase_created_at.isoformat() if purchase_created_at else None,
                        "price": purchase.price,
                        "commission_rate": purchase.commission_rate
                    },
                    "type": "purchased",
                    "tags": [
                        {
                            "id": tag.id,
                            "name": tag.name,
                            "color": tag.color
                        }
                        for tag in tags
                    ]
                }
                result["items"].append(purchase_data)

        # 如果是获取全部内容，需要手动处理分页和排序
        if type == PromptType.ALL:
            # 按创建时间/购买时间排序
            result["items"].sort(
                key=lambda x: x.get("purchase_info", {}).get("created_at", x["created_at"]) or "",
                reverse=True
            )
            # 应用分页
            result["items"] = result["items"][skip:skip + limit]

        return result
            
    except Exception as e:
        print(f"Error getting user prompts: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"获取提示词记录失败: {str(e)}"
        )

# 上架已下架的商品
@router.get("/api/prompt-market/settings")
async def get_public_prompt_market_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取提示市场的公开设置信息
    - 不需要管理员权限
    - 返回基本的市场规则设置
    """
    try:
        settings = db.query(PromptMarketSettings).first()
        if not settings:
            # 如果没有设置，创建默认设置
            settings = PromptMarketSettings()
            db.add(settings)
            db.commit()
            db.refresh(settings)
        
        return {
            "commission_rate": settings.commission_rate,
            "require_review": settings.require_review,
            "min_price": settings.min_price,
            "max_price": settings.max_price
        }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取市场设置失败: {str(e)}"
        )



# 4. 为提示词添加/移除标签的路由
@router.post("/api/admin/prompts/{product_id}/tags/{tag_id}")
async def add_tag_to_prompt(
    product_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    product = db.query(PromptProduct).filter(PromptProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    if tag in product.tags:
        raise HTTPException(status_code=400, detail="Tag already added")
    
    product.tags.append(tag)
    try:
        db.commit()
        return {"message": "Tag added successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/api/admin/prompts/{product_id}/tags/{tag_id}")
async def remove_tag_from_prompt(
    product_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    product = db.query(PromptProduct).filter(PromptProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    if tag not in product.tags:
        raise HTTPException(status_code=400, detail="Tag not found in product")
    
    product.tags.remove(tag)
    try:
        db.commit()
        return {"message": "Tag removed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/api/admin/prompt-market/products/{product_id}/list")
async def list_prompt_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    # 获取商品
    product = db.query(PromptProduct).filter(PromptProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 检查商品状态
    if product.status != "delisted":
        raise HTTPException(status_code=400, detail="Product is not delisted")
    
    # 上架商品
    product.status = "approved"
    product.updated_at = datetime.now(TIMEZONE)
    
    try:
        db.commit()
        db.refresh(product)
        return {"message": "Product listed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# 从数据库中删除商品
@router.delete("/api/admin/prompt-market/products/{product_id}")
async def delete_prompt_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    # 获取商品
    product = db.query(PromptProduct).filter(PromptProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        # 删除相关的购买记录
        db.query(PromptPurchase).filter(
            PromptPurchase.product_id == product_id
        ).delete()
        
        # 删除相关的投票记录
        db.query(PromptVote).filter(
            PromptVote.product_id == product_id
        ).delete()
        
        # 删除商品本身
        db.delete(product)
        db.commit()
        
        return {"message": "Product deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to delete product: {str(e)}"
        )



@router.get("/api/admin/prompt-market/stats")
async def get_prompt_market_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    try:
        # 获取当前日期（东八区）
        today = datetime.now(TIMEZONE).date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        # 获取总提示词数
        total_prompts = db.query(PromptProduct).count()

        # 获取待审核数
        pending_reviews = db.query(PromptProduct).filter(
            PromptProduct.status == "pending"
        ).count()

        # 获取今日购买次数
        today_purchases = db.query(PromptPurchase).filter(
            PromptPurchase.created_at >= today_start,
            PromptPurchase.created_at <= today_end
        ).count()

        return {
            "totalPrompts": total_prompts,
            "pendingReviews": pending_reviews,
            "todayPurchases": today_purchases
        }

    except Exception as e:
        print(f"Error getting prompt market stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取统计数据失败: {str(e)}"
        )



@router.get("/api/admin/prompt-market/settings")
async def get_prompt_market_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    settings = db.query(PromptMarketSettings).first()
    if not settings:
        settings = PromptMarketSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.put("/api/admin/prompt-market/settings")
async def update_prompt_market_settings(
    settings_update: PromptMarketSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    settings = db.query(PromptMarketSettings).first()
    if not settings:
        settings = PromptMarketSettings()
        db.add(settings)
    
    update_data = settings_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)
    
    try:
        db.commit()
        db.refresh(settings)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return settings


# 获取提示列表
@router.get("/api/prompts")
async def get_prompts(
    page: int = 1,  # 当前页码
    page_size: int = 12,  # 每页数量
    tag_id: Optional[int] = None,  # 标签过滤
    sort: str = "newest",  # 排序方式: newest(最新), popular(最热门), price-asc(价格从低到高), price-desc(价格从高到低)
    search: Optional[str] = None,  # 搜索关键词
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 构建基础查询
        query = db.query(PromptProduct, User.username)\
            .join(User, PromptProduct.creator_id == User.id)
        
        # 非管理员只能看到已通过审核的和自己创建的提示
        if current_user.role != UserRole.ADMIN:
            query = query.filter(
                or_(
                    PromptProduct.status == "approved",
                    and_(
                        PromptProduct.creator_id == current_user.id,
                        PromptProduct.status != "delisted"
                    )
                )
            )
            
        # 标签过滤
        if tag_id:
            query = query.join(PromptProductTag)\
                .filter(PromptProductTag.tag_id == tag_id)
        
        # 关键词搜索
        if search:
            search = f"%{search}%"
            query = query.filter(
                or_(
                    PromptProduct.title.ilike(search),
                    PromptProduct.description.ilike(search)
                )
            )
        
        # 排序
        if sort == "popular":
            query = query.order_by(PromptProduct.likes.desc())
        elif sort == "price-asc":
            query = query.order_by(PromptProduct.price.asc())
        elif sort == "price-desc":
            query = query.order_by(PromptProduct.price.desc())
        else:  # newest
            query = query.order_by(PromptProduct.created_at.desc())
        
        # 获取总数
        total = query.count()
        
        # 分页
        query = query.offset(offset).limit(page_size + 1)  # 多获取一条用于判断是否有更多
        results = query.all()
        
        # 判断是否有下一页
        has_more = len(results) > page_size
        if has_more:
            results = results[:-1]
            
        # 获取用户的购买记录
        purchases = {
            p.product_id: p 
            for p in db.query(PromptPurchase).filter(
                PromptPurchase.user_id == current_user.id
            ).all()
        }
        
        # 获取用户的投票记录
        votes = {
            v.product_id: v.vote_type 
            for v in db.query(PromptVote).filter(
                PromptVote.user_id == current_user.id
            ).all()
        }
        
        # 处理响应数据
        prompts = []
        for product, creator_username in results:
            # 查询提示的标签
            tags = db.query(Tag).join(PromptProductTag)\
                .filter(PromptProductTag.product_id == product.id).all()
            
            prompt_data = {
                "id": product.id,
                "title": product.title,
                "description": product.description,
                "content": product.content if (
                    product.id in purchases or 
                    product.creator_id == current_user.id or 
                    current_user.role == UserRole.ADMIN
                ) else None,
                "price": product.price,
                "creator_id": product.creator_id,
                "creator_username": creator_username,
                "gradientFrom": "#4F46E5",  # 这里可以根据需要设置渐变色
                "gradientTo": "#9333EA",
                "status": product.status,
                "likes": product.likes,
                "dislikes": product.dislikes,
                "is_hot": product.likes > 10,  # 可以根据需要调整热门标准
                "created_at": product.created_at,
                "has_purchased": product.id in purchases,
                "has_voted": votes.get(product.id),
                "tags": [
                    {
                        "id": tag.id,
                        "name": tag.name,
                        "color": tag.color
                    } 
                    for tag in tags
                ]
            }
            prompts.append(prompt_data)
            
        return {
            "data": prompts,
            "has_more": has_more,
            "total": total
        }
            
    except Exception as e:
        print(f"Error getting prompts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取提示列表失败: {str(e)}"
        )

# 获取单个提示详情
@router.get("/api/prompts/{prompt_id}")
async def get_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 获取提示详情
    result = db.query(PromptProduct, User.username)\
        .join(User, PromptProduct.creator_id == User.id)\
        .filter(PromptProduct.id == prompt_id)\
        .first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Prompt not found")
        
    product, creator_username = result
    
    # 检查访问权限
    if current_user.role != UserRole.ADMIN:
        if product.status != "approved" and product.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="No permission to view this prompt")
    
    # 检查是否已购买
    has_purchased = db.query(PromptPurchase).filter(
        PromptPurchase.user_id == current_user.id,
        PromptPurchase.product_id == prompt_id
    ).first() is not None
    
    # 获取用户的投票状态
    vote = db.query(PromptVote).filter(
        PromptVote.user_id == current_user.id,
        PromptVote.product_id == prompt_id
    ).first()
    
    # 获取标签
    tags = db.query(Tag).join(PromptProductTag)\
        .filter(PromptProductTag.product_id == prompt_id).all()
    
    return {
        "id": product.id,
        "title": product.title,
        "description": product.description,
        "content": product.content if (
            has_purchased or 
            product.creator_id == current_user.id or 
            current_user.role == UserRole.ADMIN
        ) else None,
        "price": product.price,
        "creator_id": product.creator_id,
        "creator_username": creator_username,
        "status": product.status,
        "likes": product.likes,
        "dislikes": product.dislikes,
        "created_at": product.created_at,
        "has_purchased": has_purchased,
        "has_voted": vote.vote_type if vote else None,
        "tags": [
            {
                "id": tag.id,
                "name": tag.name,
                "color": tag.color
            }
            for tag in tags
        ]
    }



# 管理员路由
@router.get("/api/admin/prompt-market/products")
async def get_prompt_products(
    page: int = Query(1, description="页码，从1开始"),
    size: int = Query(10, description="每页数量"),
    status: Optional[str] = None,
    tags: Optional[List[int]] = Query(None, alias="tags[]"),  # 修改这里以接收标签ID数组
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    try:
        # 计算正确的偏移量
        skip = (page - 1) * size

        # 构建基础查询，使用join获取创建者用户名和标签信息
        query = db.query(PromptProduct, User.username.label('creator_username'))\
            .join(User, PromptProduct.creator_id == User.id)\
            .options(joinedload(PromptProduct.tags))

        # 如果有标签过滤
        if tags:
            # 使用 join 和 filter 进行标签过滤
            query = query.join(PromptProductTag)\
                .filter(PromptProductTag.tag_id.in_(tags))

        # 应用状态过滤
        if status:
            query = query.filter(PromptProduct.status == status)

        # 计算过滤后的总数
        total = query.count()

        # 获取分页数据
        results = query.offset(skip).limit(size).all()

        # 处理结果
        products = []
        for product, creator_username in results:
            # 处理标签
            tags = [
                {
                    "id": tag.id,
                    "name": tag.name,
                    "color": tag.color,
                    "description": tag.description,
                    "type": tag.type,
                    "sort_order": tag.sort_order,
                    "is_active": tag.is_active,
                    "created_at": tag.created_at,
                    "created_by": tag.created_by
                }
                for tag in product.tags
            ]

            product_dict = {
                "id": product.id,
                "title": product.title,
                "description": product.description,
                "content": product.content,
                "price": product.price,
                "creator_id": product.creator_id,
                "creator_username": creator_username,
                "likes": product.likes,
                "dislikes": product.dislikes,
                "status": product.status,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
                "tags": tags
            }
            products.append(product_dict)

        return {
            "total": total,
            "items": products,
            "page": page,
            "page_size": size
        }

    except Exception as e:
        print(f"Error getting prompt products: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"获取提示词列表失败: {str(e)}"
        )

    
@router.put("/api/admin/prompt-market/products/{product_id}")
async def admin_update_prompt_product(
    product_id: int,
    product_update: PromptProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    product = db.query(PromptProduct).filter(PromptProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    try:
        db.commit()
        db.refresh(product)
        return product
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/admin/prompt-market/products/{product_id}/review")
async def admin_review_prompt_product(
    product_id: int,
    action: str = Query(..., pattern="^(approve|reject)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    product = db.query(PromptProduct).filter(PromptProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.status != "pending":
        raise HTTPException(status_code=400, detail="Product is not pending review")
    
    product.status = "approved" if action == "approve" else "rejected"
    try:
        db.commit()
        db.refresh(product)
        return {"message": f"Product {action}d successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/admin/prompt-market/products/{product_id}/delist")
async def admin_delist_prompt_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    product = db.query(PromptProduct).filter(PromptProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.status = "delisted"
    try:
        db.commit()
        db.refresh(product)
        return {"message": "Product delisted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))





# 提示词CRUD路由
@router.post("/api/prompt-market/products", response_model=PromptProductResponse)
async def create_prompt_product(
    product: PromptProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 验证价格范围
    settings = db.query(PromptMarketSettings).first()
    if not settings:
        settings = PromptMarketSettings()
        db.add(settings)
        db.commit()
        
    if product.price < settings.min_price or product.price > settings.max_price:
        raise HTTPException(
            status_code=400,
            detail=f"Price must be between {settings.min_price} and {settings.max_price}"
        )
    
    now = datetime.now(TIMEZONE)
    # 创建商品
    db_product = PromptProduct(
        title=product.title,
        description=product.description,
        content=product.content,
        price=product.price,
        creator_id=current_user.id,
        status="pending" if settings.require_review else "approved",
        created_at=now,
        updated_at=now
    )
    
    db.add(db_product)
    
    try:
        # 先提交以获取产品ID
        db.commit()
        db.refresh(db_product)

        # 添加标签关联
        if product.tags:
            # 获取所有标签
            tags = db.query(Tag).filter(Tag.id.in_(product.tags)).all()
            # 关联标签
            db_product.tags = tags
            db.commit()
            db.refresh(db_product)

        response_data = {
            "id": db_product.id,
            "title": db_product.title,
            "description": db_product.description,
            "content": db_product.content,
            "price": db_product.price,
            "creator_id": db_product.creator_id,
            "creator_username": current_user.username,
            "likes": 0,
            "dislikes": 0,
            "status": db_product.status,
            "created_at": db_product.created_at,
            "updated_at": db_product.updated_at,
            "has_purchased": False,
            "has_voted": None,
            "tags": [
                {
                    "id": tag.id,
                    "name": tag.name,
                    "color": tag.color,
                    "description": tag.description,
                    "type": tag.type,
                    "sort_order": tag.sort_order,
                    "is_active": tag.is_active,
                    "created_at": tag.created_at,
                    "created_by": tag.created_by
                }
                for tag in db_product.tags
            ]
        }
        
        return response_data
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/prompt-market/products", response_model=List[PromptProductResponse])
async def list_prompt_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 获取市场设置
    settings = db.query(PromptMarketSettings).first()
    require_review = settings.require_review if settings else True
    
    # 基础查询
    query = db.query(PromptProduct)
    
    # 如果需要审核且不是管理员，只显示已通过的商品和自己创建的商品
    if require_review and current_user.role != UserRole.ADMIN:
        query = query.filter(
            or_(
                PromptProduct.status == "approved",
                and_(
                    PromptProduct.creator_id == current_user.id,
                    PromptProduct.status != "delisted"
                )
            )
        )
    elif current_user.role != UserRole.ADMIN:
        # 不需要审核但不是管理员，显示所有未下架的商品
        query = query.filter(PromptProduct.status != "delisted")
    
    products = query.offset(skip).limit(limit).all()
    
    # 获取当前用户的购买记录
    purchases = {
        p.product_id: p 
        for p in db.query(PromptPurchase).filter(
            PromptPurchase.user_id == current_user.id
        ).all()
    }
    
    # 获取当前用户的投票记录
    votes = {
        v.product_id: v.vote_type 
        for v in db.query(PromptVote).filter(
            PromptVote.user_id == current_user.id
        ).all()
    }
    
    # 处理响应
    result = []
    for product in products:
        product_dict = PromptProductResponse(
            id=product.id,
            title=product.title,
            description=product.description,
            # 只有已购买或是创建者才能看到内容
            content=product.content if (
                product.id in purchases or 
                product.creator_id == current_user.id or 
                current_user.role == UserRole.ADMIN
            ) else None,
            price=product.price,
            creator_id=product.creator_id,
            creator_username=product.creator.username,
            likes=product.likes,
            dislikes=product.dislikes,
            status=product.status,
            created_at=product.created_at,
            updated_at=product.updated_at,
            has_purchased=product.id in purchases,
            has_voted=votes.get(product.id)
        )
        result.append(product_dict)
    
    return result

@router.post("/api/prompt-market/products/{product_id}/purchase")
async def purchase_prompt_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 检查商品是否存在且已通过审核
    product = db.query(PromptProduct).filter(
        PromptProduct.id == product_id,
        PromptProduct.status == "approved"
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or not approved")
    
    # 检查是否已购买
    existing_purchase = db.query(PromptPurchase).filter(
        PromptPurchase.user_id == current_user.id,
        PromptPurchase.product_id == product_id
    ).first()
    if existing_purchase:
        raise HTTPException(status_code=400, detail="Already purchased")
    
    # 检查金币是否足够
    price = product.price  # 商品价格应该是整数
    if current_user.coins < price:
        raise HTTPException(status_code=400, detail="Insufficient coins")
    
    # 获取市场设置
    settings = db.query(PromptMarketSettings).first()
    commission_rate = settings.commission_rate if settings else 0.1
    
    # 计算分成（向下取整确保是整数）
    creator_share = int(price * (1 - commission_rate))  # 使用 floor 除法确保整数结果
    platform_share = price - creator_share  # 平台获得剩余的金币，确保总和等于原价格
    
    try:
        # 买家扣除金币
        current_user.coins -= price
        
        # 卖家增加金币
        creator = db.query(User).filter(User.id == product.creator_id).first()
        if creator:
            # 确保 coins 字段不是 None 并且加上整数收益
            creator.coins = (creator.coins or 0) + creator_share
            print(f"Creator coins before: {creator.coins - creator_share}")
            print(f"Adding creator share: {creator_share}")
            print(f"Creator coins after: {creator.coins}")
        
        # 记录购买
        purchase = PromptPurchase(
            user_id=current_user.id,
            product_id=product_id,
            price=price,
            commission_rate=commission_rate
        )
        db.add(purchase)
        
        # 记录金币变动
        coin_logs = [
            # 买家消费记录
            CoinLog(
                user_id=current_user.id,
                amount=-price,
                type="consume",
                description=f"Purchased prompt product: {product.title}"
            ),
            # 卖家收入记录
            CoinLog(
                user_id=product.creator_id,
                amount=creator_share,
                type="income",
                description=f"Prompt product sale: {product.title}"
            )
        ]
        db.add_all(coin_logs)
        
        db.commit()
        
        print(f"Transaction completed:")
        print(f"- Original price: {price}")
        print(f"- Creator share: {creator_share}")
        print(f"- Platform share: {platform_share}")
        
        return {
            "message": "Purchase successful",
            "product": product,
            "price": price,
            "creator_share": creator_share,
            "platform_share": platform_share
        }
    except Exception as e:
        db.rollback()
        print(f"Error during purchase: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/prompt-market/products/{product_id}/vote")
async def vote_prompt_product(
    product_id: int,
    vote: PromptVoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if vote.vote_type not in ["like", "dislike"]:
        raise HTTPException(status_code=400, detail="Invalid vote type")
    
    # 检查商品是否存在和状态
    product = db.query(PromptProduct).filter(PromptProduct.id == product_id).first()
    if not product or product.status != "approved":
        raise HTTPException(status_code=404, detail="Product not found or not approved")
    
    # 检查是否是自己的商品
    if product.creator_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot vote on your own product")

    # 检查用户是否已购买该商品
    purchase = db.query(PromptPurchase).filter(
        PromptPurchase.user_id == current_user.id,
        PromptPurchase.product_id == product_id
    ).first()
    
    # 如果不是管理员且未购买商品，不允许投票
    if not purchase and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="You need to purchase this product before voting")
    
    # 检查是否已经投票
    existing_vote = db.query(PromptVote).filter(
        PromptVote.user_id == current_user.id,
        PromptVote.product_id == product_id
    ).first()
    
    try:
        if existing_vote:
            # 如果投票类型相同，取消投票
            if existing_vote.vote_type == vote.vote_type:
                if vote.vote_type == "like":
                    product.likes = max(0, product.likes - 1)
                else:
                    product.dislikes = max(0, product.dislikes - 1)
                db.delete(existing_vote)
            else:
                # 改变投票类型
                if vote.vote_type == "like":
                    product.likes += 1
                    product.dislikes = max(0, product.dislikes - 1)
                else:
                    product.dislikes += 1
                    product.likes = max(0, product.likes - 1)
                existing_vote.vote_type = vote.vote_type
        else:
            # 新投票
            new_vote = PromptVote(
                user_id=current_user.id,
                product_id=product_id,
                vote_type=vote.vote_type
            )
            db.add(new_vote)
            if vote.vote_type == "like":
                product.likes += 1
            else:
                product.dislikes += 1
        
        db.commit()
        return {
            "message": "Vote recorded successfully",
            "likes": product.likes,
            "dislikes": product.dislikes
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/prompt-market/purchases/stats", response_model=PromptPurchaseStats)
async def get_purchase_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 获取用户的所有购买记录
    purchases = db.query(PromptPurchase).filter(
        PromptPurchase.user_id == current_user.id
    ).order_by(PromptPurchase.created_at.desc()).all()
    
    # 计算总支出
    total_spent = sum(purchase.price for purchase in purchases)
    
    # 构建响应
    purchase_responses = []
    for purchase in purchases:
        product = purchase.product
        purchase_responses.append(PromptPurchaseResponse(
            id=purchase.id,
            product_id=product.id,
            product_title=product.title,
            price=purchase.price,
            commission_rate=purchase.commission_rate,
            created_at=purchase.created_at
        ))
    
    return PromptPurchaseStats(
        total_spent=total_spent,
        purchase_count=len(purchases),
        purchases=purchase_responses
    )



@router.post("/api/chats/with-private-prompt")
async def create_chat_with_private_prompt(
    chat_data: ChatWithPrivatePromptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 检查私有提示词
    prompt = db.query(PrivatePrompt).filter(
        PrivatePrompt.id == chat_data.prompt_id,
        PrivatePrompt.user_id == current_user.id
    ).first()
    
    if not prompt:
        raise HTTPException(status_code=404, detail="Private prompt not found")
    
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

@router.post("/api/private-prompts", response_model=PrivatePromptResponse)
async def create_private_prompt(
    prompt: PrivatePromptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_prompt = PrivatePrompt(
        **prompt.dict(),
        user_id=current_user.id
    )
    db.add(db_prompt)
    try:
        db.commit()
        db.refresh(db_prompt)
        return db_prompt
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/private-prompts", response_model=List[PrivatePromptResponse])
async def get_private_prompts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prompts = db.query(PrivatePrompt)\
        .filter(PrivatePrompt.user_id == current_user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return prompts

@router.get("/api/private-prompts/{prompt_id}", response_model=PrivatePromptResponse)
async def get_private_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prompt = db.query(PrivatePrompt).filter(
        PrivatePrompt.id == prompt_id,
        PrivatePrompt.user_id == current_user.id
    ).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Private prompt not found")
    return prompt

@router.put("/api/private-prompts/{prompt_id}", response_model=PrivatePromptResponse)
async def update_private_prompt(
    prompt_id: int,
    prompt_update: PrivatePromptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_prompt = db.query(PrivatePrompt).filter(
        PrivatePrompt.id == prompt_id,
        PrivatePrompt.user_id == current_user.id
    ).first()
    if not db_prompt:
        raise HTTPException(status_code=404, detail="Private prompt not found")

    for key, value in prompt_update.dict(exclude_unset=True).items():
        setattr(db_prompt, key, value)

    try:
        db.commit()
        db.refresh(db_prompt)
        return db_prompt
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/api/private-prompts/{prompt_id}")
async def delete_private_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_prompt = db.query(PrivatePrompt).filter(
        PrivatePrompt.id == prompt_id,
        PrivatePrompt.user_id == current_user.id
    ).first()
    if not db_prompt:
        raise HTTPException(status_code=404, detail="Private prompt not found")

    try:
        db.delete(db_prompt)
        db.commit()
        return {"message": "Private prompt deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/api/private-prompts/{prompt_id}/publish", response_model=PromptProductResponse)
async def publish_private_prompt(
    prompt_id: int,
    publish_data: PublishPromptRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 获取私有提示词
    private_prompt = db.query(PrivatePrompt).filter(
        PrivatePrompt.id == prompt_id,
        PrivatePrompt.user_id == current_user.id
    ).first()
    if not private_prompt:
        raise HTTPException(status_code=404, detail="Private prompt not found")

    # 获取市场设置
    settings = db.query(PromptMarketSettings).first()
    if not settings:
        settings = PromptMarketSettings()
        db.add(settings)
        db.commit()

    # 验证价格范围
    if publish_data.price < settings.min_price or publish_data.price > settings.max_price:
        raise HTTPException(
            status_code=400,
            detail=f"Price must be between {settings.min_price} and {settings.max_price}"
        )

    # 创建市场商品
    now = datetime.now(TIMEZONE)
    market_prompt = PromptProduct(
        title=private_prompt.title,
        description=private_prompt.description,
        content=private_prompt.content,
        price=publish_data.price,
        creator_id=current_user.id,
        status="pending" if settings.require_review else "approved",
        created_at=now,
        updated_at=now
    )
    
    db.add(market_prompt)
    
    try:
        # 先提交以获取产品ID
        db.commit()
        db.refresh(market_prompt)

        # 添加标签关联
        if publish_data.tags:
            # 获取所有标签
            tags = db.query(Tag).filter(Tag.id.in_(publish_data.tags)).all()
            # 关联标签
            market_prompt.tags = tags
            db.commit()
            db.refresh(market_prompt)

        # 构建响应数据，确保包含 creator_username
        response_data = {
            "id": market_prompt.id,
            "title": market_prompt.title,
            "description": market_prompt.description,
            "content": market_prompt.content,
            "price": market_prompt.price,
            "creator_id": market_prompt.creator_id,
            "creator_username": current_user.username,  # 添加创建者用户名
            "likes": market_prompt.likes,
            "dislikes": market_prompt.dislikes,
            "status": market_prompt.status,
            "created_at": market_prompt.created_at,
            "updated_at": market_prompt.updated_at,
            "has_purchased": False,
            "has_voted": None,
            "tags": [
                {
                    "id": tag.id,
                    "name": tag.name,
                    "color": tag.color,
                    "description": tag.description,
                    "type": tag.type,
                    "sort_order": tag.sort_order,
                    "is_active": tag.is_active,
                    "created_at": tag.created_at,
                    "created_by": tag.created_by
                }
                for tag in market_prompt.tags
            ]
        }

        return response_data
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/admin/tags", response_model=TagResponse)
async def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    # 检查标签名是否已存在
    if db.query(Tag).filter(Tag.name == tag.name).first():
        raise HTTPException(
            status_code=400,
            detail="Tag name already exists"
        )
    
    db_tag = Tag(
        **tag.dict(),
        created_by=current_user.id
    )
    db.add(db_tag)
    
    try:
        db.commit()
        db.refresh(db_tag)
        return db_tag
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))




@router.get("/api/admin/tags", response_model=List[TagResponse])
async def get_tags(
    type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 改为依赖当前用户而不是管理员检查
):
    """获取标签列表，根据用户角色返回不同内容"""
    query = db.query(Tag)
    
    # 如果不是管理员，只返回激活的标签
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Tag.is_active == True)
    
    # 按类型过滤
    if type:
        query = query.filter(Tag.type == type)
    
    # 按排序字段排序    
    query = query.order_by(Tag.sort_order.asc())
    
    # 只有管理员应用分页
    if current_user.role == UserRole.ADMIN:
        query = query.offset(skip).limit(limit)
    
    return query.all()

@router.put("/api/admin/tags/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
        
    # 如果更新名称，检查是否与其他标签重复
    if tag_update.name and tag_update.name != db_tag.name:
        if db.query(Tag).filter(Tag.name == tag_update.name).first():
            raise HTTPException(
                status_code=400,
                detail="Tag name already exists"
            )
    
    for key, value in tag_update.dict(exclude_unset=True).items():
        setattr(db_tag, key, value)
    
    try:
        db.commit()
        db.refresh(db_tag)
        return db_tag
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/api/admin/tags/{tag_id}")
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    try:
        # 先删除关联关系
        db.query(PromptProductTag).filter(PromptProductTag.tag_id == tag_id).delete()
        # 再删除标签
        db.delete(tag)
        db.commit()
        return {"message": "Tag deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
