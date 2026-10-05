from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserOut(BaseModel):
    id: int; name: str; email: EmailStr; role: str
    model_config = ConfigDict(from_attributes=True)

class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6)

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class HotelBase(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    city: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=20)
    image_url: Optional[str] = None
    rating: float = Field(default=0, ge=0, le=5)
    is_active: bool = True

class HotelCreate(HotelBase): pass
class HotelUpdate(HotelBase): pass

class RoomBase(BaseModel):
    number: str
    type: str
    price: float = Field(gt=0)
    capacity: int = Field(gt=0, le=20)
    amenities: List[str] = []
    is_active: bool = True

class RoomCreate(RoomBase):
    hotel_id: int
class RoomUpdate(RoomBase): pass

class BookingCreate(BaseModel):
    room_id: int
    check_in: date
    check_out: date

class BookingStatusUpdate(BaseModel):
    status: str

class ReviewCreate(BaseModel):
    booking_id: int
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=10, max_length=2000)

class ReviewReply(BaseModel):
    reply: str = Field(min_length=1, max_length=2000)

class ProfileUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)

class NotificationOut(BaseModel):
    id: int; message: str; is_read: bool; created_at: datetime
    model_config = ConfigDict(from_attributes=True)
