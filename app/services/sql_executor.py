
import sqlite3

from app.database.setup import DB_PATH
from app.services.sql_validator import validate_sql


def execute_sql(query: str) -> dict:

    # Step 1: Validate SQL
    validation = validate_sql(query)

    if not validation["valid"]:
        return {
            "success": False,
            "error": validation["error"],
            "results": []
        }

    connection = None

    try:
        # Step 2: Open database in read-only mode
        database_uri = DB_PATH.resolve().as_uri() + "?mode=ro"

        connection = sqlite3.connect(
            database_uri,
            uri=True
        )

        connection.row_factory = sqlite3.Row

        # Step 3: Execute validated query
        cursor = connection.execute(validation["sql"])

        # Step 4: Fetch results
        rows = cursor.fetchall()

        results = [
            dict(row) for row in rows
        ]

        return {
            "success": True,
            "error": None,
            "row_count": len(results),
            "results": results
        }

    except sqlite3.Error as error:
        return {
            "success": False,
            "error": str(error),
            "results": []
        }

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":

    test_query = """
        SELECT
            c.name,
            SUM(o.amount) AS total_spending
        FROM customers c
        JOIN orders o
            ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.name
        ORDER BY total_spending DESC
        LIMIT 3;
    """

    output = execute_sql(test_query)

    print("\nEXECUTION RESULT")
    print("=" * 40)
    print(output)
