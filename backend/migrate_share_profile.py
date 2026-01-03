"""
Database Migration Script for Shared Itinerary & User Profile
Adds columns for trip sharing, user profile, and saved destinations table.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import create_engine, inspect, text
from database import Base, SQLALCHEMY_DATABASE_URL
import models

def migrate_database():
    """Create new tables and update existing ones"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # 1. Update Users Table
        columns = [c['name'] for c in inspector.get_columns("users")]
        if "profile_image_url" not in columns:
            print("Adding profile columns to users table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN profile_image_url VARCHAR"))
            conn.execute(text("ALTER TABLE users ADD COLUMN bio VARCHAR"))
            conn.execute(text("ALTER TABLE users ADD COLUMN language VARCHAR DEFAULT 'en'"))
            conn.execute(text("ALTER TABLE users ADD COLUMN location VARCHAR"))
            print("✓ User table updated")
            
        # 2. Update Trips Table
        columns = [c['name'] for c in inspector.get_columns("trips")]
        if "is_public" not in columns:
            print("Adding sharable columns to trips table...")
            conn.execute(text("ALTER TABLE trips ADD COLUMN is_public INTEGER DEFAULT 0"))
            conn.execute(text("ALTER TABLE trips ADD COLUMN share_token VARCHAR"))
            # Note: SQLite doesn't support adding UNIQUE constraints via ALTER TABLE easily
            # We will rely on application logic or create index manually if needed
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_trips_share_token ON trips (share_token)"))
            print("✓ Trip table updated")

        # 3. Create Saved Destinations Table
        existing_tables = inspector.get_table_names()
        if "saved_destinations" not in existing_tables:
            print("Creating saved_destinations table...")
            # We can use metadata.create_all which is safer/easier for new tables
            Base.metadata.create_all(bind=engine)
            print("✓ Saved Destinations table created")
            
    print("\n✓ Migration completed successfully!")

if __name__ == "__main__":
    migrate_database()
