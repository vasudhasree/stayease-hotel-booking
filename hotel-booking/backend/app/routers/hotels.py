from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..database import get_db
from ..models import Hotel, Room, Booking, Review
from ..schemas import HotelCreate, HotelUpdate, RoomCreate, RoomUpdate
from ..auth import require_role

router = APIRouter(prefix="/api/hotels", tags=["Hotels"])

def room_dict(r):
    return {"id":r.id,"hotel_id":r.hotel_id,"number":r.number,"type":r.type,"price":r.price,"capacity":r.capacity,"amenities":[x for x in r.amenities.split(",") if x],"is_active":r.is_active}

def hotel_dict(h, include_rooms=False):
    data={"id":h.id,"name":h.name,"city":h.city,"description":h.description,"image_url":h.image_url,"rating":round(h.rating or 0,2),"is_active":h.is_active}
    if include_rooms: data["rooms"]=[room_dict(r) for r in h.rooms if r.is_active]
    return data

@router.get("/admin/all")
def admin_all_hotels(db:Session=Depends(get_db),user=Depends(require_role("admin"))):
    return [hotel_dict(h)|{"starting_price":min((r.price for r in h.rooms if r.is_active),default=0),"room_count":len(h.rooms),"is_active":h.is_active} for h in db.query(Hotel).order_by(Hotel.id).all()]

@router.get("")
def list_hotels(search:str="",city:str="",sort:str="rating",db:Session=Depends(get_db)):
    q=db.query(Hotel).filter(Hotel.is_active==True)
    if search:q=q.filter(or_(Hotel.name.ilike(f"%{search}%"),Hotel.city.ilike(f"%{search}%")))
    if city:q=q.filter(Hotel.city==city)
    hotels=q.all()
    if sort=="price":hotels.sort(key=lambda h:min((r.price for r in h.rooms if r.is_active),default=10**9))
    elif sort=="name":hotels.sort(key=lambda h:h.name.lower())
    else:hotels.sort(key=lambda h:h.rating or 0,reverse=True)
    return [hotel_dict(h)|{"starting_price":min((r.price for r in h.rooms if r.is_active),default=0)} for h in hotels]

@router.get("/cities")
def cities(db:Session=Depends(get_db)): return sorted({h.city for h in db.query(Hotel).filter(Hotel.is_active==True).all()})

@router.post("",dependencies=[Depends(require_role("admin"))],status_code=201)
def create_hotel(data:HotelCreate,db:Session=Depends(get_db)):
    h=Hotel(**data.model_dump());db.add(h);db.commit();db.refresh(h);return hotel_dict(h)

@router.put("/{hotel_id}",dependencies=[Depends(require_role("admin"))])
def update_hotel(hotel_id:int,data:HotelUpdate,db:Session=Depends(get_db)):
    h=db.get(Hotel,hotel_id)
    if not h:raise HTTPException(404,"Hotel not found")
    for k,v in data.model_dump().items():setattr(h,k,v)
    db.commit();db.refresh(h);return hotel_dict(h)

@router.post("/{hotel_id}/activate",dependencies=[Depends(require_role("admin"))])
def activate_hotel(hotel_id:int,db:Session=Depends(get_db)):
    h=db.get(Hotel,hotel_id)
    if not h:raise HTTPException(404,"Hotel not found")
    h.is_active=True;db.commit();return hotel_dict(h)

@router.post("/{hotel_id}/deactivate",dependencies=[Depends(require_role("admin"))])
def deactivate_hotel(hotel_id:int,db:Session=Depends(get_db)):
    h=db.get(Hotel,hotel_id)
    if not h:raise HTTPException(404,"Hotel not found")
    h.is_active=False;db.commit();return hotel_dict(h)

@router.delete("/{hotel_id}",dependencies=[Depends(require_role("admin"))])
def delete_hotel(hotel_id:int,db:Session=Depends(get_db)):
    h=db.get(Hotel,hotel_id)
    if not h:raise HTTPException(404,"Hotel not found")
    if h.bookings: raise HTTPException(409,"This hotel has booking history; deactivate it instead of deleting it")
    db.delete(h);db.commit();return {"message":"Hotel deleted"}

@router.post("/rooms",dependencies=[Depends(require_role("admin"))],status_code=201)
def create_room(data:RoomCreate,db:Session=Depends(get_db)):
    if not db.get(Hotel,data.hotel_id):raise HTTPException(404,"Hotel not found")
    r=Room(hotel_id=data.hotel_id,number=data.number,type=data.type.upper(),price=data.price,capacity=data.capacity,amenities=",".join(data.amenities),is_active=data.is_active)
    db.add(r);db.commit();db.refresh(r);return room_dict(r)

@router.put("/rooms/{room_id}",dependencies=[Depends(require_role("admin"))])
def update_room(room_id:int,data:RoomUpdate,db:Session=Depends(get_db)):
    r=db.get(Room,room_id)
    if not r:raise HTTPException(404,"Room not found")
    for k,v in data.model_dump().items():setattr(r,k,",".join(v) if k=="amenities" else (v.upper() if k=="type" else v))
    db.commit();db.refresh(r);return room_dict(r)

@router.post("/rooms/{room_id}/activate",dependencies=[Depends(require_role("admin"))])
def activate_room(room_id:int,db:Session=Depends(get_db)):
    r=db.get(Room,room_id)
    if not r:raise HTTPException(404,"Room not found")
    r.is_active=True;db.commit();return room_dict(r)

@router.post("/rooms/{room_id}/deactivate",dependencies=[Depends(require_role("admin"))])
def deactivate_room(room_id:int,db:Session=Depends(get_db)):
    r=db.get(Room,room_id)
    if not r:raise HTTPException(404,"Room not found")
    r.is_active=False;db.commit();return room_dict(r)

@router.delete("/rooms/{room_id}",dependencies=[Depends(require_role("admin"))])
def delete_room(room_id:int,db:Session=Depends(get_db)):
    r=db.get(Room,room_id)
    if not r:raise HTTPException(404,"Room not found")
    if r.bookings: raise HTTPException(409,"This room has booking history; deactivate it instead of deleting it")
    db.delete(r);db.commit();return {"message":"Room deleted"}

@router.get("/{hotel_id}")
def get_hotel(hotel_id:int,check_in:date|None=None,check_out:date|None=None,db:Session=Depends(get_db)):
    h=db.get(Hotel,hotel_id)
    if not h or not h.is_active:raise HTTPException(404,"Hotel not found")
    rooms=[]
    for r in h.rooms:
        if not r.is_active:continue
        available=True
        if check_in and check_out:
            available=db.query(Booking).filter(Booking.room_id==r.id,Booking.status.in_(["Confirmed","Checked-in"]),Booking.check_in<check_out,Booking.check_out>check_in).first() is None
        rooms.append(room_dict(r)|{"available":available})
    return hotel_dict(h)|{"rooms":rooms}

@router.get("/{hotel_id}/reviews")
def get_reviews(hotel_id:int,sort:str="newest",db:Session=Depends(get_db)):
    h=db.get(Hotel,hotel_id)
    if not h:raise HTTPException(404,"Hotel not found")
    reviews=db.query(Review).filter(Review.hotel_id==hotel_id).all()
    reviews.sort(key=(lambda r:r.rating) if sort=="rating" else (lambda r:r.created_at),reverse=True)
    groups={"Good":[],"Medium":[],"Bad":[]}
    for r in reviews:groups[r.category].append({"id":r.id,"user_name":r.user_name,"rating":r.rating,"comment":r.comment,"admin_reply":r.admin_reply,"created_at":r.created_at})
    return {"hotel_id":hotel_id,"average_rating":round(h.rating or 0,2),"count":len(reviews),"breakdown":{str(i):sum(1 for r in reviews if r.rating==i) for i in range(1,6)},"groups":groups}
