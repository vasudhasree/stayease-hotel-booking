from datetime import date
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from .models import Booking, Notification, Hotel

def booking_conflicts(db: Session, room_id: int, check_in: date, check_out: date, exclude_id=None):
    q = db.query(Booking).filter(
        Booking.room_id == room_id,
        Booking.status.in_(["Confirmed", "Checked-in"]),
        Booking.check_in < check_out,
        Booking.check_out > check_in,
    )
    if exclude_id:
        q = q.filter(Booking.id != exclude_id)
    return q.first()

def notify(db: Session, user_id: int, message: str):
    n = Notification(user_id=user_id, message=message)
    db.add(n)
    return n

def notify_admins(db: Session, message: str):
    for admin in db.query(__import__("app.models", fromlist=["User"]).User).filter_by(role="admin").all():
        notify(db, admin.id, message)

def recalc_rating(db: Session, hotel: Hotel):
    ratings = [r.rating for r in hotel.reviews]
    hotel.rating = round(sum(ratings) / len(ratings), 2) if ratings else 0
