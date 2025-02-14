import os
import openai

def query_llm(prompt):
    """Queries the LLM (GPT-4o-Mini) and returns a response."""
    openai.api_key = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDM4OTNAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.kPdd7741VFTipdu3k6uOW6dzg8LPaSULwYgbD14y16E"#os.getenv("AIPROXY_TOKEN")  # Ensure token is set via env variable

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
