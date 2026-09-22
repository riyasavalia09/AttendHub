import mysql.connector
from mysql.connector import pooling, Error
from config import Config

class DBConnection:
    """Singleton wrapper for MySQL Connection Pool"""
    _pool = None

    @classmethod
    def _initialize_pool(cls):
        if cls._pool is None:
            try:
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name="attendhub_pool",
                    pool_size=5,
                    pool_reset_session=True,
                    host=Config.MYSQL_HOST,
                    port=Config.MYSQL_PORT,
                    user=Config.MYSQL_USER,
                    password=Config.MYSQL_PASSWORD,
                    database=Config.MYSQL_DATABASE
                )
            except Error as err:
                raise Exception(f"Failed to initialize database pool: {err}")

    @classmethod
    def get_connection(cls):
        """Get a connection from the pool"""
        if cls._pool is None:
            cls._initialize_pool()
        
        try:
            return cls._pool.get_connection()
        except Error as err:
            raise Exception(f"Failed to get connection: {err}")

def get_connection():
    """Utility function to get DB connection"""
    return DBConnection.get_connection()

def close_connection(conn):
    """Utility function to close DB connection (return to pool)"""
    try:
        if conn and conn.is_connected():
            conn.close()
    except Error as err:
        print(f"Error closing connection: {err}")
