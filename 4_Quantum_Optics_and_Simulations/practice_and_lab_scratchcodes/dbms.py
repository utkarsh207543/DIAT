import sys
import math
import random
import threading
import time
import re
import sqlite3
import csv

import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("example.db")

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Create a table
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    email TEXT
                )''')

# Insert data into the table
cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)", ("john_doe", "john@example.com"))
cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)", ("jane_smith", "jane@example.com"))

# Commit the changes to the database
conn.commit()

# Query data from the table
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

# Print the results
for row in rows:
    print(f"ID: {row[0]}, Username: {row[1]}, Email: {row[2]}")

# Close the cursor and the database connection
cursor.close()
conn.close()

