import sqlite3
import random
import json

# configuration
DB_NAME = "senario2.db"
Log_Deleted = "senario2_deleted_reference_data.json"
Log_New = "senario2_inserted_reference_data.json"

# 1. Connect to SQLite (using DB_NAME consistently)
conn = sqlite3.connect(DB_NAME)
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

# 5. insert 1,500 baseline records
generated_messages = [
    (random.choice(senders), random.choice(phrases))
    for _ in range(1500)
]

# 6. Put the generated messages into the table
cursor.executemany("""
    INSERT INTO messages (sender, content)
    VALUES (?, ?)
""", generated_messages)

# 7. Commit changes
conn.commit()
print(f"Successfully created {DB_NAME} and added 1500 generated messages.")

# SCENARIO 2
# delete 200-400 messages
# perform continous allocation by adding 100 messages after deleting
cursor.execute("SELECT id, sender, content, timestamp FROM messages WHERE id BETWEEN 200 AND 400")
deleted_record = cursor.fetchall()

# Export the ground truth that was deleted to JSON
ground_truth_data_senario2 = [
    {"id": r[0], "sender": r[1], "content": r[2], "timestamp": r[3]}
    for r in deleted_record
]

with open(Log_Deleted, "w") as f:
    json.dump(ground_truth_data_senario2, f, indent=4)

# Perform deletion
cursor.execute("DELETE FROM messages WHERE id BETWEEN 200 AND 400;")
conn.commit()
print(f"Deleted {len(ground_truth_data_senario2)} records (IDs 200-400) and saved ground truth to {Log_Deleted}")

# Perform continuous allocation
new_records_to_insert = [
    ("System_New", f"Continuous allocation message {i} - Overwriting test payload.")
    for i in range(1, 101)
]

cursor.executemany("INSERT INTO messages (sender, content) VALUES (?, ?)", new_records_to_insert)
conn.commit()

# Log newly inserted records to verify their IDs/locations
cursor.execute("SELECT id, sender, content, timestamp FROM messages ORDER BY id DESC LIMIT 100")
new_inserted_records = cursor.fetchall()

new_ground_truth = [
    {"id": r[0], "sender": r[1], "content": r[2], "timestamp": r[3]}
    for r in new_inserted_records
]

with open(Log_New, "w") as f:
    json.dump(new_ground_truth, f, indent=4)

# Close connection
conn.close()
print(f"Inserted 100 new records after deletion and saved ground truth to {Log_New}.")
print("Scenario 2 baseline generation completed. Database is ready for carving test.")