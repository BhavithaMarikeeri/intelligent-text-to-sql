
from app.services.sql_generator import generate_sql
from app.services.sql_executor import execute_sql


def process_question(question: str) -> dict:
    """
    Complete Text-to-SQL pipeline:
    1. Generate SQL using Gemini.
    2. Check whether clarification is required.
    3. Validate generated SQL.
    4. Execute safe SQL.
    5. Return results.
    """

    try:
        # STEP 1: Generate SQL
        print("\n[1] Generating SQL using Ollama (Qwen 2.5 3B)...")

        generated = generate_sql(question)

        # STEP 2: Check for clarification
        if generated["needs_clarification"]:
            return {
                "success": False,
                "needs_clarification": True,
                "clarification_question": generated[
                    "clarification_question"
                ],
                "sql": None,
                "explanation": generated["explanation"],
                "results": []
            }

        sql_query = generated["sql"]

        print("[2] SQL generated successfully.")

        # STEP 3 and 4: Validate and execute SQL
        print("[3] Validating and executing SQL...")

        execution = execute_sql(sql_query)

        if not execution["success"]:
            return {
                "success": False,
                "needs_clarification": False,
                "clarification_question": None,
                "sql": sql_query,
                "explanation": generated["explanation"],
                "error": execution["error"],
                "results": []
            }

        # STEP 5: Return final response
        print("[4] Query executed successfully.")

        return {
            "success": True,
            "needs_clarification": False,
            "clarification_question": None,
            "sql": sql_query,
            "explanation": generated["explanation"],
            "assumptions": generated["assumptions"],
            "row_count": execution["row_count"],
            "results": execution["results"]
        }

    except Exception as error:
        return {
            "success": False,
            "needs_clarification": False,
            "clarification_question": None,
            "error": str(error),
            "results": []
        }


if __name__ == "__main__":

    question = "Show me the best customers."

    print("\nUSER QUESTION:")
    print(question)

    response = process_question(question)

    print("\nFINAL RESPONSE")
    print("=" * 50)

    import json
    print(json.dumps(response, indent=4))
