from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Booking, Room, Hotel, User, Notification
from ..schemas import BookingCreate, BookingStatusUpdate
from ..auth import get_current_user, require_role
from ..utils import booking_conflicts, notify, notify_admins
from .ws import manager

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])

def booking_dict(b):
    return {"id":b.id,"reference":b.reference,"user_id":b.user_id,"customer_name":b.user.name,"hotel_id":b.hotel_id,"hotel_name":b.hotel.name,"room_id":b.room_id,"room_number":b.room.number,"room_type":b.room.type,"check_in":b.check_in,"check_out":b.check_out,"total_price":b.total_price,"status":b.status,"created_at":b.created_at,"reviewed": b.review is not None}

def next_reference(db):
    year = date.today().year
    prefix = f"SE-{year}-"
    count = db.query(Booking).filter(Booking.reference.like(f"{prefix}%")).count() + 1
    return f"{prefix}{count:05d}"

@router.post("", status_code=201)
async def create_booking(data: BookingCreate, db: Session = Depends(get_db), user: User = Depends(require_role("customer"))):
    if data.check_in < date.today(): raise HTTPException(400,"Check-in cannot be in the past")
    if data.check_out <= data.check_in: raise HTTPException(400,"Check-out must be after check-in")
    room = db.get(Room, data.room_id)
    if not room or not room.is_active: raise HTTPException(404,"Room not found")
    if booking_conflicts(db, room.id, data.check_in, data.check_out): raise HTTPException(409,"This room is already booked for those dates")
    nights = (data.check_out - data.check_in).days
    booking = Booking(reference=next_reference(db), user_id=user.id, hotel_id=room.hotel_id, room_id=room.id, check_in=data.check_in, check_out=data.check_out, total_price=room.price*nights, status="Confirmed")
    db.add(booking); db.flush()
    notify_admins(db, f"New booking at {room.hotel.name} • {booking.reference}")
    notify(db, user.id, f"Your booking {booking.reference} at {room.hotel.name} is confirmed.")
    db.commit(); db.refresh(booking)
    await manager.broadcast({"type":"booking_created","booking":booking_dict(booking)})
    return booking_dict(booking)

@router.get("/mine")
def my_bookings(db: Session = Depends(get_db), user: User = Depends(require_role("customer"))):
    rows = db.query(Booking).options(joinedload(Booking.user), joinedload(Booking.hotel), joinedload(Booking.room), joinedload(Booking.review)).filter(Booking.user_id==user.id).order_by(Booking.created_at.desc()).all()
    return [booking_dict(b) for b in rows]

@router.get("/admin")
def all_bookings(status: str = "", search: str = "", db: Session = Depends(get_db), user: User = Depends(require_role("admin"))):
    q=db.query(Booking).options(joinedload(Booking.user),joinedload(Booking.hotel),joinedload(Booking.room),joinedload(Booking.review))
    if status: q=q.filter(Booking.status==status)
    rows=q.order_by(Booking.created_at.desc()).all()
    if search:
        s=search.lower(); rows=[b for b in rows if s in b.reference.lower() or s in b.user.name.lower() or s in b.hotel.name.lower() or s in b.room.number.lower()]
    return [booking_dict(b) for b in rows]

@router.patch("/{booking_id}/cancel")
async def cancel_booking(booking_id:int, db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    b=db.get(Booking,booking_id)
    if not b: raise HTTPException(404,"Booking not found")
    if user.role=="customer" and b.user_id!=user.id: raise HTTPException(403,"Not your booking")
    if b.status not in ["Confirmed"]: raise HTTPException(400,"Only confirmed bookings can be cancelled")
    b.status="Cancelled"; notify(db,b.user_id,f"Booking {b.reference} was cancelled."); db.commit()
    await manager.broadcast({"type":"booking_updated","booking":booking_dict(b)})
    return booking_dict(b)

@router.patch("/{booking_id}/status")
async def change_status(booking_id:int,data:BookingStatusUpdate,db:Session=Depends(get_db),user:User=Depends(require_role("admin"))):
    b=db.get(Booking,booking_id)
    if not b: raise HTTPException(404,"Booking not found")
    allowed={"Confirmed":["Checked-in","Cancelled"],"Checked-in":["Checked-out"],"Checked-out":[],"Cancelled":[]}
    if data.status not in allowed.get(b.status,[]): raise HTTPException(400,f"Cannot change {b.status} to {data.status}")
    b.status=data.status
    if data.status=="Checked-out": notify(db,b.user_id,f"You were checked out from {b.hotel.name}. You can now rate your stay.")
    else: notify(db,b.user_id,f"Booking {b.reference} status changed to {data.status}.")
    db.commit(); db.refresh(b)
    await manager.broadcast({"type":"booking_updated","booking":booking_dict(b)})
    return booking_dict(b)

@router.get("/{booking_id}")
def get_booking(booking_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    b=db.query(Booking).options(joinedload(Booking.user),joinedload(Booking.hotel),joinedload(Booking.room),joinedload(Booking.review)).filter(Booking.id==booking_id).first()
    if not b: raise HTTPException(404,"Booking not found")
    if user.role!="admin" and b.user_id!=user.id: raise HTTPException(403,"Not your booking")
    return booking_dict(b)
