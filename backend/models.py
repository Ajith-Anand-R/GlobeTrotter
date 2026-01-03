from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    profile_image_url = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    language = Column(String, default="en")
    location = Column(String, nullable=True)
    is_admin = Column(Integer, default=0) # 0=False, 1=True
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    trips = relationship("Trip", back_populates="owner")
    saved_destinations = relationship("SavedDestination", back_populates="user")

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    destination = Column(String)
    title = Column(String)
    description = Column(String, nullable=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    completion_percentage = Column(Integer, default=0)
    cost_from = Column(Float, nullable=True)
    budget_limit = Column(Float, default=0.0)
    cover_image_url = Column(String, nullable=True)
    status = Column(String)  # e.g., "upcoming", "past"
    is_public = Column(Integer, default=0) # Using Integer as Boolean (0=False, 1=True) for SQLite compatibility if needed, or mapped to Boolean
    share_token = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="trips")
    stops = relationship("Stop", back_populates="trip", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="trip", cascade="all, delete-orphan")

class Stop(Base):
    __tablename__ = "stops"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    city_name = Column(String)
    arrival_date = Column(DateTime)
    departure_date = Column(DateTime)
    sort_order = Column(Integer)
    accommodation_cost = Column(Float, default=0.0)
    transport_cost = Column(Float, default=0.0)
    
    trip = relationship("Trip", back_populates="stops")
    activities = relationship("Activity", back_populates="stop", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="stop", cascade="all, delete-orphan")

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    stop_id = Column(Integer, ForeignKey("stops.id"))
    description = Column(String)
    time = Column(String, nullable=True)
    cost = Column(Float, default=0.0)
    
    stop = relationship("Stop", back_populates="activities")
    expenses = relationship("Expense", back_populates="activity", cascade="all, delete-orphan")

class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    country = Column(String)
    description = Column(String)
    image_url = Column(String)
    cost_index = Column(Float) # 1.0 = average, >1 expensive
    popularity = Column(Integer) # 0-100
    
    popularity = Column(Integer) # 0-100
    
    catalog_activities = relationship("CatalogActivity", back_populates="city")
    users_saved = relationship("SavedDestination", back_populates="city")

class CatalogActivity(Base):
    __tablename__ = "catalog_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"))
    name = Column(String)
    category = Column(String) # e.g., "Sightseeing", "Food", "Adventure"
    cost = Column(Float)
    duration = Column(String) # e.g., "3 hours"
    description = Column(String)
    image_url = Column(String)
    
    city = relationship("City", back_populates="catalog_activities")

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    stop_id = Column(Integer, ForeignKey("stops.id"), nullable=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    
    name = Column(String)
    category = Column(String)  # transport, stay, food, activities, other
    amount = Column(Float)
    currency = Column(String, default="USD")
    date = Column(DateTime)
    notes = Column(String, nullable=True)
    
    trip = relationship("Trip", back_populates="expenses")
    stop = relationship("Stop", back_populates="expenses")
    activity = relationship("Activity", back_populates="expenses")

class SavedDestination(Base):
    __tablename__ = "saved_destinations"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    city_id = Column(Integer, ForeignKey("cities.id"), primary_key=True)
    saved_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="saved_destinations")
    city = relationship("City", back_populates="users_saved")
