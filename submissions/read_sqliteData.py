import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect("user_data.db")

# List of expected tables
tables = ["User", "Skills", "LearningGoal", "Topic"]

# Print each table's content as a pandas DataFrame
for table in tables:
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table};", conn)
        print(f"\n📋 Table: {table}")
        print(df)
    except Exception as e:
        print(f"\n⚠️ Could not retrieve table '{table}': {e}")

# Close connection
conn.close()
