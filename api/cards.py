from class_model import *
from func import *

from fastapi import APIRouter
router = APIRouter() 
# 在后端添加删除单个卡密的路由
@router.delete("/api/admin/cards/{card_no}")
async def delete_single_card(
    card_no: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    card = db.query(Card).filter(Card.card_no == card_no).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
        
    try:
        db.delete(card)
        db.commit()
        return {"message": "Card deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/admin/cards", response_model=List[CardResponse])
async def create_cards(
    card_data: CardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """批量创建卡密"""
    try:
        # 生成批次号
        batch_no = f"B{int(time.time())}"
        
        # 批量创建卡密
        cards = []
        for _ in range(card_data.count):
            # 生成随机卡密
            card_no = secrets.token_hex(8).upper()
            
            card = Card(
                card_no=card_no,
                type=card_data.type,
                value=card_data.value,
                creator_id=current_user.id,
                expired_at=card_data.expired_at,
                batch_no=batch_no
            )
            cards.append(card)
        
        db.add_all(cards)
        db.commit()
        
        # 刷新获取完整数据
        for card in cards:
            db.refresh(card)
            
        return cards
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"创建卡密失败: {str(e)}"
        )

@router.get("/api/admin/cards", response_model=List[CardResponse])
async def list_cards(
    skip: int = 0,
    limit: int = 100,
    type: Optional[CardType] = None,
    is_used: Optional[bool] = None,
    batch_no: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """获取卡密列表"""
    query = db.query(Card)
    
    if type:
        query = query.filter(Card.type == type)
    if is_used is not None:
        query = query.filter(Card.is_used == is_used)
    if batch_no:
        query = query.filter(Card.batch_no == batch_no)
        
    return query.offset(skip).limit(limit).all()

@router.post("/api/cards/use/{card_no}")
async def use_card(
    card_no: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """使用卡密"""
    # 查找并锁定卡密记录
    card = db.query(Card).filter(Card.card_no == card_no)\
        .with_for_update().first()
        
    if not card:
        raise HTTPException(status_code=404, detail="卡密不存在")
        
    if card.is_used:
        raise HTTPException(status_code=400, detail="卡密已被使用")
        
    # 确保使用带时区的当前时间进行比较
    current_time = datetime.now(TIMEZONE)
    
    if card.expired_at and card.expired_at.replace(tzinfo=TIMEZONE) < current_time:
        card.is_expired = True
        db.commit()
        raise HTTPException(status_code=400, detail="卡密已过期")
    
    try:
        # 更新卡密状态
        card.is_used = True
        card.used_by = current_user.id
        card.used_at = current_time
        
        # 根据卡密类型处理奖励
        if card.type == CardType.VIP:
            # 处理VIP天数
            if not current_user.vip_until or current_user.vip_until.replace(tzinfo=TIMEZONE) < current_time:
                current_user.vip_until = current_time
            current_user.vip_until = (current_user.vip_until.replace(tzinfo=TIMEZONE) + 
                                    timedelta(days=card.value))
            
        elif card.type == CardType.COIN:
            # 处理金币
            current_user.coins = (current_user.coins or 0) + card.value
            
            # 记录金币变动
            coin_log = CoinLog(
                user_id=current_user.id,
                amount=card.value,
                type="admin",
                description=f"使用卡密 {card_no}"
            )
            db.add(coin_log)
        
        db.commit()
        
        return {
            "message": "卡密使用成功",
            "type": card.type,
            "value": card.value
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"使用卡密失败: {str(e)}"
        )



@router.get("/api/admin/cards/export")
async def export_cards(
    batch_no: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """导出指定批次的卡密"""
    cards = db.query(Card).filter(Card.batch_no == batch_no).all()
    if not cards:
        raise HTTPException(status_code=404, detail="找不到指定批次的卡密")
    
    # 创建CSV输出
    output = StringIO()
    writer = csv.writer(output)
    
    # 写入标题行
    writer.writerow(['卡密号', '类型', '面值', '过期时间'])
    
    # 写入数据行
    for card in cards:
        writer.writerow([
            card.card_no,
            '会员' if card.type == CardType.VIP else '金币',
            f"{card.value}{'天' if card.type == CardType.VIP else '个'}",
            card.expired_at.strftime('%Y-%m-%d %H:%M:%S') if card.expired_at else '永不过期'
        ])
    
    # 获取输出内容
    output.seek(0)
    content = output.getvalue()
    
    # 设置响应头
    headers = {
        'Content-Disposition': f'attachment; filename=cards-{batch_no}.csv',
        'Content-Type': 'text/csv; charset=utf-8-sig'
    }
    
    return Response(
        content=content.encode('utf-8-sig'),
        media_type='text/csv',
        headers=headers
    )

# 获取卡密购买网站信息(用户可访问)
@router.get("/api/card-purchase-info")
async def get_card_purchase_info(
    db: Session = Depends(get_db)
):
    settings = db.query(SystemSettings).first()
    if not settings:
        return {
            "url": None,
            "description": None
        }
        
    return {
        "url": settings.card_purchase_url,
        "description": settings.card_purchase_description
    }
