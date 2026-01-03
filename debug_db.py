import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal, engine
import models
import auth

try:
    # Ensure tables exist
    models.Base.metadata.create_all(bind=engine)
    print("Tables created/verified")
    
    db = SessionLocal()
    
    # Try to query users
    print("Querying users...")
    users = db.query(models.User).all()
    print(f"Found {len(users)} users")
    
    # Try to create a user
    print("Creating new user...")
    hashed = auth.get_password_hash("testpassword")
    new_user = models.User(
        email="debug_test@example.com",
        hashed_password=hashed,
        full_name="Debug Test"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print(f"Created user: {new_user.id}, {new_user.email}")
    
    db.close()
    print("SUCCESS!")
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()
