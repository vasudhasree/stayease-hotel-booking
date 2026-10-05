from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import ProfileUpdate, PasswordUpdate
from ..auth import get_current_user, verify_password, hash_password

router=APIRouter(prefix="/api/users",tags=["Users"])

@router.get("/me")
def me(user:User=Depends(get_current_user)): return {"id":user.id,"name":user.name,"email":user.email,"role":user.role}

@router.put("/me")
def update_me(data:ProfileUpdate,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    other=db.query(User).filter(User.email==data.email.lower(),User.id!=user.id).first()
    if other: raise HTTPException(409,"Email is already used")
    user.name=data.name.strip(); user.email=data.email.lower(); db.commit(); return {"id":user.id,"name":user.name,"email":user.email,"role":user.role}

@router.put("/password")
def change_password(data:PasswordUpdate,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    if not verify_password(data.current_password,user.password_hash): raise HTTPException(400,"Current password is incorrect")
    user.password_hash=hash_password(data.new_password); db.commit(); return {"message":"Password changed successfully"}
