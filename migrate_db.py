import sqlite3

def migrate():
    print("Migrating database...")
    conn = sqlite3.connect("globetrotter.db")
    cursor = conn.cursor()
    
    try:
        # Tables and columns to check
        migrations = {
            "users": [
                ("profile_image_url", "TEXT"),
                ("bio", "TEXT"),
                ("language", "TEXT DEFAULT 'en'"),
                ("location", "TEXT"),
                ("is_admin", "INTEGER DEFAULT 0"),
                ("created_at", "DATETIME")
            ],
            "trips": [
                ("budget_limit", "FLOAT DEFAULT 0.0"),
                ("is_public", "INTEGER DEFAULT 0"),
                ("share_token", "TEXT")
            ],
            "stops": [
                ("accommodation_cost", "FLOAT DEFAULT 0.0"),
                ("transport_cost", "FLOAT DEFAULT 0.0")
            ]
        }
        
        for table, columns in migrations.items():
            for col_name, col_type in columns:
                try:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
                    print(f"Added {col_name} to {table}")
                except sqlite3.OperationalError as e:
                    if "duplicate column" in str(e):
                        print(f"{col_name} already exists in {table}")
                    else:
                        print(f"Error adding {col_name} to {table}: {e}")

        conn.commit()
        print("Migration complete.")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
