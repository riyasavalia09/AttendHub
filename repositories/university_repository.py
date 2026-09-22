from db_connection import get_connection, close_connection
from exceptions.custom_exceptions import DatabaseError
from mysql.connector import Error

class UniversityRepository:
    """
    Repository for accessing 'universities' table.
    
    Responsibilities:
    - CRUD operations for University entity
    """
    
    @staticmethod
    def create_university(university_name, domain, plan='FREE'):
        """
        Creates a new university record.
        Args:
            university_name (str): Name of the university
            domain (str): Domain for tenant identification
            plan (str): Subscription plan ('FREE', 'PREMIUM')
        Returns:
            int: The new university_id
        Raises:
            DatabaseError: If insert fails
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO universities (university_name, domain, plan, is_active)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (university_name, domain, plan, True))
            conn.commit()
            
            return cursor.lastrowid
            
        except Error as e:
            raise DatabaseError(f"Failed to create university: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_by_id(university_id):
        """
        Finds a university by ID.
        Args:
            university_id (int): Primary key
        Returns:
            dict: University record or None
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM universities WHERE university_id = %s"
            cursor.execute(query, (university_id,))
            
            return cursor.fetchone()
            
        except Error as e:
            raise DatabaseError(f"Failed to find university: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def update_plan(university_id, plan):
        """
        Updates the subscription plan.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = "UPDATE universities SET plan = %s WHERE university_id = %s"
            cursor.execute(query, (plan, university_id))
            conn.commit()
            
            return cursor.rowcount > 0
            
        except Error as e:
            raise DatabaseError(f"Failed to update plan: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def set_active_status(university_id, is_active):
        """
        Updates the active status (Boolean).
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = "UPDATE universities SET is_active = %s WHERE university_id = %s"
            cursor.execute(query, (is_active, university_id))
            conn.commit()
            
            return cursor.rowcount > 0
            
        except Error as e:
            raise DatabaseError(f"Failed to update status: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def update_profile(
        university_id,
        university_name=None,
        registered_address=None,
        official_contact_email=None,
        official_contact_phone=None,
        website_url=None,
    ):
        """Updates editable university profile fields.

        Returns:
            bool: True if update executed successfully (rowcount can be 0 if no changes).
        """
        fields = {
            'university_name': university_name,
            'registered_address': registered_address,
            'official_contact_email': official_contact_email,
            'official_contact_phone': official_contact_phone,
            'website_url': website_url,
        }
        set_clauses = []
        params = []
        for col, value in fields.items():
            if value is None:
                continue
            set_clauses.append(f"{col} = %s")
            params.append(value)

        if not set_clauses:
            return False

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = f"UPDATE universities SET {', '.join(set_clauses)} WHERE university_id = %s"
            params.append(university_id)
            cursor.execute(query, tuple(params))
            conn.commit()
            return True
        except Error as e:
            raise DatabaseError(f"Failed to update university profile: {e}")
        finally:
            close_connection(conn)
