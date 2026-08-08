import sqlite3

from database import get_connection

def create_user(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO users(telegram_id) VALUES(?)",
        (telegram_id,)
    )

    conn.commit()
    conn.close()


def update_name(telegram_id, name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET name = ? WHERE telegram_id = ?",
        (name, telegram_id)
    )

    conn.commit()
    conn.close()


def update_allowance(telegram_id, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET monthly_allowance = ? WHERE telegram_id = ?",
        (amount, telegram_id)
    )

    conn.commit()
    conn.close()


def get_user(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, monthly_allowance FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )

    user = cursor.fetchone()

    conn.close()

    return user
def get_conversation(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT conversation FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )

    data = cursor.fetchone()
    conn.close()

    return data[0] if data and data[0] else ""


def update_conversation(telegram_id, new_message):
    conn = get_connection()
    cursor = conn.cursor()

    old_convo = get_conversation(telegram_id)

    updated = old_convo + f"\nUser: {new_message}"

    # keep only last ~1000 chars (avoid huge memory)
    updated = updated[-1000:]

    cursor.execute(
        "UPDATE users SET conversation = ? WHERE telegram_id = ?",
        (updated, telegram_id)
    )

    conn.commit()
    conn.close()
    
def add_expense(user_id, amount, category):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO expenses (user_id, amount, category) VALUES (?, ?, ?)",
        (user_id, amount, category)
    )

    conn.commit()
    conn.close()


def get_total_spent(user_id):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT SUM(amount) FROM expenses WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()[0]

    conn.close()

    return result if result else 0

def clear_expenses(user_id):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE user_id = ?", (user_id,))
    
    conn.commit()
    conn.close()
    
def get_top_category(user_id):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, SUM(amount) as total
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
        ORDER BY total DESC
        LIMIT 1
    """, (user_id,))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None