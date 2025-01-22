from class_model import *
from func import *

from fastapi import APIRouter
router = APIRouter() 
@router.get("/api/admin/dangerous-chats", response_model=List[DangerousChatResponse])
async def get_dangerous_chats(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    query = db.query(DangerousChat, User.username)\
        .join(User, DangerousChat.user_id == User.id)
    
    if start_date:
        query = query.filter(DangerousChat.created_at >= start_date)
    if end_date:
        query = query.filter(DangerousChat.created_at <= end_date)
    if user_id:
        query = query.filter(DangerousChat.user_id == user_id)
    
    query = query.order_by(DangerousChat.created_at.desc())
    results = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": chat.id,
            "user_id": chat.user_id,
            "username": username,
            "content": chat.content,
            "matched_words": json.loads(chat.matched_words),
            "ip_address": chat.ip_address,
            "user_agent": chat.user_agent,
            "created_at": chat.created_at,
            "request_data": chat.request_data
        }
        for chat, username in results
    ]

@router.get("/api/admin/dangerous-chats/stats")
async def get_dangerous_chats_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """
    获取违规对话的统计信息
    """
    try:
        # 计算总违规数
        total_count = db.query(DangerousChat).count()
        
        # 获取今日日期（东八区）
        today = datetime.now(TIMEZONE).date()
        today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=TIMEZONE)
        today_end = datetime.combine(today, datetime.max.time()).replace(tzinfo=TIMEZONE)
        
        # 计算今日违规数
        today_count = db.query(DangerousChat).filter(
            DangerousChat.created_at >= today_start,
            DangerousChat.created_at <= today_end
        ).count()
        
        # 按用户统计违规次数
        user_stats = db.query(
            DangerousChat.user_id,
            User.username,
            func.count(DangerousChat.id).label('count')
        ).join(User).group_by(DangerousChat.user_id, User.username).all()
        
        # 计算总违规用户数
        unique_users_count = len(user_stats)
        
        # 计算AI回复的违规数（为了兼容SQLite，改用Python处理）
        all_chats = db.query(DangerousChat).all()
        ai_response_count = sum(
            1 for chat in all_chats 
            if chat.request_data and chat.request_data.get('is_ai_response', False)
        )
        
        user_input_count = total_count - ai_response_count
        
        # 最近的违规记录
        recent_chats = db.query(DangerousChat)\
            .order_by(DangerousChat.created_at.desc())\
            .limit(5)\
            .all()
        
        return {
            "total_count": total_count,
            "today_count": today_count,
            "unique_users_count": unique_users_count,
            "ai_response_count": ai_response_count,
            "user_input_count": user_input_count,
            "user_stats": [
                {
                    "user_id": stat[0],
                    "username": stat[1],
                    "violation_count": stat[2]
                }
                for stat in user_stats
            ],
            "recent_violations": [
                {
                    "id": chat.id,
                    "created_at": chat.created_at,
                    "matched_words": json.loads(chat.matched_words),
                    "is_ai_response": chat.request_data.get('is_ai_response', False) if chat.request_data else False
                }
                for chat in recent_chats
            ]
        }
    except Exception as e:
        print(f"Error in get_dangerous_chats_stats: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取统计信息失败: {str(e)}"
        )

@router.get("/api/admin/dangerous-chats/{chat_id}")
async def get_dangerous_chat_detail(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    chat = db.query(DangerousChat, User.username)\
        .join(User, DangerousChat.user_id == User.id)\
        .filter(DangerousChat.id == chat_id)\
        .first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Dangerous chat record not found")
        
    dangerous_chat, username = chat
    
    return {
        "id": dangerous_chat.id,
        "user_id": dangerous_chat.user_id,
        "username": username,
        "content": dangerous_chat.content,
        "matched_words": json.loads(dangerous_chat.matched_words),
        "ip_address": dangerous_chat.ip_address,
        "user_agent": dangerous_chat.user_agent,
        "created_at": dangerous_chat.created_at,
        "request_data": dangerous_chat.request_data,
        "chat_history": dangerous_chat.request_data.get("chat_history", [])
    }
@router.get("/api/admin/forbidden-words", response_model=List[ForbiddenWordResponse])
async def get_forbidden_words(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    words = db.query(ForbiddenWord)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return words

#@router.get("/api/admin/forbidden-words")




@router.post("/api/admin/forbidden-words", response_model=ForbiddenWordResponse)
async def create_forbidden_word(
    word: ForbiddenWordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    """
    创建新的违禁词
    """
    # 检查违禁词是否已存在
    db_word = db.query(ForbiddenWord).filter(ForbiddenWord.word == word.word).first()
    if db_word:
        raise HTTPException(status_code=400, detail="该违禁词已存在")
    
    # 创建新违禁词
    db_word = ForbiddenWord(
        word=word.word,
        level=word.level,
        description=word.description,
        created_by=current_user.id
    )
    
    db.add(db_word)
    try:
        db.commit()
        db.refresh(db_word)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"创建失败：{str(e)}")
    
    return db_word

@router.delete("/api/admin/forbidden-words/{word_id}")
async def delete_forbidden_word(
    word_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    db_word = db.query(ForbiddenWord).filter(ForbiddenWord.id == word_id).first()
    if not db_word:
        raise HTTPException(status_code=404, detail="违禁词不存在")
    
    db.delete(db_word)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "删除成功"}
