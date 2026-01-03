import datetime
import os
import sys

# Ensure backend directory is in path for imports
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models, schemas, auth, database
from database import engine, get_db

app = FastAPI()
print("DEBUG: LOADING MAIN_V2.PY WITH BUDGET ENDPOINT")

@app.get("/ping")
def ping():
    return {"message": "pong"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTH ROUTES ---
@app.post("/auth/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.email).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

print("DEBUG: REGISTERING BUDGET ROUTE")
@app.get("/budget/{trip_id}")
def get_trip_budget(trip_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.owner_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    stops = db.query(models.Stop).filter(models.Stop.trip_id == trip_id).all()
    
    accommodation_total = sum(s.accommodation_cost for s in stops)
    transport_total = sum(s.transport_cost for s in stops)
    activities_total = 0.0
    
    for stop in stops:
        for activity in stop.activities:
            activities_total += activity.cost
            
    total_cost = accommodation_total + transport_total + activities_total
    
    # Calculate daily average
    daily_avg = 0.0
    if trip.start_date and trip.end_date:
        days = (trip.end_date - trip.start_date).days + 1
        if days > 0:
            daily_avg = total_cost / days
            
    return {
        "budget_limit": trip.budget_limit or 0.0,
        "total_cost": total_cost,
        "breakdown": {
            "accommodation": accommodation_total,
            "transport": transport_total,
            "activities": activities_total,
            "meals": 0.0 # Placeholder as meals are not tracked yet
        },
        "daily_average": daily_avg,
        "currency": "USD"
    }

# --- TRIP ROUTES ---
@app.get("/trips/", response_model=List[schemas.Trip])
def get_user_trips(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Trip).filter(models.Trip.owner_id == current_user.id).all()

@app.get("/trips/{trip_id}", response_model=schemas.Trip)
def get_trip(trip_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.owner_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@app.post("/trips/", response_model=schemas.Trip)
def create_trip(trip: schemas.TripCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_trip = models.Trip(**trip.model_dump(), owner_id=current_user.id)
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

@app.put("/trips/{trip_id}", response_model=schemas.Trip)
def update_trip(trip_id: int, trip: schemas.TripCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.owner_id == current_user.id).first()
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    update_data = trip.model_dump()
    for key, value in update_data.items():
        setattr(db_trip, key, value)
    
    db.commit()
    db.refresh(db_trip)
    return db_trip

@app.delete("/trips/{trip_id}")
def delete_trip(trip_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.owner_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(trip)
    db.commit()
    return {"detail": "Trip deleted"}

# --- ITINERARY ROUTES ---
@app.post("/trips/{trip_id}/stops", response_model=schemas.Stop)
def add_stop(trip_id: int, stop: schemas.StopCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.owner_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db_stop = models.Stop(**stop.model_dump(), trip_id=trip_id)
    db.add(db_stop)
    db.commit()
    db.refresh(db_stop)
    return db_stop

@app.post("/stops/{stop_id}/activities", response_model=schemas.Activity)
def add_activity(stop_id: int, activity: schemas.ActivityCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    stop = db.query(models.Stop).join(models.Trip).filter(models.Stop.id == stop_id, models.Trip.owner_id == current_user.id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    db_activity = models.Activity(**activity.model_dump(), stop_id=stop_id)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@app.put("/stops/{stop_id}", response_model=schemas.Stop)
def update_stop(stop_id: int, stop_update: schemas.StopUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    stop = db.query(models.Stop).join(models.Trip).filter(models.Stop.id == stop_id, models.Trip.owner_id == current_user.id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    
    for key, value in stop_update.model_dump().items():
        setattr(stop, key, value)
    
    db.commit()
    db.refresh(stop)
    return stop

@app.delete("/stops/{stop_id}")
def delete_stop(stop_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    stop = db.query(models.Stop).join(models.Trip).filter(models.Stop.id == stop_id, models.Trip.owner_id == current_user.id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    
    db.delete(stop)
    db.commit()
    return {"detail": "Stop deleted"}

@app.put("/activities/{activity_id}", response_model=schemas.Activity)
def update_activity(activity_id: int, activity_update: schemas.ActivityUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    activity = db.query(models.Activity).join(models.Stop).join(models.Trip).filter(models.Activity.id == activity_id, models.Trip.owner_id == current_user.id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    for key, value in activity_update.model_dump().items():
        setattr(activity, key, value)
    
    db.commit()
    db.refresh(activity)
    return activity

@app.delete("/activities/{activity_id}")
def delete_activity(activity_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    activity = db.query(models.Activity).join(models.Stop).join(models.Trip).filter(models.Activity.id == activity_id, models.Trip.owner_id == current_user.id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    db.delete(activity)
    db.commit()
    return {"detail": "Activity deleted"}

@app.post("/trips/{trip_id}/reorder_stops")
def reorder_stops(trip_id: int, reorder: schemas.StopReorder, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.owner_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    for index, stop_id in enumerate(reorder.stop_ids):
        stop = db.query(models.Stop).filter(models.Stop.id == stop_id, models.Stop.trip_id == trip_id).first()
        if stop:
            stop.sort_order = index
    
    db.commit()
    return {"detail": "Stops reordered"}


# --- SEARCH ROUTES ---
@app.get("/cities/search", response_model=List[schemas.City])
def search_cities(query: str = "", country: str = "", db: Session = Depends(get_db)):
    q = db.query(models.City)
    if query:
        q = q.filter(models.City.name.ilike(f"%{query}%"))
    if country:
        q = q.filter(models.City.country.ilike(f"%{country}%"))
    return q.all()

@app.get("/activities/search", response_model=List[schemas.CatalogActivity])
def search_activities(city_id: int = None, query: str = "", interest: str = "", cost_max: float = None, db: Session = Depends(get_db)):
    q = db.query(models.CatalogActivity)
    if city_id:
        q = q.filter(models.CatalogActivity.city_id == city_id)
    if query:
        q = q.filter(models.CatalogActivity.name.ilike(f"%{query}%") | models.CatalogActivity.description.ilike(f"%{query}%"))
    if interest:
        q = q.filter(models.CatalogActivity.category.ilike(f"%{interest}%"))
    if cost_max is not None:
        q = q.filter(models.CatalogActivity.cost <= cost_max)
    return q.all()

def seed_data(db: Session):
    if db.query(models.City).count() == 0:
        print("Seeding initial data...")
        cities = [
            models.City(name="Paris", country="France", description="The city of light.", image_url="https://images.unsplash.com/photo-1511739001486-da0fc87b5a1b", cost_index=1.2, popularity=95),
            models.City(name="Tokyo", country="Japan", description="A neon-lit wonder.", image_url="https://images.unsplash.com/photo-1540959733332-eab4deabeeaf", cost_index=1.3, popularity=90),
            models.City(name="Bali", country="Indonesia", description="Tropical paradise.", image_url="https://images.unsplash.com/photo-1537996194471-e657df975ab4", cost_index=0.8, popularity=88),
            models.City(name="Rome", country="Italy", description="Eternal city.", image_url="https://images.unsplash.com/photo-1531572753322-ad063cecc140", cost_index=1.1, popularity=92),
            models.City(name="New York", country="USA", description="The Big Apple.", image_url="https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9", cost_index=1.5, popularity=94)
        ]
        db.add_all(cities)
        db.commit()
        
        # We need IDs, so refresh or query back. Simplified by just querying back or using object reference after commit (if supported well by session, usually need refresh)
        # Let's iterate and add activities
        for city in cities:
            db.refresh(city)
            if city.name == "Paris":
                db.add_all([
                    models.CatalogActivity(city_id=city.id, name="Eiffel Tower Tour", category="Sightseeing", cost=25.0, duration="2 hours", description="Visit the iconic tower.", image_url=""),
                    models.CatalogActivity(city_id=city.id, name="Louvre Museum", category="Art", cost=17.0, duration="4 hours", description="Home of the Mona Lisa.", image_url=""),
                    models.CatalogActivity(city_id=city.id, name="Croissant Baking Class", category="Food", cost=90.0, duration="3 hours", description="Learn to make croissants.", image_url="")
                ])
            elif city.name == "Tokyo":
                 db.add_all([
                    models.CatalogActivity(city_id=city.id, name="Sushi Making", category="Food", cost=80.0, duration="2 hours", description="Master sushi arts.", image_url=""),
                    models.CatalogActivity(city_id=city.id, name="Shibuya Crossing", category="Sightseeing", cost=0.0, duration="1 hour", description="Famous crossing.", image_url="")
                ])
        db.commit()
        print("Seeding complete.")

@app.get("/dashboard/data", response_model=schemas.DashboardData)
def get_dashboard_info(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    upcoming_trip = db.query(models.Trip).filter(models.Trip.owner_id == current_user.id, models.Trip.status == "upcoming").first()
    recent_trips = db.query(models.Trip).filter(models.Trip.owner_id == current_user.id).limit(5).all()
    
    recommendations = [
        {"city": "Reykjavik", "country": "Iceland", "price_from": 450, "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuC6GJgLZY4kyXAYASsKn277Ps-oRz1gH1edcnoSsSHRqVL8P2vKbFO1GfRiAHhhcYn2FS5UPtBlxjiDsszJKS4yxrsH7mr8rIzv18Jx-Bei0x-NoCn3g6qAb6yZexcvJx-YY-Jbd7MM2Wx3F485723CE_hO7Xp--tAKcLh_lHoX6K9n-h7nqWrgqShdJ28_6KOeMhU4Qz15u6QsvYE3bv4o6_4lrILnWlGyV1gK419XuaNOYuznIuqGcFYqcAdmWkYz5cEMLN6zzUap"},
        {"city": "Kyoto", "country": "Japan", "price_from": 820, "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuDxz9BBVOv6etnYJDXVwiRxtvgjfVRRz12N2KAHy6FCcNkULmmoncg7oCuPmMpZgkERSTtu8bk-c8bDAIwIwDKDepxm1Z8UFHADT0fWz6EFbNhBKXynVXWQbFMOzHf5ZqrfcsbmNIDSzOQYtDHcS50-OLNCLFxbyQK87HO4L5oLWrZtsD1YRDu0CKxKtxYDpDH-XCCV0WNqZ8bWQhmKYZf-9us7WIjKfaUwwyYhBHSslu3YiFDy2FVolHRL74BX0W4M6xOdJIdX7XB6"},
        {"city": "Paris", "country": "France", "price_from": 620, "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuAFJH8PAUCCRJ2nvhZYuiutdLeK_ukmLK5rF6mwRYlRVqOxQNMi7P8YMRHt-b8b5v6sbWH50udWNnasbLgL84oxURJnOtp-1gAtaX1_GXESra6Q4FGfKTW9EzTG1Ojeu4vwgKh2WMiFodC6ZCBNPwb0xPEicv_Lai60oWPa1eoF7eCfkfQ_vuVfkIKHWIt6QpHZz0hGYnKftfEB2GMgk49jlIdK1jT2U_Q_RCsn-Nfwy8SUU9WYbNzj3wbA2aSEJjEUkR2gGwTHGR-W"},
        {"city": "Bali", "country": "Indonesia", "price_from": 380, "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuCBSDIOqyW7ATjFUseJt5QifrMdpgvzq3D_80diDbfVH9Zlao8DJO3yLogI8o-yr8lp6aY4sMkYUW014lCWR5y2eZfONFLdrjv6NqEnSsZs3mPdsp_-MpZfZOFEgb3iLzX91u9EauIU492pHhdOTg3LpCUwnhC8ZcHNvWO7g8btuwB4EOeCdmkaFbVcu7tPgZaA_jtHwjyXRLqmdeiNRpsUCupr4ZVRl_OLstPjvcHj2LRDLICQ-cADXpBUmoivc5gbmBpuonIE8WTM"}
    ]
    
    return {
        "full_name": current_user.full_name,
        "upcoming_trip": upcoming_trip,
        "recent_trips": recent_trips,
        "recommendations": recommendations
    }

if __name__ == "__main__":
    import uvicorn
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    
    # Seed Data
    from database import SessionLocal
    db = SessionLocal()
    seed_data(db)
    db.close()
    
    print("Starting server on http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
