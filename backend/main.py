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

<<<<<<< HEAD
app = FastAPI()
print("DEBUG: LOADING MAIN.PY WITH BUDGET ENDPOINT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
=======
app = FastAPI(title="GlobeTrotter")
print("DEBUG: LOADING MAIN.PY WITH BUDGET ENDPOINT")

# Create database tables at import time (important for uvicorn)
models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:8000", 
        "http://127.0.0.1:8000",
        "http://localhost:5500",  # Common Live Server port
        "http://127.0.0.1:5500",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
>>>>>>> b1b02e3c0d2006fd00e882c768604aa877c20d20
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



# --- ENHANCED BUDGET ROUTES ---
@app.get("/budget/{trip_id}", response_model=schemas.BudgetSummary)
def get_trip_budget(trip_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.owner_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    stops = db.query(models.Stop).filter(models.Stop.trip_id == trip_id).all()
    expenses = db.query(models.Expense).filter(models.Expense.trip_id == trip_id).all()
    
    # Calculate breakdown by category
    breakdown = {
        "transport": 0.0,
        "stay": 0.0,
        "food": 0.0,
        "activities": 0.0,
        "other": 0.0
    }
    
    # Add costs from stops
    for stop in stops:
        breakdown["stay"] += stop.accommodation_cost
        breakdown["transport"] += stop.transport_cost
        for activity in stop.activities:
            breakdown["activities"] += activity.cost
    
    # Add costs from expenses
    for expense in expenses:
        category = expense.category.lower()
        if category in breakdown:
            breakdown[category] += expense.amount
        else:
            breakdown["other"] += expense.amount
    
    total_cost = sum(breakdown.values())
    budget_limit = trip.budget_limit or 0.0
    remaining = budget_limit - total_cost
    utilization_percentage = (total_cost / budget_limit * 100) if budget_limit > 0 else 0
    
    # Calculate daily average
    daily_avg = 0.0
    daily_target = 0.0
    if trip.start_date and trip.end_date:
        days = (trip.end_date - trip.start_date).days + 1
        if days > 0:
            daily_avg = total_cost / days
            daily_target = budget_limit / days if budget_limit > 0 else 0
    
    # Generate alerts
    alerts = []
    for category, amount in breakdown.items():
        if category != "other" and budget_limit > 0:
            # Assume each category should be roughly 25% of budget (simplified)
            category_limit = budget_limit * 0.25
            category_percentage = (amount / category_limit * 100) if category_limit > 0 else 0
            
            if category_percentage >= 85:
                alerts.append({
                    "type": "warning" if category_percentage < 100 else "danger",
                    "category": category,
                    "message": f"{category.capitalize()} category is {int(category_percentage)}% full",
                    "percentage": category_percentage
                })
    
    # Overall budget alert
    if utilization_percentage >= 90:
        alerts.append({
            "type": "danger",
            "category": "overall",
            "message": f"You've used {int(utilization_percentage)}% of your total budget",
            "percentage": utilization_percentage
        })
    
    return {
        "budget_limit": budget_limit,
        "total_cost": total_cost,
        "remaining": remaining,
        "utilization_percentage": utilization_percentage,
        "breakdown": breakdown,
        "daily_average": daily_avg,
        "daily_target": daily_target,
        "currency": "USD",
        "alerts": alerts
    }

@app.get("/budget/{trip_id}/daily-trend", response_model=schemas.DailyTrendResponse)
def get_daily_trend(trip_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.owner_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if not trip.start_date or not trip.end_date:
        raise HTTPException(status_code=400, detail="Trip must have start and end dates")
    
    # Get all expenses
    expenses = db.query(models.Expense).filter(models.Expense.trip_id == trip_id).all()
    
    # Calculate daily budget limit
    days = (trip.end_date - trip.start_date).days + 1
    budget_limit_per_day = (trip.budget_limit / days) if trip.budget_limit and days > 0 else 0
    
    # Group expenses by date
    daily_data = {}
    current_date = trip.start_date.date()
    end_date = trip.end_date.date()
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        daily_data[date_str] = {
            "date": date_str,
            "total": 0.0,
            "breakdown": {
                "transport": 0.0,
                "stay": 0.0,
                "food": 0.0,
                "activities": 0.0,
                "other": 0.0
            },
            "over_budget": False
        }
        current_date += datetime.timedelta(days=1)
    
    # Add expense data
    for expense in expenses:
        expense_date = expense.date.strftime("%Y-%m-%d")
        if expense_date in daily_data:
            category = expense.category.lower()
            if category in daily_data[expense_date]["breakdown"]:
                daily_data[expense_date]["breakdown"][category] += expense.amount
            else:
                daily_data[expense_date]["breakdown"]["other"] += expense.amount
            daily_data[expense_date]["total"] += expense.amount
    
    # Check if over budget
    for date_str, data in daily_data.items():
        data["over_budget"] = data["total"] > budget_limit_per_day if budget_limit_per_day > 0 else False
    
    return {
        "days": list(daily_data.values()),
        "budget_limit_per_day": budget_limit_per_day
    }

# --- EXPENSE ROUTES ---
@app.get("/trips/{trip_id}/expenses", response_model=List[schemas.Expense])
def get_trip_expenses(
    trip_id: int,
    category: str = None,
    start_date: datetime.datetime = None,
    end_date: datetime.datetime = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.owner_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    query = db.query(models.Expense).filter(models.Expense.trip_id == trip_id)
    
    if category:
        query = query.filter(models.Expense.category == category)
    if start_date:
        query = query.filter(models.Expense.date >= start_date)
    if end_date:
        query = query.filter(models.Expense.date <= end_date)
    
    return query.all()

@app.post("/trips/{trip_id}/expenses", response_model=schemas.Expense)
def create_expense(
    trip_id: int,
    expense: schemas.ExpenseCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.owner_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    db_expense = models.Expense(**expense.model_dump(), trip_id=trip_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@app.put("/expenses/{expense_id}", response_model=schemas.Expense)
def update_expense(
    expense_id: int,
    expense_update: schemas.ExpenseUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    expense = db.query(models.Expense).join(models.Trip).filter(
        models.Expense.id == expense_id,
        models.Trip.owner_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    update_data = expense_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(expense, key, value)
    
    db.commit()
    db.refresh(expense)
    return expense

@app.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    expense = db.query(models.Expense).join(models.Trip).filter(
        models.Expense.id == expense_id,
        models.Trip.owner_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(expense)
    db.commit()
    return {"detail": "Expense deleted"}

# --- TIMELINE & CALENDAR ROUTES ---
@app.get("/trips/{trip_id}/timeline", response_model=schemas.TripTimeline)
def get_trip_timeline(
    trip_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.owner_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if not trip.start_date or not trip.end_date:
        raise HTTPException(status_code=400, detail="Trip must have start and end dates")
    
    stops = db.query(models.Stop).filter(models.Stop.trip_id == trip_id).order_by(models.Stop.sort_order).all()
    
    # Organize activities by day
    days_data = []
    current_date = trip.start_date.date()
    end_date = trip.end_date.date()
    day_number = 1
    
    while current_date <= end_date:
        day_activities = []
        day_stops = []
        
        # Find stops for this day
        for stop in stops:
            stop_arrival = stop.arrival_date.date()
            stop_departure = stop.departure_date.date()
            
            if stop_arrival <= current_date <= stop_departure:
                day_stops.append(stop)
                
                # Get activities for this stop on this day
                for activity in sorted(stop.activities, key=lambda a: a.id):
                    # Simple categorization based on description keywords
                    category = "other"
                    desc_lower = activity.description.lower()
                    if any(word in desc_lower for word in ["flight", "train", "bus", "taxi", "transport"]):
                        category = "transport"
                    elif any(word in desc_lower for word in ["hotel", "check-in", "accommodation", "stay"]):
                        category = "accommodation"
                    elif any(word in desc_lower for word in ["lunch", "dinner", "breakfast", "restaurant", "food"]):
                        category = "food"
                    elif any(word in desc_lower for word in ["museum", "tour", "visit", "sightseeing"]):
                        category = "sightseeing"
                    
                    day_activities.append({
                        "id": activity.id,
                        "description": activity.description,
                        "time": activity.time,
                        "duration": None,  # Could be extracted from description
                        "cost": activity.cost,
                        "category": category,
                        "sort_order": activity.id
                    })
        
        # Generate day title
        day_title = f"Day {day_number}"
        if day_stops:
            day_title += f": {day_stops[0].city_name}"
        
        days_data.append({
            "day_number": day_number,
            "date": current_date.strftime("%Y-%m-%d"),
            "title": day_title,
            "stops": day_stops,
            "activities": day_activities
        })
        
        current_date += datetime.timedelta(days=1)
        day_number += 1
    
    return {
        "trip_id": trip.id,
        "title": trip.title,
        "start_date": trip.start_date.strftime("%Y-%m-%d"),
        "end_date": trip.end_date.strftime("%Y-%m-%d"),
        "days": days_data
    }

@app.get("/trips/{trip_id}/calendar", response_model=schemas.CalendarResponse)
def get_trip_calendar(
    trip_id: int,
    month: str = None,  # Format: YYYY-MM
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.owner_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if not trip.start_date or not trip.end_date:
        raise HTTPException(status_code=400, detail="Trip must have start and end dates")
    
    # Determine which month to show
    if month:
        try:
            year, month_num = map(int, month.split("-"))
            start_of_month = datetime.date(year, month_num, 1)
        except:
            raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM")
    else:
        start_of_month = trip.start_date.date().replace(day=1)
    
    # Get last day of month
    if start_of_month.month == 12:
        end_of_month = datetime.date(start_of_month.year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        end_of_month = datetime.date(start_of_month.year, start_of_month.month + 1, 1) - datetime.timedelta(days=1)
    
    # Get all activities for the trip
    stops = db.query(models.Stop).filter(models.Stop.trip_id == trip_id).all()
    activity_counts = {}
    
    for stop in stops:
        for activity in stop.activities:
            # Assume activities happen on the stop's arrival date if no specific time
            activity_date = stop.arrival_date.date()
            date_str = activity_date.strftime("%Y-%m-%d")
            activity_counts[date_str] = activity_counts.get(date_str, 0) + 1
    
    # Build calendar days
    calendar_days = []
    current_date = start_of_month
    trip_start = trip.start_date.date()
    trip_end = trip.end_date.date()
    
    while current_date <= end_of_month:
        date_str = current_date.strftime("%Y-%m-%d")
        is_trip_day = trip_start <= current_date <= trip_end
        activity_count = activity_counts.get(date_str, 0)
        
        calendar_days.append({
            "date": date_str,
            "activity_count": activity_count,
            "has_activities": activity_count > 0,
            "is_trip_day": is_trip_day
        })
        
        current_date += datetime.timedelta(days=1)
    
    return {
        "month": start_of_month.strftime("%Y-%m"),
        "days": calendar_days
    }

@app.post("/stops/{stop_id}/reorder_activities")
def reorder_activities(
    stop_id: int,
    reorder: schemas.ActivityReorder,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    stop = db.query(models.Stop).join(models.Trip).filter(
        models.Stop.id == stop_id,
        models.Trip.owner_id == current_user.id
    ).first()
    
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    
    # Update sort order (using id as proxy for sort_order since Activity doesn't have sort_order field)
    # In a real implementation, you'd add a sort_order field to Activity model
    return {"detail": "Activity reordering not yet implemented - requires sort_order field in Activity model"}

@app.put("/activities/{activity_id}/time")
def update_activity_time(
    activity_id: int,
    time_update: schemas.ActivityTimeUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    activity = db.query(models.Activity).join(models.Stop).join(models.Trip).filter(
        models.Activity.id == activity_id,
        models.Trip.owner_id == current_user.id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Update time (and duration if provided)
    activity.time = time_update.time
    if time_update.duration:
        # Could store duration in description or add a duration field
        pass
    
    db.commit()
    db.refresh(activity)
    return activity



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

# --- SHARED ITINERARY ROUTES ---
@app.post("/trips/{trip_id}/share", response_model=schemas.ShareTokenResponse)
def share_trip(trip_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.owner_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    import uuid
    if not trip.is_public:
        trip.is_public = 1
        trip.share_token = str(uuid.uuid4())
        db.commit()
        db.refresh(trip)
    elif not trip.share_token: # Should not happen if is_public is true, but safe guard
        trip.share_token = str(uuid.uuid4())
        db.commit()
        db.refresh(trip)
        
    return {"share_url": f"/trips/public/{trip.share_token}", "token": trip.share_token}

@app.delete("/trips/{trip_id}/share")
def unshare_trip(trip_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.owner_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    trip.is_public = 0
    trip.share_token = None
    db.commit()
    return {"detail": "Trip unshared successfully"}

@app.get("/trips/public/{share_token}", response_model=schemas.TripPublic)
def get_public_trip(share_token: str, db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.share_token == share_token, models.Trip.is_public == 1).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found or not public")
    
    # Construct response manually or rely on Pydantic to extract relation fields if mapped correctly.
    # TripPublic schema expects 'owner_name' and 'owner_image'. 
    # We need to ensure we pass an object that has these attributes or use a dict.
    
    response_data = {
        "id": trip.id,
        "destination": trip.destination,
        "title": trip.title,
        "description": trip.description,
        "start_date": trip.start_date,
        "end_date": trip.end_date,
        "completion_percentage": trip.completion_percentage,
        "cost_from": trip.cost_from,
        "budget_limit": trip.budget_limit,
        "cover_image_url": trip.cover_image_url,
        "status": trip.status,
        "owner_name": trip.owner.full_name,
        "owner_image": trip.owner.profile_image_url,
        "stops": trip.stops
    }
    return response_data

@app.post("/trips/public/{share_token}/copy", response_model=schemas.Trip)
def copy_trip(share_token: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    original_trip = db.query(models.Trip).filter(models.Trip.share_token == share_token, models.Trip.is_public == 1).first()
    if not original_trip:
        raise HTTPException(status_code=404, detail="Trip not found or not public")
    
    # 1. Create new trip
    new_trip = models.Trip(
        destination=original_trip.destination,
        title=f"Copy of {original_trip.title}",
        description=original_trip.description,
        start_date=datetime.now(), # Reset dates or keep? Usually reset for planning
        end_date=datetime.now() + (original_trip.end_date - original_trip.start_date),
        budget_limit=original_trip.budget_limit,
        cover_image_url=original_trip.cover_image_url,
        status="planning",
        owner_id=current_user.id
    )
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    
    # 2. Copy Stops and Activities
    for original_stop in original_trip.stops:
        # Calculate offset days for new dates
        days_offset = (original_stop.arrival_date - original_trip.start_date).days
        duration_days = (original_stop.departure_date - original_stop.arrival_date).days
        
        new_arrival = new_trip.start_date + datetime.timedelta(days=days_offset)
        new_departure = new_arrival + datetime.timedelta(days=duration_days)
        
        new_stop = models.Stop(
            trip_id=new_trip.id,
            city_name=original_stop.city_name,
            arrival_date=new_arrival,
            departure_date=new_departure,
            sort_order=original_stop.sort_order,
            accommodation_cost=original_stop.accommodation_cost,
            transport_cost=original_stop.transport_cost
        )
        db.add(new_stop)
        db.commit()
        db.refresh(new_stop)
        
        for original_activity in original_stop.activities:
            new_activity = models.Activity(
                stop_id=new_stop.id,
                description=original_activity.description,
                time=original_activity.time,
                cost=original_activity.cost
            )
            db.add(new_activity)
            
    db.commit()
    return new_trip

# --- USER PROFILE ROUTES ---
@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.put("/users/me", response_model=schemas.User)
def update_user_profile(user_update: schemas.UserUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@app.delete("/users/me")
def delete_user_account(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # Cascade delete is handled by database models, but explicit cleanup is explicit
    db.delete(current_user)
    db.commit()
    return {"detail": "Account deleted successfully"}

# --- SAVED DESTINATIONS ROUTES ---
@app.get("/users/me/saved-destinations", response_model=List[schemas.SavedDestination])
def get_saved_destinations(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return db.query(models.SavedDestination).filter(models.SavedDestination.user_id == current_user.id).all()

@app.post("/users/me/saved-destinations/{city_id}", response_model=schemas.SavedDestination)
def save_destination(city_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    city = db.query(models.City).filter(models.City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
        
    existing = db.query(models.SavedDestination).filter(
        models.SavedDestination.user_id == current_user.id,
        models.SavedDestination.city_id == city_id
    ).first()
    
    if existing:
        return existing
        
    saved = models.SavedDestination(user_id=current_user.id, city_id=city_id)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved

@app.delete("/users/me/saved-destinations/{city_id}")
def unsave_destination(city_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    saved = db.query(models.SavedDestination).filter(
        models.SavedDestination.user_id == current_user.id,
        models.SavedDestination.city_id == city_id
    ).first()
    
    if not saved:
         raise HTTPException(status_code=404, detail="Destination not found in saved list")
         
    db.delete(saved)
    db.commit()
    return {"detail": "Destination removed from saved list"}

# --- SEARCH ROUTES ---

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
    
    print("Starting server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

# --- ADMIN DEPENDENCY ---
def get_current_admin(current_user: models.User = Depends(auth.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

# --- ADMIN ANALYTICS ROUTES ---
@app.get("/admin/stats", response_model=schemas.AdminStats)
def get_admin_stats(current_admin: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    total_users = db.query(models.User).count()
    total_trips = db.query(models.Trip).count()
    active_trips = db.query(models.Trip).filter(models.Trip.status == "active").count()
    
    # Calculate estimated revenue (Mock calculation or sum of budget/costs if applicable)
    # Using simple heuristic: 1% of total budgets tracked
    total_budget_sum = db.query(models.Trip).with_entities(func.sum(models.Trip.budget_limit)).scalar() or 0
    total_revenue_estimated = total_budget_sum * 0.01 
    
    return {
        "total_users": total_users,
        "total_trips": total_trips,
        "active_trips": active_trips,
        "total_revenue_estimated": total_revenue_estimated
    }

from sqlalchemy import func, extract

@app.get("/admin/stats/growth", response_model=List[schemas.GrowthData])
def get_growth_stats(period: str = "monthly", current_admin: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
<<<<<<< HEAD
    # Group by creation date
    if period == "monthly":
        date_format = "YYYY-MM"
    else:
        date_format = "YYYY-WW" # Weekly
        
    query = db.query(
        func.to_char(models.Trip.created_at, date_format).label('period'),
=======
    # Group by creation date (using SQLite compatible strftime)
    if period == "monthly":
        date_format = "%Y-%m"
    else:
        date_format = "%Y-%W" # Weekly
        
    # Stats for Trips creation
    # Note: SQLite uses strftime('%Y-%m', date_col)
    query = db.query(
        func.strftime(date_format, models.Trip.created_at).label('period'),
>>>>>>> b1b02e3c0d2006fd00e882c768604aa877c20d20
        func.count(models.Trip.id).label('count')
    ).group_by('period').order_by('period').all()
    
    return [{"period": row.period or "Unknown", "count": row.count} for row in query]

@app.get("/admin/stats/top-destinations", response_model=List[schemas.TopDestination])
def get_top_destinations(limit: int = 5, current_admin: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    # Aggregating from Stops and SavedDestinations
    query = db.query(
        models.Stop.city_name,
        func.count(models.Stop.id).label('visit_count')
    ).group_by(models.Stop.city_name).order_by(func.count(models.Stop.id).desc()).limit(limit).all()
    
    # Simple mapping, country might be missing if only city_name is stored in Stop
    #Ideally Stop should link to City model, but it stores city_name string based on current schema
    # We can try to fetch country from City table if name matches
    
    results = []
    for row in query:
        city = db.query(models.City).filter(models.City.name == row.city_name).first()
        country = city.country if city else "Unknown"
        results.append({
            "city_name": row.city_name,
            "country": country,
            "visit_count": row.visit_count
        })
        
    return results

@app.get("/admin/users", response_model=List[schemas.User])
def list_users(skip: int = 0, limit: int = 20, current_admin: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(models.User).offset(skip).limit(limit).all()

@app.put("/admin/users/{user_id}/role")
def change_user_role(user_id: int, is_admin: bool, current_admin: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_admin = 1 if is_admin else 0
    db.commit()
    return {"detail": f"User role updated to {'Admin' if is_admin else 'User'}"}

@app.delete("/admin/users/{user_id}")
def delete_user(user_id: int, current_admin: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}
