import sqlite3
import random
import json

# File Configuration
DataBase_Name = "senario3_wal.db"
Log_Deleted = "senario3_deleted_reference_data.json"
Log_WAL_Frames = "senario3_wal_uncheckpointed_ground_truth.json"

# 1. Connect to SQLite
conn = sqlite3.connect(DataBase_Name)
cursor = conn.cursor()

# 2. Enable Write-Ahead Logging Mode
cursor.execute("PRAGMA journal_mode=WAL;")
mode = cursor.fetchone()[0]
print(f"[Setup] Database mode set to: {mode.upper()}")

# 3. Disable Automatic Checkpointing so WAL frames accumulate on disk
cursor.execute("PRAGMA wal_autocheckpoint=0;")

# 4. Re-initialize table
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
initial_messages = [(random.choice(senders), random.choice(phrases)) for _ in range(1500)]
cursor.executemany("INSERT INTO messages (sender, content) VALUES (?, ?)", initial_messages)
conn.commit()
print(f"Inserted 1,500 baseline records into {DataBase_Name}.")

# Force a checkpoint here so baseline records push to main .db file
cursor.execute("PRAGMA wal_checkpoint(FULL);")

# 6. Soft delete IDs 200 to 400
cursor.execute("SELECT id, sender, content, timestamp FROM messages WHERE id BETWEEN 200 AND 400")
deleted_records = cursor.fetchall()

deleted_ground_truth = [
    {"id": r[0], "sender": r[1], "content": r[2], "timestamp": r[3]}
    for r in deleted_records
]

with open(Log_Deleted, "w") as f:
    json.dump(deleted_ground_truth, f, indent=4)

cursor.execute("DELETE FROM messages WHERE id BETWEEN 200 AND 400;")
conn.commit()  # Commits to WAL file instaed of main .db file
print(f"Deleted IDs 200-400 into uncheckpointed WAL file. Ground truth saved to {Log_Deleted}.")

# 7. Insert 50 uncheckpointed records into WAL file
wal_uncheckpointed_messages = [
    ("WAL_User", f"WAL transaction message {i} sitting in uncheckpointed frame.")
    for i in range(1, 51)
]

cursor.executemany("INSERT INTO messages (sender, content) VALUES (?, ?)", wal_uncheckpointed_messages)
conn.commit()

# Capture ground truth for the uncheckpointed WAL writes
cursor.execute("SELECT id, sender, content, timestamp FROM messages ORDER BY id DESC LIMIT 50")
wal_records = cursor.fetchall()

wal_ground_truth = [
    {"id": r[0], "sender": r[1], "content": r[2], "timestamp": r[3]}
    for r in wal_records
]

with open(Log_WAL_Frames, "w") as f:
    json.dump(wal_ground_truth, f, indent=4)

print(f"Inserted 50 uncheckpointed WAL records. Ground truth saved to {Log_WAL_Frames}.")

# Leave database connection closed without syncing WAL to .db
conn.close()
print("Scenario 3 setup complete! scenario3_wal.db and scenario3_wal.db-wal are ready.")