from database import get_connection

def add_snack(name, expiry_date, stock):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO snacks (name, expiry_date, stock) VALUES (?, ?, ?)",
        (name, expiry_date, stock)
    )
    conn.commit()
    conn.close()


def get_all_snacks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM snacks")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_expiring_snacks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM snacks
        WHERE DATE(expiry_date) <= DATE('now', '+3 day');
    """)
    rows = cur.fetchall()
    conn.close()
    return rows
