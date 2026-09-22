from db_connection import get_connection, close_connection
from exceptions.custom_exceptions import DatabaseError, DuplicateRecordError
from mysql.connector import Error, IntegrityError

class AdminRepository:
    """
    Repository for accessing 'admins' table.
    """
    
    @staticmethod
    def create_admin(university_id, name, email, password_hash):
        """
        Creates a new admin record.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # is_verified defaults to False for security
            query = """
                INSERT INTO admins (university_id, name, email, password_hash, is_verified)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (university_id, name, email, password_hash, False))
            conn.commit()
            
            return cursor.lastrowid

        except IntegrityError:
            # Duplicate key (e.g., unique email) or other integrity constraints
            raise DuplicateRecordError("Admin email already exists")
        except Error as e:
            raise DatabaseError(f"Failed to create admin: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_by_email(email):
        """
        Finds admin by email.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM admins WHERE email = %s"
            cursor.execute(query, (email,))
            
            return cursor.fetchone()
            
        except Error as e:
            raise DatabaseError(f"Failed to find admin by email: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_by_id(admin_id):
        """
        Finds admin by ID.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM admins WHERE admin_id = %s"
            cursor.execute(query, (admin_id,))
            
            return cursor.fetchone()
            
        except Error as e:
            raise DatabaseError(f"Failed to find admin by ID: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def update_password(admin_id, password_hash):
        """Updates admin password hash."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = "UPDATE admins SET password_hash = %s WHERE admin_id = %s"
            cursor.execute(query, (password_hash, admin_id))
            conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            raise DatabaseError(f"Failed to update admin password: {e}")
        finally:
            close_connection(conn)
