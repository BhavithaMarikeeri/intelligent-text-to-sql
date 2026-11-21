
from app.core.llm import generate_ai_response

try:
    result = generate_ai_response("Reply with exactly: Gemini is working!")
    print("\nSUCCESS:")
    print(result)

except Exception as error:
    print("\nERROR:")
    print(error)
