
import sqlite3
from app.database.setup import DB_PATH

connection = sqlite3.connect(DB_PATH)

cursor = connection.cursor()

cursor.execute("SELECT * FROM customers")
customers = cursor.fetchall()

print("CUSTOMERS:")
for customer in customers:
    print(customer)

print("\nORDERS:")
cursor.execute("SELECT * FROM orders")

for order in cursor.fetchall():
    print(order)

connection.close()
