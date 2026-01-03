import sqlite3

def list_trips():
    conn = sqlite3.connect("globetrotter.db")
    cursor = conn.cursor()
    print("Trips:")
    for row in cursor.execute("SELECT id, title FROM trips"):
        print(row)
    conn.close()

if __name__ == "__main__":
    list_trips()
