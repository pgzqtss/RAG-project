import mysql.connector
from config import (
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_USER,
    DATABASE_NAME
)

def connect_to_database():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=DATABASE_NAME
    )