import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from database import engine, Base
import models

# Recreate all tables
print("Dropping existing tables...")
Base.metadata.drop_all(bind=engine)
print("Creating fresh tables...")
Base.metadata.create_all(bind=engine)
print("Database recreated successfully!")
