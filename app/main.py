
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4

from app.services.query_pipeline import process_question

app = FastAPI(
    title="Intelligent Text-to-SQL API",
    description="Convert natural language into safe SQL queries.",
    version="1.0.0"
)

# Temporary storage for questions awaiting clarification
pending_questions = {}


class QueryRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=1000
    )
    conversation_id: str | None = None


@app.get("/")
def home():
    return {
        "message": "Intelligent Text-to-SQL API is running!"
    }


@app.post("/query")
def generate_query(request: QueryRequest):

    conversation_id = request.conversation_id
    question = request.question

    # Check whether this is a follow-up answer
    if conversation_id and conversation_id in pending_questions:

        original_question = pending_questions[conversation_id]

        question = (
            f"Original question: {original_question}\n"
            f"User's clarification: {request.question}"
        )

    result = process_question(question)

    # AI needs another clarification
    if result.get("needs_clarification"):

        if not conversation_id:
            conversation_id = str(uuid4())

        pending_questions[conversation_id] = question

        result["conversation_id"] = conversation_id

        return result

    # Remove completed conversation from temporary storage
    if conversation_id:
        pending_questions.pop(conversation_id, None)

    if "error" in result:
        raise HTTPException(
            status_code=500,
            detail=result["error"]
        )

    result["conversation_id"] = conversation_id

    return result
