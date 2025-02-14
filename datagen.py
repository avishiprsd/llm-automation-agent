import os
import sys
import json
import random
from datetime import datetime, timedelta

def create_directories():
    """Creates required directories if they do not exist."""
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/docs", exist_ok=True)

def generate_dates():
    """Generate a file containing random dates."""
    start_date = datetime(2020, 1, 1)
    with open("data/dates.txt", "w") as f:
        for _ in range(100):  # Generate 100 random dates
            random_date = start_date + timedelta(days=random.randint(0, 1825))  # 5 years range
            f.write(random_date.strftime("%Y-%m-%d") + "\n")

def generate_contacts():
    """Generate a JSON file containing sample contacts."""
    contacts = [
        {"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com"},
        {"first_name": "Bob", "last_name": "Johnson", "email": "bob@example.com"},
        {"first_name": "Charlie", "last_name": "Brown", "email": "charlie@example.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=4)

def generate_logs():
    """Generate random log files with timestamps."""
    for i in range(10):  # Create 10 log files
        filename = f"data/logs/log_{i}.log"
        with open(filename, "w") as f:
            for _ in range(5):  # 5 log entries per file
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} - Log entry {random.randint(1000, 9999)}\n")

def generate_markdown():
    """Generate sample Markdown files with H1 headers."""
    md_content = [
        "# Home\nWelcome to the documentation.\n",
        "# Large Language Models\nThis file explains LLMs.\n",
    ]
    for i, content in enumerate(md_content):
        filename = f"data/docs/file_{i}.md"
        with open(filename, "w") as f:
            f.write(content)

def generate_email():
    """Generate a sample email file."""
    email_content = """From: sender@example.com\nTo: receiver@example.com\nSubject: Test Email\n\nHello, this is a test email."""
    with open("data/email.txt", "w") as f:
        f.write(email_content)

def generate_credit_card_image():
    """Placeholder function for a credit card image (Actual OCR needed)."""
    with open("data/credit-card.png", "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n...")  # Minimal PNG header for testing

def generate_comments():
    """Generate a file with random comments."""
    comments = [
        "This is an amazing project!",
        "I love this tool!",
        "The API could be improved.",
        "Nice work, keep it up!",
        "This tool is not working as expected.",
    ]
    with open("data/comments.txt", "w") as f:
        f.write("\n".join(comments))

def generate_ticket_sales():
    """Generate a sample SQLite database for ticket sales."""
    import sqlite3
    conn = sqlite3.connect("data/ticket-sales.db")
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY,
            type TEXT,
            units INTEGER,
            price REAL
        )
    """)
    
    # Insert sample data
    sample_data = [
        ("Gold", 2, 50.0),
        ("Silver", 5, 30.0),
        ("Gold", 3, 50.0),
        ("Bronze", 4, 20.0),
    ]
    cursor.executemany("INSERT INTO tickets (type, units, price) VALUES (?, ?, ?)", sample_data)
    conn.commit()
    conn.close()

def main():
    """Main function to generate all required data."""
    if len(sys.argv) < 2:
        print("Usage: python datagen.py <user.email>")
        sys.exit(1)

    user_email = sys.argv[1]
    print(f"Generating data for user: {user_email}")

    create_directories()
    generate_dates()
    generate_contacts()
    generate_logs()
    generate_markdown()
    generate_email()
    generate_credit_card_image()
    generate_comments()
    generate_ticket_sales()

    print("Data generation complete.")

if __name__ == "__main__":
    main()
