import psycopg2
from psycopg2 import sql

# Define your PostgreSQL connection parameters
database_name = "flyingbox_database"
database_user = "postgres"
database_password = "flyingbox"
database_host = "34.22.206.231"  # Typically, this is the IP address or domain of your PostgreSQL instance
database_port = "5432"  # The default PostgreSQL port is 5432

# Connect to the database
conn = psycopg2.connect(
    dbname=database_name,
    user=database_user,
    password=database_password,
    host=database_host,
    port=database_port
)

# Create a cursor
cursor = conn.cursor()

# Define SQL commands to create tables
create_users_table = sql.SQL("""
    CREATE TABLE IF NOT EXISTS Test (
        message_id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        message VARCHAR(250) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Execute the SQL commands to create tables
cursor.execute(create_users_table)

# Commit the changes to the database
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()
print("connection is good, all ok")
