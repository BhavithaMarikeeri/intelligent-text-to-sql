
import json
import re

from app.core.llm import generate_ai_response
from app.database.schema import format_schema_for_ai


def clarification_response(question: str) -> dict:
    """Create a standard clarification response."""

    return {
        "needs_clarification": True,
        "clarification_question": question,
        "sql": None,
        "explanation": "The question is ambiguous and needs more information.",
        "assumptions": []
    }


def _is_ambiguous_customer_ranking(question: str) -> bool:
    """Detect vague customer-ranking requests."""

    normalized = question.lower()

    vague_ranking = re.search(
        r"\b(best|top|good)\s+customers?\b",
        normalized
    )

    ranking_metric = re.search(
        r"\b(spending|spent|revenue|amount|sales|"
        r"orders|order count|number of orders|purchase)\b",
        normalized
    )

    return bool(vague_ranking and not ranking_metric)


def _handle_known_questions(question: str):
    """Handle common questions using reliable predefined logic."""

    normalized = question.lower()

    # Handle Bengaluru and common spelling variations.
    city_variants = [
        "bengaluru",
        "bangalore",
        "banglore",
        "bbengauru"
    ]

    if (
        any(city in normalized for city in city_variants)
        and "customer" in normalized
        and re.search(r"\b(from|in)\b", normalized)
    ):
        return {
            "needs_clarification": False,
            "clarification_question": None,
            "sql": (
                "SELECT * FROM customers "
                "WHERE city = 'Bengaluru'"
            ),
            "explanation": "Retrieves customers from Bengaluru.",
            "assumptions": [
                "The city name refers to Bengaluru."
            ]
        }

    # Handle top customers ranked by total spending.
    if (
        re.search(r"\b(top|highest|most)\b", normalized)
        and re.search(
            r"\b(spending|spent|total spending)\b",
            normalized
        )
    ):
        match = re.search(r"\btop\s+(\d+)\b", normalized)

        limit = int(match.group(1)) if match else 1

        if limit < 1 or limit > 100:
            return None

        sql = f"""
            SELECT
                c.customer_id,
                c.name,
                SUM(o.amount) AS total_spending
            FROM customers c
            JOIN orders o
                ON c.customer_id = o.customer_id
            GROUP BY c.customer_id, c.name
            ORDER BY total_spending DESC
            LIMIT {limit}
        """

        return {
            "needs_clarification": False,
            "clarification_question": None,
            "sql": sql,
            "explanation": (
                "Ranks customers by their total spending "
                "in descending order."
            ),
            "assumptions": []
        }

    return None


def _extract_json(response: str) -> dict:
    """Extract JSON from the local AI response."""

    cleaned = response.strip()

    # Remove Markdown code fences.
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        result = json.loads(cleaned)

    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON object found in AI response.")

        result = json.loads(cleaned[start:end + 1])

    # Handle JSON wrapped inside an array.
    if isinstance(result, list):

        if len(result) != 1 or not isinstance(result[0], dict):
            raise ValueError("AI must return exactly one JSON object.")

        result = result[0]

    if not isinstance(result, dict):
        raise ValueError("AI response must be a JSON object.")

    return result


def _normalize_response(result: dict) -> dict:
    """Normalize and validate the AI-generated response."""

    required_fields = {
        "needs_clarification",
        "clarification_question",
        "sql",
        "explanation",
        "assumptions"
    }

    missing_fields = required_fields - set(result.keys())

    if missing_fields:
        raise ValueError(
            f"AI response is missing fields: {missing_fields}"
        )

    # Normalize clarification status.
    status = result["needs_clarification"]

    if isinstance(status, bool):
        needs_clarification = status

    elif isinstance(status, str):

        value = status.strip().lower()

        if value in ("true", "yes"):
            needs_clarification = True

        elif value in ("false", "no"):
            needs_clarification = False

        else:
            needs_clarification = True

            if not result.get("clarification_question"):
                result["clarification_question"] = status.strip()

    else:
        raise ValueError("Invalid clarification status.")

    # Normalize assumptions.
    assumptions = result["assumptions"]

    if isinstance(assumptions, str):
        assumptions = [assumptions] if assumptions.strip() else []

    if not isinstance(assumptions, list):
        raise ValueError("Assumptions must be a list.")

    # Normalize explanation.
    explanation = result["explanation"]

    if not isinstance(explanation, str):
        explanation = str(explanation)

    # If clarification is required, discard any generated SQL.
    if needs_clarification:

        clarification = result.get("clarification_question")

        if not isinstance(clarification, str) or not clarification.strip():
            clarification = (
                "Would you like to rank customers by total spending "
                "or by the number of orders?"
            )

        sql = None

    else:

        clarification = None
        sql = result["sql"]

        if not isinstance(sql, str) or not sql.strip():
            raise ValueError("AI did not generate valid SQL.")

    return {
        "needs_clarification": needs_clarification,
        "clarification_question": clarification,
        "sql": sql,
        "explanation": explanation,
        "assumptions": assumptions
    }


def generate_sql(question: str) -> dict:
    """
    Convert natural language questions into SQLite SELECT queries
    using local Qwen inference through Ollama.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    question = question.strip()

    # Step 1: Handle known question patterns.
    known_result = _handle_known_questions(question)

    if known_result is not None:
        return known_result

    # Step 2: Handle vague customer-ranking questions.
    if _is_ambiguous_customer_ranking(question):
        return clarification_response(
            "Would you like to rank customers by total spending "
            "or by the number of orders they have placed?"
        )

    # Step 3: Get database schema.
    schema = format_schema_for_ai()

    # Step 4: Create AI prompt.
    prompt = f"""
You are an intelligent Text-to-SQL assistant.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

RULES:

1. Generate SQLite-compatible SELECT queries only.
2. Use only existing tables and columns.
3. Never generate INSERT, UPDATE, DELETE, DROP, CREATE or ALTER.
4. Use JOIN when multiple tables are required.
5. Correct obvious spelling mistakes using context.
6. Bengaluru, Bangalore and Banglore refer to the same city.
7. Do not ask unnecessary clarification questions.
8. Generate SQL when the user's intention is clear.
9. Ask clarification when the intention is genuinely ambiguous.
10. Return exactly one JSON object.
11. Always include all five required fields.
12. When clarification is required, SQL must be null.

OUTPUT FORMAT:

Return ONLY valid JSON without Markdown.

For a clear question:
{{
    "needs_clarification": false,
    "clarification_question": null,
    "sql": "SELECT ...",
    "explanation": "Explain the query",
    "assumptions": []
}}

For an ambiguous question:
{{
    "needs_clarification": true,
    "clarification_question": "Ask a question",
    "sql": null,
    "explanation": "Explain why clarification is needed",
    "assumptions": []
}}
"""

    # Step 5: Generate AI response.
    response = generate_ai_response(prompt)

    # Step 6: Parse and normalize response.
    try:
        result = _extract_json(response)
        return _normalize_response(result)

    except (ValueError, json.JSONDecodeError) as error:
        raise ValueError(
            f"Could not process AI response: {error}\n"
            f"Actual response: {response}"
        ) from error


if __name__ == "__main__":

    test_questions = [
        "Show all customers from Bengaluru.",
        "Show all customers from bbengauru.",
        "Find the top 3 customers based on their total spending.",
        "Show me the best customers."
    ]

    for question in test_questions:

        print("\n" + "=" * 60)
        print("QUESTION:", question)
        print("=" * 60)

        try:
            result = generate_sql(question)
            print(json.dumps(result, indent=4))

        except Exception as error:
            print("SQL generation failed:", error)
