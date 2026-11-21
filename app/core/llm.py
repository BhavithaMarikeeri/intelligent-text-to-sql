
import requests
from app.core.config import OLLAMA_BASE_URL, OLLAMA_MODEL


def generate_ai_response(prompt: str) -> str:
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1
                }
            },
            timeout=180
        )

        response.raise_for_status()

        data = response.json()
        generated_text = data.get("response", "").strip()

        if not generated_text:
            raise RuntimeError("Ollama returned an empty response.")

        return generated_text

    except requests.RequestException as error:
        raise RuntimeError(
            f"Could not connect to Ollama. "
            f"Make sure Ollama is running: {error}"
        ) from error
