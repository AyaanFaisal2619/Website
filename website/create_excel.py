import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('listings.db')

# Query to fetch all listings
query = ' SELECT * FROM listings'

# Fetch data into a pandas DataFrame
df = pd.read_sql_query(query, conn)
print(df)
# Close the database connection
conn.close()

# Create an Excel writer object
excel_writer = pd.ExcelWriter('listings.xlsx', engine='openpyxl')

# Write the DataFrame to the Excel file
df.to_excel(excel_writer, sheet_name='Listings', index=False)

# Save the Excel file
excel_writer.close()  # Corrected line

print('Excel file "listings.xlsx" created successfully.')
