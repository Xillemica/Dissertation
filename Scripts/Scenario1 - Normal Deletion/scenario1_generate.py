import sqlite3
import random
import json

# configuration
DataBase_Name = "senario1_generate.py"
Log_Name = "senario1_deleted_reference_data.json"

# 1. Connect to SQLite 
conn = sqlite3.connect("senario1.db")
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

# 6. Put the generated messages into the table
cursor.executemany("""
    INSERT INTO messages (sender, content)
    VALUES (?, ?)
""", generated_messages)

# 7. Commit changes
conn.commit()
print("Successfully created senario1.db and added 1500 generated messages.")

# SENARIO 1 DELETION : deleting a specific range like IDs 200 to 400)
# get all records from before deletion to get a reference point (ground truth)

cursor.execute("SELECT id, sender, content, timestamp FROM messages WHERE id BETWEEN 200 AND 400")
deleted_record = cursor.fetchall()

# Export the ground truth that was deleted to JSON to be compared/verify against carver
ground_truth_data_senario1 = [
    {"id": r[0], "sender": r[1], "content": r[2], "timestamp": r[3]}
    for r in deleted_record
]

with open (Log_Name, "w") as f:
    json.dump(ground_truth_data_senario1, f, indent=4)

print(f"Logged {len(ground_truth_data_senario1)} target records to {Log_Name}")

# perform soft deletion
cursor.execute("DELETE FROM messages WHERE id BETWEEN 200 AND 400;")
conn.commit()

# close connection with no other writes
conn.close()
print("Senario 1 baseline generation completed. Database is ready for carving test.")
