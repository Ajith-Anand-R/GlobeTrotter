"""
Database Migration Script for Admin Dashboard
Adds is_admin to users and created_at to users/trips.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import create_engine, inspect, text
from database import Base, SQLALCHEMY_DATABASE_URL
import models

def migrate_database():
    """Update tables with admin columns"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        with conn.begin(): # Start transaction
            # 1. Update Users Table
            columns = [c['name'] for c in inspector.get_columns("users")]
            
            if "is_admin" not in columns:
                print("Adding is_admin to users...")
                conn.execute(text("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0"))
            
            if "created_at" not in columns:
                print("Adding created_at to users...")
                conn.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME"))
                # Set default for existing rows
                conn.execute(text("UPDATE users SET created_at = datetime('now') WHERE created_at IS NULL"))

            # 2. Update Trips Table
            trip_columns = [c['name'] for c in inspector.get_columns("trips")]
            if "created_at" not in trip_columns:
                print("Adding created_at to trips...")
                conn.execute(text("ALTER TABLE trips ADD COLUMN created_at DATETIME"))
                conn.execute(text("UPDATE trips SET created_at = datetime('now') WHERE created_at IS NULL"))

        print("✓ Admin migration completed successfully!")

if __name__ == "__main__":
    try:
        migrate_database()
    except Exception as e:
        print(f"Migration failed: {e}")
