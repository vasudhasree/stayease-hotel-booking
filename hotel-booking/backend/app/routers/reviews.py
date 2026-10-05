from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Review, Booking, User
from ..schemas import ReviewCreate, ReviewReply
from ..auth import require_role
from ..utils import recalc_rating, notify
from .ws import manager

router=APIRouter(prefix="/api/reviews",tags=["Reviews"])

def review_dict(r):
    return {"id":r.id,"hotel_id":r.hotel_id,"booking_id":r.booking_id,"user_name":r.user_name,"rating":r.rating,"comment":r.comment,"category":r.category,"admin_reply":r.admin_reply,"created_at":r.created_at}

@router.post("",status_code=201)
async def create_review(data:ReviewCreate,db:Session=Depends(get_db),user:User=Depends(require_role("customer"))):
    b=db.get(Booking,data.booking_id)
    if not b: raise HTTPException(404,"Booking not found")
    if b.user_id!=user.id: raise HTTPException(403,"This booking does not belong to you")
    if b.status!="Checked-out": raise HTTPException(400,"You can review only after check-out")
    if b.review: raise HTTPException(409,"This booking has already been reviewed")
    category="Good" if data.rating>=4 else "Medium" if data.rating==3 else "Bad"
    r=Review(hotel_id=b.hotel_id,user_id=user.id,booking_id=b.id,user_name=user.name,rating=data.rating,comment=data.comment.strip(),category=category)
    db.add(r); db.flush(); recalc_rating(db,b.hotel); notify(db,user.id,f"Thanks for reviewing {b.hotel.name}!"); db.commit(); db.refresh(r)
    await manager.broadcast({"type":"review_created","hotel_id":b.hotel_id,"review":review_dict(r)})
    return review_dict(r)

@router.patch("/{review_id}/reply")
def reply(review_id:int,data:ReviewReply,db:Session=Depends(get_db),user:User=Depends(require_role("admin"))):
    r=db.get(Review,review_id)
    if not r: raise HTTPException(404,"Review not found")
    r.admin_reply=data.reply.strip(); notify(db,r.user_id,f"The hotel team replied to your review at {r.hotel.name}."); db.commit(); return review_dict(r)
