import sqlite3
import json

# Connect to the SQLite database
conn = sqlite3.connect('data/db-name.db')
cursor = conn.cursor()

# Execute SQL query to fetch data from the database
cursor.execute('SELECT * FROM message')

# Fetch all rows from the result set
rows = cursor.fetchall()

data = []
for row in rows:
    text = {
        "id": row[0],
        "timestamp": row[1],
        "recipient": row[2],
        "message": row[3],
        "flags": row[4],
        "sender": row[6],
        "all_data": row
    }
    data.append(text)

# Convert data to JSON
json_data = json.dumps(data, indent=4)

# Write JSON data to a file
with open('imessage_db2.json', 'w') as f:
    f.write(json_data)

# Close the cursor and the connection
cursor.close()
conn.close()