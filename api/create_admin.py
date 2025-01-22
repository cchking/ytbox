import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from init import *



def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_admin():
    db = SessionLocal()
    try:
        # 检查管理员是否存在
        result = db.execute(
            text("SELECT * FROM users WHERE username = :username"),
            {"username": "admin"}
        ).first()
        
        if result:
            print("Admin account already exists!")
            return

        # 创建管理员账户
        hashed_password = get_password_hash("admin123")
        db.execute(
            text("""
            INSERT INTO users (username, email, hashed_password, role, is_active, is_banned) 
            VALUES (:username, :email, :password, :role, :is_active, :is_banned)
            """),
            {
                "username": "admin",
                "email": "admin@example.com",
                "password": hashed_password,
                "role": "ADMIN",
                "is_active": True,
                "is_banned": False  # 添加这个字段
            }
        )
        db.commit()
        print("Admin account created successfully!")
        print("Username: admin")
        print("Password: admin123")
    except Exception as e:
        db.rollback()
        print(f"Error creating admin account: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()