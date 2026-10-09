import sqlite3
import random
import json

DataBase_Name = "scenario4_vacuum.db"
Log_Deleted = "senario4_deleted_reference_data.json"

conn = sqlite3.connect(DataBase_Name)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS messages")
cursor.execute("""
    CREATE TABLE messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

senders = ["Amy", "Samantha", "John", "David", "Alice", "Bob", "Charlie", "System"]
phrases = ["Meeting at 3 PM", "Project status update", "Verification code 1234", "Coffee today?"]

# 1. Insert 1,500 baseline records
initial_messages = [(random.choice(senders), random.choice(phrases)) for _ in range(1500)]
cursor.executemany("INSERT INTO messages (sender, content) VALUES (?, ?)", initial_messages)
conn.commit()

# 2. Log ground truth and delete IDs 200-400
cursor.execute("SELECT id, sender, content, timestamp FROM messages WHERE id BETWEEN 200 AND 400")
deleted_records = cursor.fetchall()

deleted_ground_truth = [
    {"id": r[0], "sender": r[1], "content": r[2], "timestamp": r[3]}
    for r in deleted_records
]

with open(Log_Deleted, "w") as f:
    json.dump(deleted_ground_truth, f, indent=4)

cursor.execute("DELETE FROM messages WHERE id BETWEEN 200 AND 400;")
conn.commit()

# 3. RUN VACUUM (Wipes unallocated space and rebuilds B-tree)
print("Executing VACUUM to compact database and wipe slack space...")
cursor.execute("VACUUM;")
conn.commit()

conn.close()
print("Scenario 4 setup complete. Unallocated space zeroed out.")