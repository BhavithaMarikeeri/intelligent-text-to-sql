
import sqlite3
from app.database.setup import DB_PATH


def get_database_schema():

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    # Find all tables
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
    """)

    tables = cursor.fetchall()

    schema = {}

    for (table_name,) in tables:

        # Get columns of each table
        cursor.execute(f'PRAGMA table_info("{table_name}")')

        columns = cursor.fetchall()

        column_details = []

        for column in columns:

            column_details.append({
                "name": column[1],
                "type": column[2],
                "primary_key": bool(column[5])
            })

        # Get foreign key relationships
        cursor.execute(f'PRAGMA foreign_key_list("{table_name}")')

        foreign_keys = cursor.fetchall()

        relationships = []

        for fk in foreign_keys:

            relationships.append({
                "referenced_table": fk[2],
                "column": fk[3],
                "referenced_column": fk[4]
            })

        schema[table_name] = {
            "columns": column_details,
            "relationships": relationships
        }

    connection.close()

    return schema


def format_schema_for_ai():

    schema = get_database_schema()

    formatted_schema = ""

    for table_name, details in schema.items():

        formatted_schema += f"\nTABLE: {table_name}\n"

        formatted_schema += "COLUMNS:\n"

        for column in details["columns"]:

            formatted_schema += (
                f"- {column['name']} "
                f"({column['type']})"
            )

            if column["primary_key"]:
                formatted_schema += " PRIMARY KEY"

            formatted_schema += "\n"

        formatted_schema += "RELATIONSHIPS:\n"

        for relationship in details["relationships"]:

            formatted_schema += (
                f"- {relationship['column']} references "
                f"{relationship['referenced_table']}."
                f"{relationship['referenced_column']}\n"
            )

    return formatted_schema


if __name__ == "__main__":

    print("DATABASE SCHEMA")
    print("=" * 40)

    print(format_schema_for_ai())
