from db_connection import get_connection, close_connection
from exceptions.custom_exceptions import DatabaseError
from mysql.connector import Error

class FacultyRepository:
    """
    Repository for accessing 'faculty' table.
    """
    
    @staticmethod
    def create_faculty(university_id, name, email, department, password_hash):
        """Creates a new faculty account."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO faculty (university_id, name, email, department, password_hash, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (university_id, name, email, department, password_hash, True))
            conn.commit()
            
            return cursor.lastrowid
            
        except Error as e:
            raise DatabaseError(f"Failed to create faculty: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_by_email(email):
        """Finds faculty by email."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM faculty WHERE email = %s"
            cursor.execute(query, (email,))
            
            return cursor.fetchone()
            
        except Error as e:
            raise DatabaseError(f"Failed to find faculty by email: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_by_name_and_university(name, university_id):
        """Finds faculty by exact name within a university."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM faculty WHERE university_id = %s AND name = %s"
            cursor.execute(query, (university_id, name))
            return cursor.fetchone()

        except Error as e:
            raise DatabaseError(f"Failed to find faculty by name: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_by_id(faculty_id):
        """Finds faculty by ID."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM faculty WHERE faculty_id = %s"
            cursor.execute(query, (faculty_id,))
            
            return cursor.fetchone()
            
        except Error as e:
            raise DatabaseError(f"Failed to find faculty by ID: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_all_by_university(university_id):
        """Returns all faculty members for a specific university."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM faculty WHERE university_id = %s"
            cursor.execute(query, (university_id,))
            
            return cursor.fetchall()
            
        except Error as e:
            raise DatabaseError(f"Failed to list university faculty: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def update_status(faculty_id, is_active):
        """Updates the active status of a faculty member."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = "UPDATE faculty SET is_active = %s WHERE faculty_id = %s"
            cursor.execute(query, (is_active, faculty_id))
            conn.commit()
            
            return cursor.rowcount > 0
            
        except Error as e:
            raise DatabaseError(f"Failed to update faculty status: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def update_faculty_profile(faculty_id, name, email, department, password_hash=None):
        """Updates faculty basic profile; updates password if password_hash is provided."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            if password_hash:
                query = "UPDATE faculty SET name=%s, email=%s, department=%s, password_hash=%s WHERE faculty_id=%s"
                cursor.execute(query, (name, email, department, password_hash, faculty_id))
            else:
                query = "UPDATE faculty SET name=%s, email=%s, department=%s WHERE faculty_id=%s"
                cursor.execute(query, (name, email, department, faculty_id))

            conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            raise DatabaseError(f"Failed to update faculty: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def update_password(faculty_id, password_hash):
        """Updates faculty password hash."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = "UPDATE faculty SET password_hash = %s WHERE faculty_id = %s"
            cursor.execute(query, (password_hash, faculty_id))
            conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            raise DatabaseError(f"Failed to update faculty password: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def count_by_university(university_id):
        """Counts active faculty for a university."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM faculty WHERE university_id = %s AND is_active = TRUE"
            cursor.execute(query, (university_id,))
            return cursor.fetchone()[0]
        except Error as e:
            raise DatabaseError(f"Failed to count faculty: {e}")
        finally:
            close_connection(conn)
