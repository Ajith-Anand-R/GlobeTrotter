import sqlite3

conn = sqlite3.connect('globetrotter.db')
cursor = conn.cursor()

# Get existing columns
cursor.execute('PRAGMA table_info(users)')
existing_columns = [row[1] for row in cursor.fetchall()]
print(f"Existing columns: {existing_columns}")

# Add missing columns if they don't exist
columns_to_add = [
    ('full_name', 'VARCHAR'),
    ('profile_image_url', 'VARCHAR'),
    ('bio', 'VARCHAR'),
    ('language', 'VARCHAR DEFAULT "en"'),
    ('location', 'VARCHAR'),
    ('is_admin', 'INTEGER DEFAULT 0'),
    ('created_at', 'DATETIME'),
]

for col_name, col_type in columns_to_add:
    if col_name not in existing_columns:
        try:
            cursor.execute(f'ALTER TABLE users ADD COLUMN {col_name} {col_type}')
            print(f"Added column: {col_name}")
        except Exception as e:
            print(f"Error adding {col_name}: {e}")

conn.commit()
conn.close()
print("Migration complete!")
