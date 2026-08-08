import sqlite3

DB_NAME = "atlas.db"


def get_connection():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    # existing users table...

    # ✅ NEW: expenses table
    cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    category TEXT
)
""")
    conn.commit()
    conn.close()