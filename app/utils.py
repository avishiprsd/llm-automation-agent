import os
from dotenv import load_dotenv
import openai


def query_llm(prompt):
    load_dotenv()

    """Queries the LLM (GPT-4o-Mini) and returns a response."""
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise ValueError("API Key is missing! Check your .env file or environment variables.")

    try:
        response = openai.Completion.create(
            model="gpt-4o-mini",
            prompt=prompt,
            max_tokens=100
        )
        return response.choices[0].text.strip()
    except openai.error.OpenAIError as e:
        return f"LLM Error: {str(e)}"

def validate_file_path(path):
    """Ensures the file path is inside the /data directory (Security Check)."""
    base_dir = os.path.abspath("data")
    full_path = os.path.abspath(path)

    if not full_path.startswith(base_dir):
        return False  # Prevents access outside `/data`
    return True
