import sqlite3

# 1. Connect to SQLite 
conn = sqlite3.connect("messages1234.db")
cursor = conn.cursor()

# 2. Drop the old table if it exists so we always start fresh
cursor.execute("DROP TABLE IF EXISTS messages")

# 3. Create table to store messages (with commas and correct spelling!)
cursor.execute("""
    CREATE TABLE messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

# 4. Generate sample messages
generated_messages = [
    ("Amy", "Hey there! This is my first message."),
    ("Samantha", "Hi Amy, testing the message generation"),
    ("System", "Database successfully updated!"),
]

# 5. Put the generated messages into the table
cursor.executemany("""
    INSERT INTO messages (sender, content)
    VALUES (?, ?)
""", generated_messages)

# 6. Commit changes and close connection
conn.commit()
conn.close()

print("Successfully created messages1234.db and added generated messages.")