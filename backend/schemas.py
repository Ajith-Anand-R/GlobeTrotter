from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class ActivityBase(BaseModel):
    description: str
    time: Optional[str] = None
    cost: float = 0.0

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int
    stop_id: int

    class Config:
        from_attributes = True

class CatalogActivityBase(BaseModel):
    name: str
    category: str
    cost: float
    duration: str
    description: str
    image_url: Optional[str] = None

class CatalogActivity(CatalogActivityBase):
    id: int
    city_id: int
    
    class Config:
        from_attributes = True

class CityBase(BaseModel):
    name: str
    country: str
    description: str
    image_url: Optional[str] = None
    cost_index: float
    popularity: int

class City(CityBase):
    id: int
    catalog_activities: List[CatalogActivity] = []
    
    class Config:
        from_attributes = True

class StopBase(BaseModel):
    city_name: str
    arrival_date: datetime
    departure_date: datetime
    sort_order: int
    accommodation_cost: float = 0.0
    transport_cost: float = 0.0

class StopCreate(StopBase):
    pass

class StopUpdate(StopBase):
    pass

class StopReorder(BaseModel):
    stop_ids: List[int]

class Stop(StopBase):
    id: int
    trip_id: int
    activities: List[Activity] = []

    class Config:
        from_attributes = True

class TripBase(BaseModel):
    destination: str
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    completion_percentage: int = 0
    cost_from: Optional[float] = None
    budget_limit: float = 0.0
    cover_image_url: Optional[str] = None
    status: str

class TripCreate(TripBase):
    pass

class Trip(TripBase):
    id: int
    owner_id: int
    created_at: Optional[datetime] = None
    stops: List[Stop] = []

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    full_name: str

class User(UserBase):
    id: int
    full_name: str
    profile_image_url: Optional[str] = None
    bio: Optional[str] = None
    language: str = "en"
    location: Optional[str] = None
    is_admin: int = 0
    created_at: Optional[datetime] = None
    
    trips: List[Trip] = []

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    bio: Optional[str] = None
    language: Optional[str] = "en"
    location: Optional[str] = None

class ShareTokenResponse(BaseModel):
    share_url: str
    token: str

class SavedDestination(BaseModel):
    user_id: int
    city_id: int
    saved_at: datetime
    city: Optional[City] = None

    class Config:
        from_attributes = True

class TripPublic(TripBase):
    id: int
    owner_name: str
    owner_image: Optional[str] = None
    stops: List[Stop] = []

    class Config:
        from_attributes = True

class AdminStats(BaseModel):
    total_users: int
    total_trips: int
    active_trips: int
    total_revenue_estimated: float
    
class GrowthData(BaseModel):
    period: str # e.g., "2023-01"
    count: int

class TopDestination(BaseModel):
    city_name: str
    country: str
    visit_count: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class DashboardData(BaseModel):
    full_name: str
    upcoming_trip: Optional[Trip] = None
    recent_trips: List[Trip] = []
    recommendations: List[dict] = []

# --- EXPENSE SCHEMAS ---
class ExpenseBase(BaseModel):
    name: str
    category: str  # transport, stay, food, activities, other
    amount: float
    currency: str = "USD"
    date: datetime
    notes: Optional[str] = None
    stop_id: Optional[int] = None
    activity_id: Optional[int] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None

class Expense(ExpenseBase):
    id: int
    trip_id: int
    
    class Config:
        from_attributes = True

# --- BUDGET SCHEMAS ---
class BudgetBreakdown(BaseModel):
    transport: float
    stay: float
    food: float
    activities: float
    other: float

class BudgetAlert(BaseModel):
    type: str  # warning, danger, info
    category: str
    message: str
    percentage: float

class BudgetSummary(BaseModel):
    budget_limit: float
    total_cost: float
    remaining: float
    utilization_percentage: float
    breakdown: BudgetBreakdown
    daily_average: float
    daily_target: float
    currency: str
    alerts: List[BudgetAlert]

class DailySpending(BaseModel):
    date: str
    total: float
    breakdown: BudgetBreakdown
    over_budget: bool

class DailyTrendResponse(BaseModel):
    days: List[DailySpending]
    budget_limit_per_day: float

# --- TIMELINE SCHEMAS ---
class TimelineActivity(BaseModel):
    id: int
    description: str
    time: Optional[str]
    duration: Optional[str] = None
    cost: float
    category: str
    sort_order: int = 0

class TimelineStop(BaseModel):
    id: int
    city_name: str
    arrival_date: datetime
    departure_date: datetime
    
    class Config:
        from_attributes = True

class TimelineDay(BaseModel):
    day_number: int
    date: str
    title: str
    stops: List[TimelineStop]
    activities: List[TimelineActivity]

class TripTimeline(BaseModel):
    trip_id: int
    title: str
    start_date: str
    end_date: str
    days: List[TimelineDay]

class CalendarDay(BaseModel):
    date: str
    activity_count: int
    has_activities: bool
    is_trip_day: bool

class CalendarResponse(BaseModel):
    month: str
    days: List[CalendarDay]

class ActivityReorder(BaseModel):
    activity_ids: List[int]

class ActivityTimeUpdate(BaseModel):
    time: str
    duration: Optional[str] = None
