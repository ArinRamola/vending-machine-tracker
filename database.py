import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

DB_NAME = "database.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

# Initialize database
conn = get_connection()
c = conn.cursor()

# Snacks table with additional fields
c.execute("""
CREATE TABLE IF NOT EXISTS snacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    stock INTEGER DEFAULT 0,
    expiry_date DATE NOT NULL,
    price REAL DEFAULT 0.0,
    category TEXT DEFAULT 'General',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Users table
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin','vendor','employee')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)
""")

# Machines table with status
c.execute("""
CREATE TABLE IF NOT EXISTS machines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'maintenance', 'inactive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Updates table with better structure
c.execute("""
CREATE TABLE IF NOT EXISTS updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor TEXT NOT NULL,
    machine TEXT NOT NULL,
    info TEXT NOT NULL,
    time TEXT NOT NULL,
    update_type TEXT DEFAULT 'restock' CHECK(update_type IN ('restock', 'maintenance', 'issue'))
)
""")

# Insert sample users with hashed passwords
users = [
    ("admin", "admin123", "admin"),
    ("vendor1", "vendor123", "vendor"),
    ("employee1", "emp123", "employee"),
]

for u in users:
    c.execute("""
        INSERT OR IGNORE INTO users (username, password, role)
        VALUES (?, ?, ?)
    """, (u[0], generate_password_hash(u[1]), u[2]))

# Insert sample machines
machines = [
    ("Main Lobby Machine", "Building A - Main Entrance"),
    ("Cafeteria Machine", "Building A - 2nd Floor Cafeteria"),
    ("Break Room Machine", "Building B - 3rd Floor"),
]

for m in machines:
    c.execute("""
        INSERT OR IGNORE INTO machines (name, location, status)
        VALUES (?, ?, 'active')
    """, m)

# Insert sample snacks with variety
sample_snacks = [
    ("Chips", 50, (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"), 1.50, "Savory"),
    ("Chocolate Bar", 40, (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"), 2.00, "Candy"),
    ("Cookies", 35, (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"), 1.75, "Bakery"),
    ("Granola Bar", 45, (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"), 2.25, "Healthy"),
    ("Pretzels", 30, (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"), 1.50, "Savory"),  # Expiring soon
    ("Gummy Bears", 25, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), 1.25, "Candy"),  # Expiring soon
    ("Trail Mix", 20, (datetime.now() + timedelta(days=120)).strftime("%Y-%m-%d"), 2.50, "Healthy"),
    ("Popcorn", 15, (datetime.now() + timedelta(days=40)).strftime("%Y-%m-%d"), 1.00, "Savory"),
]

for snack in sample_snacks:
    c.execute("""
        INSERT OR IGNORE INTO snacks (name, stock, expiry_date, price, category)
        VALUES (?, ?, ?, ?, ?)
    """, snack)

conn.commit()
conn.close()

print("=" * 50)
print("Database initialized successfully!")
print("=" * 50)
print("\nSample Login Credentials:")
print("-" * 50)
print("Admin:")
print("  Username: admin")
print("  Password: admin123")
print("\nVendor:")
print("  Username: vendor1")
print("  Password: vendor123")
print("\nEmployee:")
print("  Username: employee1")
print("  Password: emp123")
print("=" * 50)