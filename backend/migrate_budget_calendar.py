"""
Database Migration Script for Trip Budget & Calendar Features
Adds the expenses table to support detailed expense tracking
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import create_engine, inspect
from database import Base, SQLALCHEMY_DATABASE_URL
import models

def migrate_database():
    """Create new tables and update existing ones"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    inspector = inspect(engine)
    
    # Check if expenses table already exists
    existing_tables = inspector.get_table_names()
    
    print("Current tables:", existing_tables)
    
    if "expenses" in existing_tables:
        print("✓ Expenses table already exists")
    else:
        print("Creating expenses table...")
        # Create all tables (will only create missing ones)
        Base.metadata.create_all(bind=engine)
        print("✓ Expenses table created successfully")
    
    # Verify the table was created
    inspector = inspect(engine)
    updated_tables = inspector.get_table_names()
    
    print("\nFinal tables:", updated_tables)
    print("\n✓ Migration completed successfully!")
    
    # Show expenses table structure
    if "expenses" in updated_tables:
        columns = inspector.get_columns("expenses")
        print("\nExpenses table structure:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")

if __name__ == "__main__":
    migrate_database()
