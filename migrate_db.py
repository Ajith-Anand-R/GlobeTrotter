import sqlite3

def migrate():
    print("Migrating database...")
    conn = sqlite3.connect("globetrotter.db")
    cursor = conn.cursor()
    
    try:
        # Add budget_limit to trips
        try:
            cursor.execute("ALTER TABLE trips ADD COLUMN budget_limit FLOAT DEFAULT 0.0")
            print("Added budget_limit to trips")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e):
                print("budget_limit already exists")
            else:
                print(f"Error adding budget_limit: {e}")

        # Add accommodation_cost to stops
        try:
            cursor.execute("ALTER TABLE stops ADD COLUMN accommodation_cost FLOAT DEFAULT 0.0")
            print("Added accommodation_cost to stops")
        except sqlite3.OperationalError as e:
             if "duplicate column" in str(e):
                print("accommodation_cost already exists")
             else:
                print(f"Error adding accommodation_cost: {e}")

        # Add transport_cost to stops
        try:
            cursor.execute("ALTER TABLE stops ADD COLUMN transport_cost FLOAT DEFAULT 0.0")
            print("Added transport_cost to stops")
        except sqlite3.OperationalError as e:
             if "duplicate column" in str(e):
                print("transport_cost already exists")
             else:
                print(f"Error adding transport_cost: {e}")

        conn.commit()
        print("Migration complete.")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
