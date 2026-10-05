from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine, SessionLocal
from .config import settings
from .seed import seed
from .routers import auth, hotels, bookings, reviews, notifications, users, admin, ws

app=FastAPI(title="StayEase Hotel Booking API",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.CORS_ORIGINS.split(",")],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(auth.router);app.include_router(hotels.router);app.include_router(bookings.router);app.include_router(reviews.router);app.include_router(notifications.router);app.include_router(users.router);app.include_router(admin.router);app.include_router(ws.router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    seed()

@app.get("/")
def root(): return {"message":"StayEase API is running","docs":"/docs"}

@app.get("/api/health")
def health(): return {"status":"ok"}
