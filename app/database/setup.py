
import sqlite3
from pathlib import Path

# Find the project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Database location
DB_PATH = BASE_DIR / "ecommerce.db"


def create_database():
    connection = sqlite3.connect(DB_PATH)

    # Enable foreign key enforcement
    connection.execute("PRAGMA foreign_keys = ON")

    cursor = connection.cursor()

    # Customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT NOT NULL
        )
    """)

    # Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            order_date TEXT NOT NULL,
            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        )
    """)

    # Insert sample customers
    cursor.executemany("""
        INSERT OR IGNORE INTO customers
        (customer_id, name, city)
        VALUES (?, ?, ?)
    """, [
        (1, "Rahul", "Bengaluru"),
        (2, "Priya", "Mysuru"),
        (3, "Aman", "Bengaluru"),
        (4, "Sneha", "Mumbai"),
        (5, "Arjun", "Delhi")
    ])

    # Insert sample orders
    cursor.executemany("""
        INSERT OR IGNORE INTO orders
        (order_id, customer_id, amount, order_date)
        VALUES (?, ?, ?, ?)
    """, [
        (101, 1, 5000, "2026-01-10"),
        (102, 2, 3000, "2026-01-12"),
        (103, 1, 2000, "2026-01-15"),
        (104, 3, 7000, "2026-01-18"),
        (105, 4, 4500, "2026-01-20"),
        (106, 5, 6000, "2026-01-22"),
        (107, 2, 1500, "2026-01-25"),
        (108, 3, 2500, "2026-01-28")
    ])

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_orders_customer
        ON orders(customer_id)
    """)

    connection.commit()
    connection.close()

    print("Database created successfully!")
    print(f"Database location: {DB_PATH}")


if __name__ == "__main__":
    create_database()
