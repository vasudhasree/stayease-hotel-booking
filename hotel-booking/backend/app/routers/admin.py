from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import Booking, Hotel, User, Review
from ..auth import require_role

router=APIRouter(prefix="/api/admin",tags=["Admin"])

@router.get("/stats")
def stats(db:Session=Depends(get_db),user=Depends(require_role("admin"))):
    bookings=db.query(Booking).all()
    revenue=sum(b.total_price for b in bookings if b.status!="Cancelled")
    today=date.today()
    return {"total_bookings":len(bookings),"revenue":round(revenue,2),"hotels":db.query(Hotel).filter(Hotel.is_active==True).count(),"customers":db.query(User).filter(User.role=="customer").count(),"todays_checkins":sum(1 for b in bookings if b.check_in==today and b.status in ["Confirmed","Checked-in"])}

@router.get("/analytics")
def analytics(db:Session=Depends(get_db),user=Depends(require_role("admin"))):
    bookings=db.query(Booking).filter(Booking.status!="Cancelled").all()
    start=date.today()-timedelta(days=13)
    per_day=[]
    for i in range(14):
        d=start+timedelta(days=i); rows=[b for b in bookings if b.created_at.date()==d]
        per_day.append({"date":d.isoformat(),"bookings":len(rows),"revenue":round(sum(b.total_price for b in rows),2)})
    hotels=[]
    for h in db.query(Hotel).filter(Hotel.is_active==True).all():
        total=len([r for r in h.rooms if r.is_active]); booked=len([b for b in bookings if b.hotel_id==h.id and b.check_in<=date.today()<=b.check_out and b.status in ["Confirmed","Checked-in"]])
        hotels.append({"hotel":h.name,"occupancy":round((booked/total)*100,1) if total else 0,"rating":round(h.rating or 0,2)})
    top=sorted(hotels,key=lambda x:x["rating"],reverse=True)[:5]
    return {"per_day":per_day,"occupancy":hotels,"top_rated":top}

@router.get("/customers")
def customers(db:Session=Depends(get_db),user=Depends(require_role("admin"))):
    return [{"id":u.id,"name":u.name,"email":u.email,"created_at":u.created_at} for u in db.query(User).filter(User.role=="customer").order_by(User.created_at.desc()).all()]

@router.get("/reviews")
def reviews(db:Session=Depends(get_db),user=Depends(require_role("admin"))):
    return [{"id":r.id,"hotel_name":r.hotel.name,"user_name":r.user_name,"rating":r.rating,"comment":r.comment,"admin_reply":r.admin_reply,"created_at":r.created_at} for r in db.query(Review).order_by(Review.created_at.desc()).all()]
