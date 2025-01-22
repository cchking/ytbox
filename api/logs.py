from class_model import *
from func import *

from fastapi import APIRouter
router = APIRouter() 


@router.get("/api/admin/logs/overview")
async def get_logs_overview(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    try:
        # 构建基础查询
        query = db.query(APILog)
        
        # 添加时间过滤
        if start_date:
            query = query.filter(APILog.timestamp >= start_date)
        if end_date:
            query = query.filter(APILog.timestamp <= end_date)

        # 总请求数
        total_requests = query.count()

        if total_requests == 0:
            return {
                "total_requests": 0,
                "error_count": 0,
                "avg_response_time": 0,
                "success_count": 0,
                "success_rate": 0
            }

        # 错误数（有error字段的请求）
        error_count = query.filter(APILog.error.isnot(None)).count()

        # 平均响应时间
        avg_response_time = db.query(func.avg(APILog.response_time))\
            .filter(APILog.response_time.isnot(None))\
            .scalar() or 0

        # 成功请求数（状态码小于400的请求）
        success_count = query.filter(APILog.response_status < 400).count()

        return {
            "total_requests": total_requests,
            "error_count": error_count,
            "avg_response_time": round(float(avg_response_time), 2),
            "success_count": success_count,
            "success_rate": round((success_count / total_requests) * 100, 1) if total_requests > 0 else 0
        }
        
    except Exception as e:
        print(f"Error getting logs overview: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取统计数据失败: {str(e)}"
        )






@router.get("/api/admin/logs/export")
async def export_system_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[int] = None,
    status_code: Optional[str] = None,
    method: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    try:
        # 构建基础查询
        query = db.query(
            APILog,
            User.username
        ).join(
            User,
            APILog.user_id == User.id
        )
        
        # 应用过滤条件
        if start_date:
            query = query.filter(APILog.timestamp >= start_date)
        if end_date:
            query = query.filter(APILog.timestamp <= end_date)
        if user_id:
            query = query.filter(APILog.user_id == user_id)
        if method:
            query = query.filter(APILog.method == method)
            
        # 处理状态码过滤
        if status_code:
            if status_code == '2xx':
                query = query.filter(APILog.response_status.between(200, 299))
            elif status_code == '4xx':
                query = query.filter(APILog.response_status.between(400, 499))
            elif status_code == '5xx':
                query = query.filter(APILog.response_status.between(500, 599))
            else:
                try:
                    specific_status = int(status_code)
                    query = query.filter(APILog.response_status == specific_status)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail="无效的状态码格式"
                    )
        
        # 获取数据并按时间排序
        logs = query.order_by(APILog.timestamp.desc()).all()
        
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
        
        # 创建 CSV 输出
        output = StringIO(newline='')
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        # 写入 UTF-8 BOM
        output.write('\ufeff')
        
        # 写入标题行
        headers = [
            "时间", "用户", "请求方法", "请求路径", "状态码", 
            "响应时间(ms)", "IP地址", "用户代理",
            "请求数据", "响应数据", "错误信息"
        ]
        writer.writerow(headers)
        
        # 写入数据行
        for log, username in logs:
            # 转换时间到东八区
            timestamp = log.timestamp
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=ZoneInfo('UTC'))
            timestamp = timestamp.astimezone(TIMEZONE)
            
            row = [
                timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                clean_text(username),
                clean_text(log.method),
                clean_text(log.endpoint),
                str(log.response_status),
                str(round(log.response_time) if log.response_time else 0),
                clean_text(log.ip_address),
                clean_text(log.user_agent),
                clean_text(log.request_data),
                clean_text(log.response_data),
                clean_text(log.error)
            ]
            writer.writerow(row)
        
        # 获取输出内容
        output.seek(0)
        content = output.getvalue()
        output.close()
        
        # 设置响应头
        headers = {
            'Content-Disposition': f'attachment; filename=system-logs-{datetime.now().strftime("%Y%m%d-%H%M%S")}.csv',
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


@router.get("/api/admin/logs", response_model=List[APILogResponse])
async def get_api_logs(
    skip: int = 0,
    limit: int = 100,  
    user_id: Optional[int] = None,
    status_code: Optional[str] = None,  
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    # 使用 join 查询来获取用户信息
    query = db.query(APILog, User.username)\
            .join(User, APILog.user_id == User.id)
    
    # 应用过滤条件
    if user_id:
        query = query.filter(APILog.user_id == user_id)

    # 添加时间范围过滤
    if start_date:
        query = query.filter(APILog.timestamp >= start_date)
    if end_date:
        query = query.filter(APILog.timestamp <= end_date)

    if status_code:
        # 处理状态码范围筛选（2xx, 4xx, 5xx）
        if status_code == '2xx':
            query = query.filter(APILog.response_status.between(200, 299))
        elif status_code == '4xx':
            query = query.filter(APILog.response_status.between(400, 499))
        elif status_code == '5xx':
            query = query.filter(APILog.response_status.between(500, 599))
        else:
            try:
                # 尝试将具体的状态码转换为整数
                specific_status = int(status_code)
                query = query.filter(APILog.response_status == specific_status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid status code format"
                )

    if endpoint:
        query = query.filter(APILog.endpoint.contains(endpoint))
    if method:
        query = query.filter(APILog.method == method)

    # 按时间倒序排序
    query = query.order_by(APILog.timestamp.desc())
    
    # 分页
    results = query.offset(skip).limit(limit).all()
    
    # 处理结果
    logs = []
    for log, username in results:
        log_dict = log.__dict__
        
        # 转换时间到东八区
        if log_dict.get('timestamp'):
            if log_dict['timestamp'].tzinfo is None:
                log_dict['timestamp'] = log_dict['timestamp'].replace(tzinfo=ZoneInfo('UTC'))
            log_dict['timestamp'] = log_dict['timestamp'].astimezone(TIMEZONE)
            
        log_dict['username'] = username
        logs.append(log_dict)

    return logs

@router.get("/api/admin/logs/stats")
async def get_log_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    query = db.query(APILog)
    
    if start_date:
        query = query.filter(APILog.timestamp >= start_date)
    if end_date:
        query = query.filter(APILog.timestamp <= end_date)
    
    # 总请求数
    total_requests = query.count()
    
    # 按状态码统计
    status_stats = db.query(
        APILog.response_status,
        func.count(APILog.id).label('count')
    ).group_by(APILog.response_status).all()
    
    # 按端点统计
    endpoint_stats = db.query(
        APILog.endpoint,
        func.count(APILog.id).label('count'),
        func.avg(APILog.response_time).label('avg_response_time')
    ).group_by(APILog.endpoint).all()
    
    # 响应时间统计
    time_stats = db.query(
        func.avg(APILog.response_time).label('avg'),
        func.min(APILog.response_time).label('min'),
        func.max(APILog.response_time).label('max')
    ).first()
    
    # 错误率统计
    error_count = query.filter(APILog.error.isnot(None)).count()
    
    return {
        "total_requests": total_requests,
        "status_stats": [{"status": s[0], "count": s[1]} for s in status_stats],
        "endpoint_stats": [{
            "endpoint": e[0],
            "count": e[1],
            "avg_response_time": e[2]
        } for e in endpoint_stats],
        "time_stats": {
            "avg": time_stats.avg,
            "min": time_stats.min,
            "max": time_stats.max
        },
        "error_rate": error_count / total_requests if total_requests > 0 else 0
    }

@router.delete("/api/admin/logs/cleanup")
async def cleanup_old_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[int] = None,
    status_code: Optional[str] = None,
    method: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_permission)
):
    try:
        print(f"开始清理日志，收到的参数：")
        print(f"start_date: {start_date}")
        print(f"end_date: {end_date}")

        # 构建基础查询
        query = db.query(APILog)
        
        # 处理时间过滤
        if start_date:
            # 将本地时间转换为UTC时间进行存储和比较
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=TIMEZONE)
            start_date_utc = start_date.astimezone(timezone.utc).replace(tzinfo=None)
            query = query.filter(APILog.timestamp >= start_date_utc)
            print(f"添加起始时间过滤 UTC: {start_date_utc}")

        if end_date:
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=TIMEZONE)
            end_date_utc = end_date.astimezone(timezone.utc).replace(tzinfo=None)
            query = query.filter(APILog.timestamp <= end_date_utc)
            print(f"添加结束时间过滤 UTC: {end_date_utc}")

        if user_id:
            query = query.filter(APILog.user_id == user_id)
            print(f"添加用户ID过滤: {user_id}")
            
        if method:
            query = query.filter(APILog.method == method)
            print(f"添加请求方法过滤: {method}")

        # 在删除之前打印将要删除的记录数
        to_delete_count = query.count()
        print(f"符合条件的记录数: {to_delete_count}")

        # 执行删除操作
        deleted_count = query.delete(synchronize_session=False)
        print(f"实际删除的记录数: {deleted_count}")
        
        # 提交事务
        db.commit()
        
        return {
            "message": f"成功删除 {deleted_count} 条日志记录",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        db.rollback()
        print(f"清理日志时出错: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"清理日志失败: {str(e)}"
        )
  