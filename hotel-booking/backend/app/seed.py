from datetime import date, timedelta, datetime
from .database import Base, engine, SessionLocal
from .models import User, Hotel, Room, Review, Booking
from .auth import hash_password


HOTELS = [
    ("Aurora Grand", "Hyderabad", "A polished city hotel with skyline views, quiet rooms and a rooftop lounge."),
    ("Palm Grove Retreat", "Goa", "A tropical retreat close to the beach with lush gardens and relaxed suites."),
    ("The Sapphire Residency", "Bengaluru", "Modern business-friendly rooms near technology hubs, cafes and shopping."),
    ("Heritage Courtyard", "Jaipur", "A warm heritage stay blending traditional architecture with contemporary comfort."),
    ("Lakeview Crest", "Udaipur", "A serene lakeside escape with elegant rooms and sunset dining."),
    ("Cedar Park Suites", "Delhi", "A refined urban stay with spacious suites, a fitness studio and fast Wi-Fi."),
    ("Coastal Pearl", "Chennai", "Comfortable coastal accommodation with local cuisine and family-friendly rooms."),
    ("Misty Pines Resort", "Ooty", "A cool hill-station retreat surrounded by pine forests and scenic trails."),
    ("Riverstone Palace", "Kolkata", "Classic hospitality, spacious rooms and easy access to cultural landmarks."),
    ("Marigold Heights", "Pune", "A contemporary hotel designed for business trips, weekends and celebrations."),
    ("Royal Deccan", "Nashik", "Elegant rooms near vineyards, with a calm courtyard and regional dining."),
    ("Blue Horizon Inn", "Visakhapatnam", "A bright seaside stay with practical rooms and quick beach access."),
    ("Maple Leaf Residency", "Mysuru", "A peaceful base for palace visits, family trips and local sightseeing."),
    ("Golden Fort Hotel", "Jodhpur", "A distinctive stay with fort views, artisan decor and rooftop breakfasts."),
    ("Green Valley Lodge", "Manali", "A cozy mountain lodge with warm interiors, balconies and valley views."),
    ("Coral Bay Resort", "Kochi", "A stylish waterfront stay with easy access to heritage streets and ferries."),
    ("Silver Oak Hotel", "Ahmedabad", "A smart, comfortable property close to business districts and restaurants."),
    ("Lotus Crown Palace", "Lucknow", "Graceful interiors, generous rooms and easy access to the old city."),
    ("Sunrise Meadows", "Coorg", "A peaceful plantation-side retreat with nature walks and spacious suites."),
    ("Urban Nest Central", "Mumbai", "A compact premium city stay near transit, dining and major attractions."),
]

IMAGE_IDS = [
    "1566073771259-6a8506099945",
    "1551882547-ff40c63fe5fa",
    "1578683010236-d716f9a3f461",
    "1564501049412-61c2a3083791",
    "1584132967334-10e028bd69f7",
    "1566665797739-1674de7a421a",
    "1582719478250-c89cae4dc85b",
    "1571896349842-33c89424de2d",
    "1590490360182-c33d57733427",
    "1542314831-068cd1dbfeeb",
    "1584132967334-10e028bd69f7",
    "1566665797739-1674de7a421a",
    "1571003123894-1f0594d2b5d9",
    "1559599101-1b4b3f9b2f1a",
    "1505693416388-ac5ce068fe85",
    "1512918728675-ed5a9ae0b5f5",
    "1564501049412-61c2a3083791",
    "1554995207-c18c203602cb",
    "1510798831973-3e5a4e0a8a9d",
    "1505693416388-ac5ce068fe85",
]

COMMENTS = {
    "Good": [
        "Beautiful room and very comfortable bed.",
        "The staff were warm, helpful and professional.",
        "Excellent location and a peaceful stay.",
        "Clean room, quick service and a lovely breakfast.",
    ],
    "Medium": [
        "The stay was comfortable but could be quieter.",
        "Good location, though some facilities felt basic.",
        "Room was fine and the service was average.",
        "A decent stay with a few areas that need improvement.",
    ],
    "Bad": [
        "The room needed better maintenance and cleaning.",
        "Service was slower than expected during our stay.",
        "The experience did not match the price we paid.",
        "Noise and delayed service made the stay disappointing.",
    ],
}


def seed():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        if db.query(User).first():
            return

        users = [
            User(
                name="StayEase Admin",
                email="admin@stayease.com",
                password_hash=hash_password("Admin@123"),
                role="admin",
            ),
            User(
                name="Demo Customer",
                email="customer@stayease.com",
                password_hash=hash_password("Customer@123"),
                role="customer",
            ),
        ]

        for i in range(4):
            users.append(
                User(
                    name=f"Sample Customer {i + 1}",
                    email=f"sample{i + 1}@stayease.com",
                    password_hash=hash_password(f"Sample@{i + 1}23"),
                    role="customer",
                )
            )

        db.add_all(users)
        db.flush()

        for idx, (name, city, desc) in enumerate(HOTELS, 1):

            h = Hotel(
                name=name,
                city=city,
                description=desc,
                image_url=f"https://images.unsplash.com/photo-{IMAGE_IDS[idx - 1]}?auto=format&fit=crop&w=1200&q=80",
                rating=0,
                is_active=True,
            )

            db.add(h)
            db.flush()

            rooms = []

            for n in range(1, 21):

                typ = (
                    "BIG"
                    if n <= 10
                    else "MEDIUM"
                    if n <= 15
                    else "SMALL"
                )

                price = {
                    "BIG": 8500 + idx * 150,
                    "MEDIUM": 5200 + idx * 90,
                    "SMALL": 3200 + idx * 60,
                }[typ]

                capacity = {
                    "BIG": 4,
                    "MEDIUM": 3,
                    "SMALL": 2,
                }[typ]

                amenities = {
                    "BIG": "King bed,Living area,Bathtub,City view,Wi-Fi",
                    "MEDIUM": "Queen bed,Work desk,Wi-Fi,TV,Mini fridge",
                    "SMALL": "Double bed,Wi-Fi,TV,Tea maker",
                }[typ]

                rooms.append(
                    Room(
                        hotel_id=h.id,
                        number=f"{100 + idx}{n:02d}",
                        type=typ,
                        price=price,
                        capacity=capacity,
                        amenities=amenities,
                        is_active=True,
                    )
                )

            db.add_all(rooms)
            db.flush()

            ratings = [5, 4, 5, 3, 4, 2, 1, 3]

            for j, rating in enumerate(ratings):

                category = (
                    "Good"
                    if rating >= 4
                    else "Medium"
                    if rating == 3
                    else "Bad"
                )

                reviewer = users[(j + 1) % len(users)]

                db.add(
                    Review(
                        hotel_id=h.id,
                        user_id=reviewer.id,
                        booking_id=None,
                        user_name=reviewer.name,
                        rating=rating,
                        comment=COMMENTS[category][j % 4],
                        category=category,
                        created_at=datetime.utcnow()
                        - timedelta(days=idx + j),
                    )
                )

            h.rating = sum(ratings) / len(ratings)

        db.commit()

        hotels = db.query(Hotel).all()

        # Demo bookings
        examples = [
            (0, 0, 0, 1, "Checked-out"),
            (1, 10, 1, 2, "Checked-in"),
            (2, 5, 3, 4, "Confirmed"),
            (3, 16, 2, 3, "Confirmed"),
            (4, 12, 4, 6, "Cancelled"),
        ]

        for hotel_i, room_i, user_i, offset, status in examples:

            h = hotels[hotel_i]
            room = h.rooms[room_i]

            check_in = date.today() + timedelta(days=offset)
            check_out = check_in + timedelta(days=2)

            booking = Booking(
                reference=f"SE-{date.today().year}-{100 + hotel_i:05d}",
                user_id=users[user_i + 1].id,
                hotel_id=h.id,
                room_id=room.id,
                check_in=check_in,
                check_out=check_out,
                total_price=room.price * 2,
                status=status,
            )

            db.add(booking)

        db.commit()

    finally:
        db.close()