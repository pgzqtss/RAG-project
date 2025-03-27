# mysql_connection.py
import mysql.connector
from mysql.connector import errorcode
from config import (
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_USER,
    DATABASE_NAME
)
import logging
import time

logger = logging.getLogger(__name__)

def connect_to_database(retries=3):
    attempt = 0
    while attempt < retries:
        try:
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=DATABASE_NAME,
                connection_timeout=5
            )
            logger.info("successful connection to database")
            return conn
        except mysql.connector.Error as err:
            attempt += 1
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logger.error("database username or password is incorrect")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logger.error(f"database{DATABASE_NAME}not exist")
            else:
                logger.error(f"fail connect: {str(err)}")
            
            if attempt < retries:
                logger.info(f"number {attempt} trying...")
                time.sleep(2**attempt)  
                
    raise RuntimeError("database connection failed")