from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Notification, User
from ..auth import get_current_user

router=APIRouter(prefix="/api/notifications",tags=["Notifications"])

@router.get("")
def notifications(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    return [{"id":n.id,"message":n.message,"is_read":n.is_read,"created_at":n.created_at} for n in db.query(Notification).filter(Notification.user_id==user.id).order_by(Notification.created_at.desc()).limit(50).all()]

@router.post("/read-all")
def read_all(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    db.query(Notification).filter(Notification.user_id==user.id,Notification.is_read==False).update({"is_read":True}); db.commit(); return {"message":"Notifications marked as read"}
