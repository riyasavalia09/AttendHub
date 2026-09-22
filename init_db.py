
import mysql.connector
from config import Config
import sys

def init_db():
    print('Initializing Database...')
    print(f'Host: {Config.MYSQL_HOST}, User: {Config.MYSQL_USER}')
    
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            port=Config.MYSQL_PORT
        )
        cursor = conn.cursor()
        
        try:
            with open('db.sql', 'r') as f:
                sql_script = f.read()
        except FileNotFoundError:
            print('Error: db.sql file not found.')
            return

        print('Executing SQL script...')
        # Simple split by semicolon
        statements = sql_script.split(';')
        
        for statement in statements:
            stmt = statement.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                    conn.commit()
                except mysql.connector.Error as err:
                    print(f'Error executing: {stmt[:50]}... \nMessage: {err}')
                    # Don't exit, might be 'already exists' which is fine
        
        print('Database operations completed.')
        
    except mysql.connector.Error as err:
        print(f'Connection Error: {err}')
        print('Check credentials.')
        
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == '__main__':
    init_db()

