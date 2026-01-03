import sqlite3

def check():
    conn = sqlite3.connect("globetrotter.db")
    cursor = conn.cursor()
    print("Columns in trips:")
    for row in cursor.execute("PRAGMA table_info(trips)"):
        print(row)
    print("\nColumns in stops:")
    for row in cursor.execute("PRAGMA table_info(stops)"):
        print(row)
    conn.close()

if __name__ == "__main__":
    check()
