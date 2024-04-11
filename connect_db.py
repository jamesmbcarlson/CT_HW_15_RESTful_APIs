import mysql.connector
from mysql.connector import Error

def connect_db():

    try:
        conn = mysql.connector.connect(
            database = "fitness_schedule_db",
            user = "root",
            password = "Password123!",
            host = "localhost"
        )

        print("Connected to database successfully")
        return conn
    
    except Error as e:
        print(f"Error: {e}")
        return None
