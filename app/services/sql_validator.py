
import sqlglot
from sqlglot import exp


def validate_sql(query: str) -> dict:

    if not query or not query.strip():
        return {
            "valid": False,
            "error": "SQL query cannot be empty."
        }

    try:
        # Parse SQL using SQLite dialect
        statements = sqlglot.parse(query, read="sqlite")

        # Allow only one SQL statement
        if len(statements) != 1 or statements[0] is None:
            return {
                "valid": False,
                "error": "Only one SQL statement is allowed."
            }

        parsed_query = statements[0]

        # Allow only SELECT queries
        if not isinstance(parsed_query, exp.Query):
            return {
                "valid": False,
                "error": "Only SELECT queries are allowed."
            }

        # Reject dangerous operations
        forbidden = (
            exp.Insert,
            exp.Update,
            exp.Delete,
            exp.Drop,
            exp.Create,
            exp.Alter,
            exp.Command
        )

        if next(parsed_query.find_all(*forbidden), None) is not None:
            return {
                "valid": False,
                "error": "Dangerous SQL operation detected."
            }

        return {
            "valid": True,
            "error": None,
            "sql": parsed_query.sql(dialect="sqlite")
        }

    except sqlglot.errors.ParseError as error:
        return {
            "valid": False,
            "error": f"Invalid SQL syntax: {error}"
        }


if __name__ == "__main__":

    test_queries = [
        "SELECT * FROM customers;",
        "DELETE FROM customers;",
        "DROP TABLE orders;",
        "SELECT name FROM customers WHERE city = 'Bengaluru';"
    ]

    for query in test_queries:
        print("\nQuery:", query)
        print("Result:", validate_sql(query))
