# GlobeTrotter - Your Personalized Travel Companion

GlobeTrotter is a full-stack web application designed to help travelers plan, track, and share their journeys. From budget management to itinerary building, GlobeTrotter provides a comprehensive suite of tools for the modern explorer.

## 🚀 Features

-   **Trip Planning**: Create and manage detailed itineraries with multiple stops and activities.
-   **Budget Tracking**: Monitor your expenses in real-time with visual cost breakdowns and daily spending trends.
-   **User Authentication**: Secure signup and login system with persistent user profiles.
-   **Interactive Dashboard**: Personalized overview of upcoming trips, travel stats, and curated recommendations.
-   **Shared Itineraries**: Make your trips public and share them with the world via unique share tokens.
-   **Admin Panel**: Robust analytics and user management tools for administrators.

## 🛠️ Tech Stack

-   **Backend**: Python, FastAPI, SQLAlchemy
-   **Database**: PostgreSQL (Primary), SQLite (Supported)
-   **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (ES6+)
-   **Authentication**: JWT (JSON Web Tokens)
-   **Styling**: Premium, responsive dark-themed UI with glassmorphism aesthetics.

## 🏁 Getting Started

### Prerequisites

-   Python 3.10+
-   PostgreSQL
-   Required Python packages (see `backend/requirements.txt`)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Ajith-Anand-R/GlobeTrotter.git
    cd GlobeTrotter
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r backend/requirements.txt
    ```

3.  **Database Setup**:
    -   Ensure PostgreSQL is running.
    -   Update the connection string in `backend/database.py`.
    -   Run the initialization script:
        ```bash
        python init_pg_db.py
        ```

4.  **Run the Backend Server**:
    ```bash
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
    ```

5.  **Access the Frontend**:
    Open `Frontend/login_/_signup_screen/code.html` in your favorite browser.

## 🧪 Testing

The repository includes several utility scripts for verification:
-   `backend/bootstrap_user.py`: Creates a test user.
-   `check_pg.py`: Verifies PostgreSQL connection.
-   `test_budget.py`: Tests budget calculation logic.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
