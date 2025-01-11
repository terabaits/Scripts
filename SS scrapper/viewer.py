import sqlite3

# Connect to the database
conn = sqlite3.connect('listings.db')
cursor = conn.cursor()

# Execute a query to retrieve all listings
cursor.execute("SELECT * FROM listings")  # Replace 'listings' with your actual table name

# Fetch and print all rows
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close the connection
conn.close()
