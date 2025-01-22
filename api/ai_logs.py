#ai-logs.py
from class_model import *
from func import *

from fastapi import APIRouter
router = APIRouter() 
@router.get("/api/user/ai-logs")
async def get_user_ai_logs(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 构建基础查询
        query = db.query(
            AIRequestLog,
            User.username,
            func.coalesce(Channel.channel_name, 'market').label('channel_name')  # 市场模型显示"market"
        ).join(
            User,
            AIRequestLog.user_id == User.id
        ).outerjoin(  # 改为外连接以包含没有channel的记录
            Channel,
            AIRequestLog.channel_id == Channel.id
        ).filter(
            AIRequestLog.user_id == current_user.id
        )

        # 获取总数
        total = query.count()
        
        # 获取分页数据
        results = query.order_by(AIRequestLog.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

        # 处理结果
        logs = []
        for log, username, channel_name in results:
            # 判断是否是市场模型调用
            is_market_model = log.model_name.startswith('@')
            
            log_dict = {
                "id": log.id,
                "user_id": log.user_id,
                "username": username,
                "model_name": log.model_name,
                "channel_id": log.channel_id,
                "channel_name": "Market Model" if is_market_model else channel_name,
                "streaming": log.streaming,
                "first_token_latency": log.first_token_latency or 0,
                "total_latency": log.total_latency or 0,
                "prompt_tokens": log.prompt_tokens or 0,
                "completion_tokens": log.completion_tokens or 0,
                "total_tokens": log.total_tokens or 0,
                "request_text": log.request_text or "",
                "response_text": log.response_text or "",
                "error": log.error,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            logs.append(log_dict)

        return {
            "items": logs,
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit,
            "has_more": total > (skip + limit)
        }
        
    except Exception as e:
        print(f"Error getting user AI logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取日志失败: {str(e)}"
        )



@router.get("/api/user/ai-logs/stats")
def get_user_ai_logs_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(AIRequestLog).filter(AIRequestLog.user_id == current_user.id)
    
    if start_date:
        query = query.filter(AIRequestLog.created_at >= start_date)
    if end_date:
        query = query.filter(AIRequestLog.created_at <= end_date)
    
    logs = query.all()
    
    # 基础统计
    total_requests = len(logs)
    total_tokens = sum(log.total_tokens or 0 for log in logs)
    failed_requests = sum(1 for log in logs if log.error)
    successful_requests = total_requests - failed_requests
    
    # 计算错误率
    error_rate = failed_requests / total_requests if total_requests > 0 else 0
    
    # 计算平均值
    avg_tokens = total_tokens / total_requests if total_requests > 0 else 0
    avg_latency = sum(log.total_latency or 0 for log in logs) / successful_requests if successful_requests > 0 else 0
    
    # 模型使用统计
    model_stats = {}
    for log in logs:
        if log.model_name not in model_stats:
            model_stats[log.model_name] = {"count": 0, "tokens": 0}
        model_stats[log.model_name]["count"] += 1
        model_stats[log.model_name]["tokens"] += log.total_tokens or 0
    
    models_usage = [
        {
            "model": model,
            "count": stats["count"],
            "tokens": stats["tokens"]
        }
        for model, stats in model_stats.items()
    ]
    
    # 按日期统计
    date_stats = {}
    for log in logs:
        date = log.created_at.date().isoformat()
        if date not in date_stats:
            date_stats[date] = {"count": 0, "tokens": 0}
        date_stats[date]["count"] += 1
        date_stats[date]["tokens"] += log.total_tokens or 0
    
    daily_usage = [
        {
            "date": date,
            "count": stats["count"],
            "tokens": stats["tokens"]
        }
        for date, stats in date_stats.items()
    ]

    return {
        "total_requests": total_requests,
        "total_tokens": total_tokens,
        "avg_tokens": round(avg_tokens, 2),
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "error_rate": error_rate,  # 添加错误率字段
        "avg_latency": round(avg_latency, 2),
        "models_usage": models_usage,
        "daily_usage": daily_usage
    }



@router.get("/api/admin/ai-logs")
async def get_ai_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    model_name: Optional[str] = None,
    channel_id: Optional[int] = None,
    min_tokens: Optional[int] = None,
    max_tokens: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    streaming: Optional[StreamingFilter] = Query(default=StreamingFilter.NULL, description="过滤流式请求：true/false/null"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    query = db.query(
        AIRequestLog,
        User.username,
        Channel.channel_name
    ).join(
        User,
        AIRequestLog.user_id == User.id
    ).join(
        Channel,
        AIRequestLog.channel_id == Channel.id
    )
    
    # 应用过滤条件
    if user_id:
        query = query.filter(AIRequestLog.user_id == user_id)
    if model_name:
        query = query.filter(AIRequestLog.model_name == model_name)
    if channel_id:
        query = query.filter(AIRequestLog.channel_id == channel_id)
    if min_tokens:
        query = query.filter(AIRequestLog.total_tokens >= min_tokens)
    if max_tokens:
        query = query.filter(AIRequestLog.total_tokens <= max_tokens)
    if streaming != StreamingFilter.NULL:
        query = query.filter(AIRequestLog.streaming == (streaming == StreamingFilter.TRUE))
    if start_date:
        query = query.filter(AIRequestLog.created_at >= start_date)
    if end_date:
        query = query.filter(AIRequestLog.created_at <= end_date)

    # 获取总数
    total_count = query.count()
    
    # 按时间倒序排序并应用分页
    query = query.order_by(AIRequestLog.created_at.desc())
    results = query.offset(skip).limit(limit).all()
    
    # 处理结果
    logs = []
    for log, username, channel_name in results:
        log_dict = log.__dict__.copy()  # 创建副本避免修改原始对象
        
        # 转换时间为ISO格式字符串
        if log_dict.get('created_at'):
            log_dict['created_at'] = serialize_datetime(log_dict['created_at'])
            
        # 设置默认值
        log_dict.setdefault('first_token_latency', 0.0)
        log_dict.setdefault('total_latency', 0.0)
        log_dict.setdefault('prompt_tokens', 0)
        log_dict.setdefault('completion_tokens', 0)
        log_dict.setdefault('total_tokens', 0)
        log_dict.setdefault('request_text', "")
        log_dict.setdefault('response_text', "")
        log_dict.setdefault('error', None)
            
        # 添加用户名和渠道名称
        log_dict['username'] = username
        log_dict['channel_name'] = channel_name
        
        # 处理 prompt_messages
        try:
            log_dict['prompt_messages'] = json.loads(log.prompt_messages) if log.prompt_messages else []
        except json.JSONDecodeError:
            log_dict['prompt_messages'] = []
        except Exception as e:
            print(f"Error processing prompt messages: {str(e)}")
            log_dict['prompt_messages'] = []
        
        # 移除 SQLAlchemy 特定的属性
        log_dict.pop('_sa_instance_state', None)
        
        logs.append(log_dict)

    return JSONResponse(
        content={
            "items": logs,
            "total": total_count,
            "page": skip // limit + 1 if limit > 0 else 1,
            "page_size": limit
        }
    )



@router.get("/api/admin/ai-logs/token-stats")
async def get_token_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[int] = None,
    model_name: Optional[str] = None,
    channel_id: Optional[int] = None,
    min_tokens: Optional[int] = None,
    max_tokens: Optional[int] = None,
    streaming: Optional[StreamingFilter] = Query(default=StreamingFilter.NULL, description="过滤流式请求：true/false/null"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    try:
        # 设置默认时间范围为过去24小时
        if not end_date:
            end_date = datetime.now(TIMEZONE)
        if not start_date:
            start_date = end_date - timedelta(hours=24)

        # 确保时间包含时区信息
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=TIMEZONE)
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=TIMEZONE)

        # 构建基础查询条件
        base_query = db.query(AIRequestLog)
        if start_date:
            base_query = base_query.filter(AIRequestLog.created_at >= start_date)
        if end_date:
            base_query = base_query.filter(AIRequestLog.created_at <= end_date)
        
        # 添加其他筛选条件
        if user_id:
            base_query = base_query.filter(AIRequestLog.user_id == user_id)
        if model_name:
            base_query = base_query.filter(AIRequestLog.model_name == model_name)
        if channel_id:
            base_query = base_query.filter(AIRequestLog.channel_id == channel_id)
        if min_tokens:
            base_query = base_query.filter(AIRequestLog.total_tokens >= min_tokens)
        if max_tokens:
            base_query = base_query.filter(AIRequestLog.total_tokens <= max_tokens)
        if streaming != StreamingFilter.NULL:
            base_query = base_query.filter(AIRequestLog.streaming == (streaming == StreamingFilter.TRUE))

        # 找到筛选后数据中的最后一条记录时间
        last_record = base_query.order_by(AIRequestLog.created_at.desc()).first()
        if not last_record:
            # 如果没有数据，返回空结果
            return {
                "total_requests": 0,
                "error_rate": 0,
                "latency_stats": {
                    "avg_first_token_latency": 0,
                    "avg_total_latency": 0
                },
                "token_usage": {
                    "total_prompt_tokens": 0,
                    "total_completion_tokens": 0,
                    "total_tokens": 0,
                    "average_prompt_tokens": 0,
                    "average_completion_tokens": 0
                },
                "timeLabels": [],
                "tokenData": [],
                "firstTokenLatencyData": [],
                "totalLatencyData": []
            }

        # 计算图表的时间范围（基于筛选后的最后一条数据）
        chart_end = last_record.created_at
        chart_start = chart_end - timedelta(hours=12)

        # 获取统计数据（使用筛选后的查询）
        total_requests = base_query.count()
        error_count = base_query.filter(AIRequestLog.error.isnot(None)).count()
        error_rate = error_count / total_requests if total_requests > 0 else 0

        # 获取响应时间统计
        latency_stats = db.query(
            func.avg(AIRequestLog.first_token_latency).label('avg_first_token_latency'),
            func.avg(AIRequestLog.total_latency).label('avg_total_latency')
        ).filter(base_query.whereclause).first()

        # Token使用统计
        token_stats = db.query(
            func.sum(AIRequestLog.prompt_tokens).label('total_prompt_tokens'),
            func.sum(AIRequestLog.completion_tokens).label('total_completion_tokens'),
            func.sum(AIRequestLog.total_tokens).label('total_tokens'),
            func.avg(AIRequestLog.prompt_tokens).label('avg_prompt_tokens'),
            func.avg(AIRequestLog.completion_tokens).label('avg_completion_tokens')
        ).filter(base_query.whereclause).first()

        # 生成最后12小时的时间点
        current_hour = chart_end.replace(minute=0, second=0, microsecond=0)
        start_hour = current_hour - timedelta(hours=11)  # 11小时前，加上当前小时共12小时
        
        # 创建时间点列表
        all_hours = []
        current = start_hour
        while current <= current_hour:
            all_hours.append(current)
            current += timedelta(hours=1)

        # 查询最后12小时的数据（使用筛选后的查询基础）
        chart_query = base_query.filter(AIRequestLog.created_at >= chart_start)

        hour_stats = db.query(
            func.strftime('%H:00', AIRequestLog.created_at).label('hour'),
            func.sum(AIRequestLog.total_tokens).label('total_tokens'),
            func.avg(AIRequestLog.first_token_latency).label('avg_first_token_latency'),
            func.avg(AIRequestLog.total_latency).label('avg_total_latency')
        ).filter(chart_query.whereclause).group_by(
            func.strftime('%H', AIRequestLog.created_at)
        ).all()

        # 将查询结果转换为字典
        hour_data = {}
        for stat in hour_stats:
            hour_data[stat.hour] = {
                'total_tokens': stat.total_tokens,
                'avg_first_token_latency': stat.avg_first_token_latency,
                'avg_total_latency': stat.avg_total_latency
            }

        # 处理时间序列数据
        timeLabels = []
        tokenData = []
        firstTokenLatencyData = []
        totalLatencyData = []

        # 填充每个小时的数据
        for hour in all_hours:
            hour_str = hour.strftime('%H:00')
            timeLabels.append(hour_str)
            
            if hour_str in hour_data:
                stat = hour_data[hour_str]
                tokenData.append(float(stat['total_tokens'] or 0))
                firstTokenLatencyData.append(float(stat['avg_first_token_latency'] or 0))
                totalLatencyData.append(float(stat['avg_total_latency'] or 0))
            else:
                tokenData.append(0.0)
                firstTokenLatencyData.append(0.0)
                totalLatencyData.append(0.0)

        return {
            "total_requests": total_requests,
            "error_rate": error_rate,
            "latency_stats": {
                "avg_first_token_latency": float(latency_stats.avg_first_token_latency or 0),
                "avg_total_latency": float(latency_stats.avg_total_latency or 0)
            },
            "token_usage": {
                "total_prompt_tokens": int(token_stats.total_prompt_tokens or 0),
                "total_completion_tokens": int(token_stats.total_completion_tokens or 0),
                "total_tokens": int(token_stats.total_tokens or 0),
                "average_prompt_tokens": float(token_stats.avg_prompt_tokens or 0),
                "average_completion_tokens": float(token_stats.avg_completion_tokens or 0)
            },
            "timeLabels": timeLabels,
            "tokenData": tokenData,
            "firstTokenLatencyData": firstTokenLatencyData,
            "totalLatencyData": totalLatencyData
        }

    except Exception as e:
        print(f"Error getting token stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/admin/ai-logs/stats")
async def get_ai_logs_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    # 基础查询
    base_query = db.query(AIRequestLog)
    
    if start_date:
        base_query = base_query.filter(AIRequestLog.created_at >= start_date)
    if end_date:
        base_query = base_query.filter(AIRequestLog.created_at <= end_date)
    
    # 1. 总请求数
    total_requests = base_query.count()
    print(f"Total requests found: {total_requests}")
    
    if total_requests == 0:
        return {
            "total_requests": 0,
            "token_stats": {
                "total_tokens": 0,
                "avg_tokens_per_request": 0,
                "min_tokens": 0,
                "max_tokens": 0
            },
            "latency_stats": {
                "avg_first_token_latency": 0,
                "avg_total_latency": 0,
                "min_latency": 0,
                "max_latency": 0
            },
            "error_rate": 0
        }

    # 2. Token统计
    token_query = base_query.with_entities(
        func.sum(AIRequestLog.total_tokens).label('total_tokens'),
        func.avg(AIRequestLog.total_tokens).label('avg_tokens'),
        func.min(AIRequestLog.total_tokens).label('min_tokens'),
        func.max(AIRequestLog.total_tokens).label('max_tokens')
    ).filter(AIRequestLog.total_tokens > 0)
    
    token_stats = token_query.first()
    print(f"Token stats query result: {token_stats}")

    # 3. 延迟统计
    latency_query = base_query.with_entities(
        func.avg(AIRequestLog.first_token_latency).label('avg_first_token_latency'),
        func.avg(AIRequestLog.total_latency).label('avg_total_latency'),
        func.min(AIRequestLog.total_latency).label('min_latency'),
        func.max(AIRequestLog.total_latency).label('max_latency')
    ).filter(
        AIRequestLog.total_latency > 0,
        AIRequestLog.first_token_latency > 0
    )
    
    latency_stats = latency_query.first()
    print(f"Latency stats query result: {latency_stats}")

    # 4. 错误率统计
    error_count = base_query.filter(AIRequestLog.error.isnot(None)).count()
    print(f"Error count: {error_count}")

    # 处理结果并返回
    result = {
        "total_requests": total_requests,
        "token_stats": {
            "total_tokens": int(token_stats.total_tokens or 0),
            "avg_tokens_per_request": round(float(token_stats.avg_tokens or 0), 2),
            "min_tokens": int(token_stats.min_tokens or 0),
            "max_tokens": int(token_stats.max_tokens or 0)
        },
        "latency_stats": {
            "avg_first_token_latency": round(float(latency_stats.avg_first_token_latency or 0), 2),
            "avg_total_latency": round(float(latency_stats.avg_total_latency or 0), 2),
            "min_latency": round(float(latency_stats.min_latency or 0), 2),
            "max_latency": round(float(latency_stats.max_latency or 0), 2)
        },
        "error_rate": error_count / total_requests if total_requests > 0 else 0
    }
    
    print(f"Returning stats: {result}")
    return result


@router.delete("/api/admin/ai-logs/cleanup")
async def cleanup_ai_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    try:
        # 构建基础查询
        query = db.query(AIRequestLog)
        
        # 添加时间范围筛选
        if start_date:
            query = query.filter(AIRequestLog.created_at >= start_date)
        if end_date:
            query = query.filter(AIRequestLog.created_at <= end_date)
            
        # 执行删除操作
        deleted_count = query.delete(synchronize_session=False)
        db.commit()
        
        return {
            "message": f"成功删除 {deleted_count} 条日志记录",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"删除日志失败: {str(e)}"
        )

@router.get("/api/admin/ai-logs/export")
async def export_ai_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[int] = None,
    model_name: Optional[str] = None,
    channel_id: Optional[int] = None,
    min_tokens: Optional[int] = None,
    max_tokens: Optional[int] = None,
    streaming: Optional[StreamingFilter] = Query(default=StreamingFilter.NULL),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    try:
        # 构建查询
        query = db.query(
            AIRequestLog,
            User.username,
            Channel.channel_name
        ).join(
            User,
            AIRequestLog.user_id == User.id
        ).join(
            Channel,
            AIRequestLog.channel_id == Channel.id
        )
        
        # 应用筛选条件
        if start_date:
            query = query.filter(AIRequestLog.created_at >= start_date)
        if end_date:
            query = query.filter(AIRequestLog.created_at <= end_date)
        if user_id:
            query = query.filter(AIRequestLog.user_id == user_id)
        if model_name:
            query = query.filter(AIRequestLog.model_name == model_name)
        if channel_id:
            query = query.filter(AIRequestLog.channel_id == channel_id)
        if min_tokens:
            query = query.filter(AIRequestLog.total_tokens >= min_tokens)
        if max_tokens:
            query = query.filter(AIRequestLog.total_tokens <= max_tokens)
        if streaming != StreamingFilter.NULL:
            query = query.filter(AIRequestLog.streaming == (streaming == StreamingFilter.TRUE))
            
        # 获取数据
        logs = query.order_by(AIRequestLog.created_at.desc()).all()
        
        def clean_text(text):
            """清理文本，处理特殊字符"""
            if text is None:
                return ""
            # 替换换行符为空格
            text = str(text).replace('\n', ' ').replace('\r', ' ')
            # 删除多余的空格
            text = ' '.join(text.split())
            # 确保文本被正确引用
            if '"' in text:
                text = text.replace('"', '""')
            return text
        
        # 使用 StringIO 并设置 newline='' 来正确处理换行
        output = StringIO(newline='')
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL, escapechar='\\')
        
        # 写入带 BOM 的 UTF-8 头
        output.write('\ufeff')
        
        # 写入标题行
        headers = [
            "时间", "用户", "模型", "渠道", "请求类型",
            "输入Tokens", "输出Tokens", "总Tokens",
            "首字延迟(ms)", "总延迟(ms)",
            "请求内容", "响应内容", "错误信息"
        ]
        writer.writerow(headers)
        
        # 写入数据行
        for log, username, channel_name in logs:
            row = [
                log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                clean_text(username),
                clean_text(log.model_name),
                clean_text(channel_name),
                "流式" if log.streaming else "普通",
                str(log.prompt_tokens or 0),
                str(log.completion_tokens or 0),
                str(log.total_tokens or 0),
                str(round(log.first_token_latency) if log.first_token_latency else 0),
                str(round(log.total_latency) if log.total_latency else 0),
                clean_text(log.request_text),
                clean_text(log.response_text),
                clean_text(log.error)
            ]
            writer.writerow(row)
        
        # 获取输出内容
        output.seek(0)
        content = output.getvalue()
        output.close()
        
        # 设置响应头
        headers = {
            'Content-Disposition': f'attachment; filename=ai-logs-{datetime.now().strftime("%Y%m%d-%H%M%S")}.csv',
            'Content-Type': 'text/csv; charset=utf-8-sig'
        }
        
        return Response(
            content=content.encode('utf-8-sig'),
            media_type='text/csv',
            headers=headers
        )
        
    except Exception as e:
        print(f"Export error: {str(e)}")  # 添加错误日志
        raise HTTPException(
            status_code=500,
            detail=f"导出日志失败: {str(e)}"
        )
