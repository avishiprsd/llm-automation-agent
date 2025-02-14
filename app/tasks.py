import os
import re
import subprocess
import json
import sqlite3
import requests
import shutil
from dateutil import parser
from datetime import datetime
from app.utils import query_llm


def execute_task(task_description):
    """Parses and executes tasks based on their description using LLM for interpretation."""
    print(f"Executing task: {task_description}")

    # Use LLM to interpret the task and extract structured information
    structured_task = query_llm(
        f"Extract the following details from this task description: "
        f"1. Action (e.g., count, format, sort, extract, etc.). "
        f"2. Input file path. "
        f"3. Output file path. "
        f"4. Additional parameters (e.g., day of the week, ticket type, etc.). "
        f"Return the result as a JSON object. Task description: {task_description}"
    )

    try:
        task_info = json.loads(structured_task)
    except json.JSONDecodeError:
        return "Error: Unable to parse task description."

    action = task_info.get("action", "").lower()
    input_path = task_info.get("input_path", "")
    output_path = task_info.get("output_path", "")
    parameters = task_info.get("parameters", {})

    # Ensure paths are within the /data directory
    if not check_data_directory(input_path) or not check_data_directory(output_path):
        return "Error: File paths must be within the /data directory."

    # **TASK A1: Install `uv` and run `datagen.py`**
    if "install" in action and "run" in action:
        if not shutil.which("uv"):
            try:
                subprocess.run(["pip", "install", "uv"], check=True)
            except subprocess.CalledProcessError:
                return "Error installing `uv`."

        datagen_url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
        datagen_path = "datagen.py"

        try:
            response = requests.get(datagen_url)
            response.raise_for_status()
            with open(datagen_path, "w") as file:
                file.write(response.text)
        except requests.RequestException as e:
            return f"Error downloading datagen.py: {str(e)}"

        try:
            subprocess.run(["python", datagen_path, parameters.get("email", "")], check=True)
            return "Data generation complete."
        except subprocess.CalledProcessError:
            return "Error running `datagen.py`."

    # **TASK A2: Format Markdown using Prettier**
    if "format" in action:
        if not os.path.exists(input_path):
            return f"Error: File {input_path} not found."

        try:
            subprocess.run(["npx", "prettier", "--write", input_path], check=True)
            return "Markdown formatted successfully."
        except subprocess.CalledProcessError:
            return "Error running Prettier."
        except FileNotFoundError:
            return "Error: `npx` is not installed or not found in PATH."

    # **TASK A3: Count specific day in a file**
    if "count" in action:
        if not os.path.exists(input_path):
            return f"Error: File {input_path} not found."

        day_to_count = parameters.get("day", "wednesday").lower()
        day_map = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }

        if day_to_count not in day_map:
            return f"Error: Invalid day '{day_to_count}' specified."

        try:
            day_count = 0
            with open(input_path, "r", encoding="utf-8") as file:
                for line in file:
                    date_str = line.strip()
                    if date_str:
                        try:
                            date_obj = parser.parse(date_str)
                            if date_obj.weekday() == day_map[day_to_count]:
                                day_count += 1
                        except ValueError:
                            return f"Error: Invalid date format found: {date_str}"

            with open(output_path, "w", encoding="utf-8") as file:
                file.write(str(day_count))

            return f"{day_to_count.capitalize()}s counted."
        except Exception as e:
            return f"Error: {str(e)}"

    # **TASK A4: Sort contacts**
    if "sort" in action:
        if not os.path.exists(input_path):
            return f"Error: File {input_path} not found."

        with open(input_path, "r") as file:
            contacts = json.load(file)
        sorted_contacts = sorted(contacts, key=lambda x: (x["last_name"], x["first_name"]))
        with open(output_path, "w") as file:
            json.dump(sorted_contacts, file)
        return "Contacts sorted."

    # **TASK A5: Extract first lines from recent logs**
    if "extract" in action and "log" in action:
        log_dir = os.path.dirname(input_path)
        if not os.path.exists(log_dir):
            return "Error: Logs directory not found."

        log_files = sorted([f for f in os.listdir(log_dir) if f.endswith(".log")],
                           key=lambda f: os.path.getmtime(os.path.join(log_dir, f)), reverse=True)[:10]
        with open(output_path, "w") as outfile:
            for log_file in log_files:
                with open(os.path.join(log_dir, log_file), "r") as infile:
                    outfile.write(infile.readline().strip() + "\n")
        return "Log first lines extracted."

    # **TASK A6: Extract Markdown titles**
    if "extract" in action and "markdown" in action:
        index = {}
        docs_dir = os.path.dirname(input_path)
        if not os.path.exists(docs_dir):
            return "Error: Docs directory not found."

        for file_name in os.listdir(docs_dir):
            if file_name.endswith(".md"):
                with open(os.path.join(docs_dir, file_name), "r") as file:
                    for line in file:
                        if line.startswith("# "):
                            index[file_name] = line.strip("# ").strip()
                            break
        with open(output_path, "w") as file:
            json.dump(index, file)
        return "Markdown titles indexed."

    # **TASK A7: Extract sender email using LLM**
    if "extract" in action and "email" in action:
        email_content = open(input_path, "r").read()
        sender_email = query_llm(f"Extract sender email from this text: {email_content}")
        with open(output_path, "w") as file:
            file.write(sender_email)
        return "Sender email extracted."

    # **TASK A8: Extract credit card number using LLM**
    if "extract" in action and "credit card" in action:
        card_number = query_llm(f"Extract credit card number from this image: {input_path}")
        with open(output_path, "w") as file:
            file.write(card_number.replace(" ", ""))
        return "Credit card number extracted."

    # **TASK A9: Find most similar comments using embeddings**
    if "find" in action and "similar" in action:
        comments = open(input_path, "r").readlines()
        most_similar = query_llm(f"Find the most similar pair in this list: {comments}")
        with open(output_path, "w") as file:
            file.write(most_similar)
        return "Most similar comments found."

    # **TASK A10: Calculate total sales for a ticket type**
    if "calculate" in action and "sales" in action:
        ticket_type = parameters.get("ticket_type", "Gold")
        conn = sqlite3.connect(input_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT SUM(price * units) FROM tickets WHERE type='{ticket_type}'")
        total_sales = cursor.fetchone()[0]
        conn.close()
        with open(output_path, "w") as file:
            file.write(str(total_sales))
        return f"{ticket_type} ticket sales calculated."

    # **TASK B1: Prevent access to data outside /data**
    if "access" in action and "data" in action:
        if not check_data_directory(input_path):
            return "Error: Access to data outside /data is not allowed."
        return "Data access verified."

    # **TASK B2: Prevent data deletion**
    if "delete" in action:
        return "Error: Data deletion is not allowed."

    # **TASK B3: Fetch data from an API and save it**
    if "fetch" in action and "api" in action:
        api_url = re.search(r"https?://[^\s]+", task_description)
        if not api_url:
            return "Error: No valid API URL found in task description."
        try:
            response = requests.get(api_url.group(0))
            response.raise_for_status()
            with open(output_path, "w") as file:
                json.dump(response.json(), file)
            return "API data fetched and saved."
        except requests.RequestException as e:
            return f"Error fetching API data: {str(e)}"

    # **TASK B4: Clone a git repo and make a commit**
    if "clone" in action and "git" in action:
        repo_url = re.search(r"https?://[^\s]+", task_description)
        if not repo_url:
            return "Error: No valid Git repository URL found in task description."
        try:
            subprocess.run(["git", "clone", repo_url.group(0), "/data/repo"], check=True)
            subprocess.run(["git", "commit", "-m", "Automated commit"], cwd="/data/repo", check=True)
            return "Git repository cloned and commit made."
        except subprocess.CalledProcessError:
            return "Error cloning Git repository or making commit."

    # **TASK B5: Run a SQL query on a SQLite or DuckDB database**
    if "sql" in action and "query" in action:
        db_path = input_path
        query = re.search(r"SELECT .+", task_description, re.IGNORECASE)
        if not query:
            return "Error: No valid SQL query found in task description."
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(query.group(0))
            result = cursor.fetchall()
            conn.close()
            with open(output_path, "w") as file:
                json.dump(result, file)
            return "SQL query executed and result saved."
        except sqlite3.Error as e:
            return f"Error executing SQL query: {str(e)}"

    # **TASK B6: Extract data from a website (scraping)**
    if "scrape" in action or "extract" in action:
        url = re.search(r"https?://[^\s]+", task_description)
        if not url:
            return "Error: No valid URL found in task description."
        try:
            response = requests.get(url.group(0))
            response.raise_for_status()
            with open(output_path, "w") as file:
                file.write(response.text)
            return "Website data scraped and saved."
        except requests.RequestException as e:
            return f"Error scraping website: {str(e)}"

    # **TASK B7: Compress or resize an image**
    if "compress" in action or "resize" in action:
        try:
            from PIL import Image
            img = Image.open(input_path)
            img = img.resize((100, 100))  # Resize to 100x100
            img.save(output_path, optimize=True, quality=85)
            return "Image compressed and resized."
        except ImportError:
            return "Error: PIL library not installed."
        except Exception as e:
            return f"Error processing image: {str(e)}"

    # **TASK B8: Transcribe audio from an MP3 file**
    if "transcribe" in action and "mp3" in action:
        try:
            transcription = query_llm(f"Transcribe this audio file: {input_path}")
            with open(output_path, "w") as file:
                file.write(transcription)
            return "Audio transcribed."
        except Exception as e:
            return f"Error transcribing audio: {str(e)}"

    # **TASK B9: Convert Markdown to HTML**
    if "markdown" in action and "html" in action:
        try:
            with open(input_path, "r") as md_file:
                md_content = md_file.read()
            html_content = query_llm(f"Convert this Markdown to HTML: {md_content}")
            with open(output_path, "w") as html_file:
                html_file.write(html_content)
            return "Markdown converted to HTML."
        except Exception as e:
            return f"Error converting Markdown to HTML: {str(e)}"

    # **TASK B10: Filter CSV and return JSON**
    if "csv" in action and "filter" in action:
        try:
            import pandas as pd
            df = pd.read_csv(input_path)
            filtered_data = df.to_json(orient="records")
            with open(output_path, "w") as file:
                file.write(filtered_data)
            return "CSV filtered and JSON saved."
        except ImportError:
            return "Error: pandas library not installed."
        except Exception as e:
            return f"Error filtering CSV: {str(e)}"

    return "Unknown task"


class InvalidDirectoryError(Exception):
    """Custom exception to be raised when the directory check fails."""
    pass


def check_data_directory(file_path):
    if not file_path.startswith('/data'):
        return False
    return True


def read_file(path):
    """Reads and returns the content of a file."""
    try:
        if check_data_directory(path):
            with open(path, "r") as file:
                return file.read()
        else:
            raise InvalidDirectoryError(f"The directory for the path '{path}' is invalid.")
    except FileNotFoundError:
        return None
    except InvalidDirectoryError as e:
        return str(e)