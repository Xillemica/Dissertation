import sqlite3
import random

# 1. Connect to SQLite 
conn = sqlite3.connect("Database.db")
cursor = conn.cursor()

# 2. Drop the old table if it exists so we always start fresh
cursor.execute("DROP TABLE IF EXISTS messages")

# 3. Create table to store messages
cursor.execute("""
    CREATE TABLE messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

# 4. Generate sample messages
senders = ["Amy", "Samantha", "John", "David", "Alice", "Bob", "Charlie", "System"]
phrases = [
    "Hey, did you get my previous email?",
    "Meeting rescheduled to 3 PM tomorrow.",
    "Please send over the updated SQLite report.",
    "Your verification code is " + str(random.randint(1000, 9999)),
    "Let's catch up over coffee this afternoon.",
    "Project status: all tests are green.",
    "Can you double-check the database migration script?",
    "Thanks for sending that file over!"
]

# 5. Insert 1,500 baseline records
generated_messages = []
for _ in range(1500):
    generated_messages.append((random.choice(senders), random.choice(phrases)))

# 6. Put the messages into the table
cursor.executemany("""
    INSERT INTO messages (sender, content)
    VALUES (?, ?)
""", generated_messages)

# 7. Commit changes and close
conn.commit()
conn.close()

print("Successfully created Database.db with 1500 messages.")