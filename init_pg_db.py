import sys
import os

# Ensure backend directory is in path for imports
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import engine
import models

def init_db():
    print("Dropping all tables in PostgreSQL (Fresh Start)...")
    models.Base.metadata.drop_all(bind=engine)
    print("Creating tables in PostgreSQL...")
    models.Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()
