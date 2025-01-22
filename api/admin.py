from class_model import *
from func import *

from fastapi import APIRouter
router = APIRouter() 
#@app.get("/api/admin/models")

@router.get("/debug/check_admin")
async def check_admin(db: Session = Depends(get_db)):
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        return {
            "exists": True,
            "username": admin.username,
            "role": admin.role,
            "is_active": admin.is_active
        }
    return {"exists": False}










