from db_connection import get_connection, close_connection
from exceptions.custom_exceptions import DatabaseError
from mysql.connector import Error

class ReportRepository:
    """
    Repository for interacting with the 'reports' table.
    """
    
    @staticmethod
    def create(university_id, report_type, generated_by, coverage_period, file_path):
        """Creates a new report entry."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            sql = """
                INSERT INTO reports (university_id, report_type, generated_by, coverage_period, file_path)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (university_id, report_type, generated_by, coverage_period, file_path))
            conn.commit()
            return cursor.lastrowid
        except Error as err:
            raise DatabaseError(f"Failed to create report: {err}")
        finally:
            try:
                if conn:
                    cursor.close()
            finally:
                close_connection(conn)

    @staticmethod
    def get_all_by_university(university_id, limit=20):
        """Retrieves recent reports for a university."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT * FROM reports 
                WHERE university_id = %s 
                ORDER BY created_at DESC
                LIMIT %s
            """
            cursor.execute(sql, (university_id, limit))
            return cursor.fetchall()
        except Error as err:
            raise DatabaseError(f"Failed to fetch reports: {err}")
        finally:
            try:
                if conn:
                    cursor.close()
            finally:
                close_connection(conn)
