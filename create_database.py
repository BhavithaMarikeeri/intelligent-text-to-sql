
import sqlite3

# Connect to database
connection = sqlite3.connect("database/ecommerce.db")

# Create cursor
cursor = connection.cursor()

# Create customers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL
)
""")

# Create orders table
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    amount REAL,
    FOREIGN KEY (customer_id)
    REFERENCES customers(customer_id)
)
""")

# Insert customer data
cursor.executemany(
    "INSERT OR IGNORE INTO customers VALUES (?, ?, ?)",
    [
        (1, "Rahul", "Bengaluru"),
        (2, "Priya", "Mysuru"),
        (3, "Aman", "Bengaluru")
    ]
)

# Insert order data
cursor.executemany(
    "INSERT OR IGNORE INTO orders VALUES (?, ?, ?)",
    [
        (101, 1, 5000),
        (102, 2, 3000),
        (103, 1, 2000),
        (104, 3, 7000)
    ]
)

# Save changes
connection.commit()

# Display customers
cursor.execute("SELECT * FROM customers")

print("CUSTOMERS:")
for row in cursor.fetchall():
    print(row)

# Close connection
connection.close()
