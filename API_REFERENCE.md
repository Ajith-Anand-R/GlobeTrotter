# Trip Budget & Calendar API Reference

## Base URL
```
http://127.0.0.1:8000
```

## Authentication
All endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

---

## Budget Endpoints

### Get Budget Summary
```http
GET /budget/{trip_id}
```

**Response**: `BudgetSummary`
```json
{
  "budget_limit": 3500.0,
  "total_cost": 1250.0,
  "remaining": 2250.0,
  "utilization_percentage": 35.7,
  "breakdown": {
    "transport": 562.0,
    "stay": 250.0,
    "food": 250.0,
    "activities": 187.0,
    "other": 1.0
  },
  "daily_average": 145.0,
  "daily_target": 125.0,
  "currency": "USD",
  "alerts": [
    {
      "type": "warning",
      "category": "food",
      "message": "Food category is 85% full",
      "percentage": 85.0
    }
  ]
}
```

### Get Daily Spending Trend
```http
GET /budget/{trip_id}/daily-trend
```

**Response**: `DailyTrendResponse`
```json
{
  "days": [
    {
      "date": "2023-10-12",
      "total": 65.0,
      "breakdown": {
        "transport": 0.0,
        "stay": 50.0,
        "food": 15.0,
        "activities": 0.0,
        "other": 0.0
      },
      "over_budget": false
    }
  ],
  "budget_limit_per_day": 125.0
}
```

---

## Expense Endpoints

### List Expenses
```http
GET /trips/{trip_id}/expenses?category={category}&start_date={date}&end_date={date}
```

**Query Parameters**:
- `category` (optional): Filter by category (transport, stay, food, activities, other)
- `start_date` (optional): ISO 8601 datetime
- `end_date` (optional): ISO 8601 datetime

**Response**: `List[Expense]`
```json
[
  {
    "id": 1,
    "trip_id": 1,
    "stop_id": null,
    "activity_id": null,
    "name": "Taxi to Airport",
    "category": "transport",
    "amount": 45.0,
    "currency": "USD",
    "date": "2023-10-17T10:00:00",
    "notes": "Uber ride"
  }
]
```

### Create Expense
```http
POST /trips/{trip_id}/expenses
```

**Request Body**: `ExpenseCreate`
```json
{
  "name": "Dinner at Restaurant",
  "category": "food",
  "amount": 85.0,
  "currency": "USD",
  "date": "2023-10-17T19:30:00",
  "notes": "Optional notes",
  "stop_id": 1,
  "activity_id": null
}
```

**Response**: `Expense`

### Update Expense
```http
PUT /expenses/{expense_id}
```

**Request Body**: `ExpenseUpdate` (all fields optional)
```json
{
  "name": "Updated name",
  "amount": 90.0,
  "notes": "Updated notes"
}
```

**Response**: `Expense`

### Delete Expense
```http
DELETE /expenses/{expense_id}
```

**Response**:
```json
{
  "detail": "Expense deleted"
}
```

---

## Timeline Endpoints

### Get Trip Timeline
```http
GET /trips/{trip_id}/timeline
```

**Response**: `TripTimeline`
```json
{
  "trip_id": 1,
  "title": "Summer in Paris",
  "start_date": "2024-08-12",
  "end_date": "2024-08-19",
  "days": [
    {
      "day_number": 1,
      "date": "2024-08-12",
      "title": "Day 1: Paris",
      "stops": [
        {
          "id": 1,
          "city_name": "Paris",
          "arrival_date": "2024-08-12T09:00:00",
          "departure_date": "2024-08-19T18:00:00"
        }
      ],
      "activities": [
        {
          "id": 1,
          "description": "Flight to Paris (CDG)",
          "time": "09:00 AM",
          "duration": "2h 30m",
          "cost": 0.0,
          "category": "transport",
          "sort_order": 0
        },
        {
          "id": 2,
          "description": "Check-in: Pullman Tour Eiffel",
          "time": "12:30 PM",
          "duration": null,
          "cost": 250.0,
          "category": "accommodation",
          "sort_order": 1
        }
      ]
    }
  ]
}
```

### Get Calendar View
```http
GET /trips/{trip_id}/calendar?month={YYYY-MM}
```

**Query Parameters**:
- `month` (optional): Format YYYY-MM (defaults to trip start month)

**Response**: `CalendarResponse`
```json
{
  "month": "2024-08",
  "days": [
    {
      "date": "2024-08-01",
      "activity_count": 0,
      "has_activities": false,
      "is_trip_day": false
    },
    {
      "date": "2024-08-12",
      "activity_count": 4,
      "has_activities": true,
      "is_trip_day": true
    }
  ]
}
```

### Reorder Activities
```http
POST /stops/{stop_id}/reorder_activities
```

**Request Body**: `ActivityReorder`
```json
{
  "activity_ids": [3, 1, 2, 4]
}
```

**Response**:
```json
{
  "detail": "Activity reordering not yet implemented - requires sort_order field in Activity model"
}
```

### Update Activity Time
```http
PUT /activities/{activity_id}/time
```

**Request Body**: `ActivityTimeUpdate`
```json
{
  "time": "14:30",
  "duration": "2h 30m"
}
```

**Response**: `Activity`

---

## Data Models

### Expense Categories
- `transport` - Flights, trains, buses, taxis
- `stay` - Hotels, accommodations
- `food` - Meals, restaurants, groceries
- `activities` - Tours, attractions, entertainment
- `other` - Miscellaneous expenses

### Activity Categories (Auto-detected)
- `transport` - Keywords: flight, train, bus, taxi, transport
- `accommodation` - Keywords: hotel, check-in, accommodation, stay
- `food` - Keywords: lunch, dinner, breakfast, restaurant, food
- `sightseeing` - Keywords: museum, tour, visit, sightseeing
- `other` - Default category

### Alert Types
- `warning` - Category 85-99% full
- `danger` - Category ≥100% full or overall budget ≥90%
- `info` - Informational alerts

---

## Error Responses

### 404 Not Found
```json
{
  "detail": "Trip not found"
}
```

### 400 Bad Request
```json
{
  "detail": "Trip must have start and end dates"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

---

## Example Usage

### JavaScript (Fetch API)
```javascript
// Get budget summary
const response = await fetch('http://127.0.0.1:8000/budget/1', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const budget = await response.json();

// Create expense
const expense = await fetch('http://127.0.0.1:8000/trips/1/expenses', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    name: 'Taxi Ride',
    category: 'transport',
    amount: 25.50,
    date: new Date().toISOString()
  })
});

// Get timeline
const timeline = await fetch('http://127.0.0.1:8000/trips/1/timeline', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const timelineData = await timeline.json();
```

### Python (Requests)
```python
import requests

BASE_URL = "http://127.0.0.1:8000"
headers = {"Authorization": f"Bearer {token}"}

# Get budget
budget = requests.get(f"{BASE_URL}/budget/1", headers=headers).json()

# Create expense
expense_data = {
    "name": "Taxi Ride",
    "category": "transport",
    "amount": 25.50,
    "date": "2023-10-17T10:00:00"
}
expense = requests.post(
    f"{BASE_URL}/trips/1/expenses",
    json=expense_data,
    headers=headers
).json()

# Get timeline
timeline = requests.get(f"{BASE_URL}/trips/1/timeline", headers=headers).json()
```

---

## Notes

> [!IMPORTANT]
> All datetime fields should be in ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`

> [!TIP]
> Use the `category` query parameter on `/trips/{trip_id}/expenses` to filter expenses for specific chart sections

> The timeline endpoint automatically categorizes activities based on keywords in their descriptions. For more accurate categorization, consider adding a `category` field to the Activity model.

---

## Admin & Analytics Endpoints
*Authentication Required: Admin User*

### Get Overview Stats
```http
GET /admin/stats
```
**Response**: `AdminStats`
```json
{
  "total_users": 150,
  "total_trips": 45,
  "active_trips": 12,
  "total_revenue_estimated": 12500.50
}
```

### Get Growth Data
```http
GET /admin/stats/growth?period={monthly|weekly}
```
**Response**: `List[GrowthData]`
```json
[
  { "period": "2023-01", "count": 12 },
  { "period": "2023-02", "count": 18 }
]
```

### Get Top Destinations
```http
GET /admin/stats/top-destinations?limit=5
```
**Response**: `List[TopDestination]`
```json
[
  { "city_name": "Paris", "country": "France", "visit_count": 42 }
]
```

### Manage Users
- `GET /admin/users` - List users
- `PUT /admin/users/{user_id}/role` - Change role (Body: `{"is_admin": true}`)
- `DELETE /admin/users/{user_id}` - Ban/Delete user
