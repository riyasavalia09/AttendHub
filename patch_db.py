
import mysql.connector
from config import Config
import sys

def patch_db():
    print('Patching Database...')
    
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            port=Config.MYSQL_PORT,
            database=Config.MYSQL_DATABASE  # Connect directly to DB
        )
        cursor = conn.cursor()
        
        patch_files = [
            'db_patch_reports.sql',
            'db_patch_university_profile.sql',
            'db_patch_timetable_sunday.sql',
            'db_patch_password_reset.sql',
            'db_patch_lecture_state.sql',
        ]

        for patch_file in patch_files:
            try:
                with open(patch_file, 'r') as f:
                    sql_script = f.read()
            except FileNotFoundError:
                print(f'Warning: {patch_file} not found, skipping.')
                continue

            print(f'Executing SQL script: {patch_file} ...')
            # Simple split by semicolon
            statements = sql_script.split(';')

            for statement in statements:
                if statement.strip():
                    try:
                        cursor.execute(statement)
                        print(f"Executed: {statement[:60]}...")
                    except mysql.connector.Error as err:
                        print(f"Error executing statement: {err}")
                    
        conn.commit()
        cursor.close()
        conn.close()
        print('Database patched successfully.')
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == '__main__':
    patch_db()
