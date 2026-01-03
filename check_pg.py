import psycopg2
from psycopg2 import sql

def check_db():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="200611",
            host="127.0.0.1",
            port="5432"
        )
        print("Connected to PostgreSQL on port 5432")
        
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if 'globetrotter' exists
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'globetrotter'")
        exists = cur.fetchone()
        
        if not exists:
            print("Database 'globetrotter' does not exist. Creating it...")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier("globetrotter")))
            print("Database 'globetrotter' created successfully.")
        else:
            print("Database 'globetrotter' already exists.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
