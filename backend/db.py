import mysql.connector
from mysql.connector import Error

def get_conn():
    try:
        connection = mysql.connector.connect(
            host="217.21.80.3",
            user="u341672715_python_code",                    # change if your MySQL user is different
            password="F!ntree@2026", # put your password
            database="u341672715_python_code"
        )
        return connection
    except Error as e:
        print("MySQL Connection Error:", e)
        return None
