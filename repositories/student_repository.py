from db_connection import get_connection, close_connection
from exceptions.custom_exceptions import DatabaseError
from mysql.connector import Error

class StudentRepository:
    """
    Repository for accessing 'students' table.
    """
    
    @staticmethod
    def create_student(university_id, enrollment_no, name, department, semester, email, password_hash):
        """Creates a new student."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO students (university_id, enrollment_no, name, department, semester, email, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (university_id, enrollment_no, name, department, semester, email, password_hash))
            conn.commit()
            
            return cursor.lastrowid
            
        except Error as e:
            raise DatabaseError(f"Failed to create student: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_by_enrollment(enrollment_no):
        """Finds student by enrollment number."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM students WHERE enrollment_no = %s"
            cursor.execute(query, (enrollment_no,))
            
            return cursor.fetchone()
            
        except Error as e:
            raise DatabaseError(f"Failed to find student by enrollment: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_by_id(student_id):
        """Finds student by ID."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM students WHERE student_id = %s"
            cursor.execute(query, (student_id,))
            
            return cursor.fetchone()
            
        except Error as e:
            raise DatabaseError(f"Failed to find student by ID: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_all_by_university(university_id):
        """Returns all students for a specific university."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM students WHERE university_id = %s"
            cursor.execute(query, (university_id,))
            
            return cursor.fetchall()
            
        except Error as e:
            raise DatabaseError(f"Failed to list university students: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_by_department_and_semester(department, semester, university_id=None):
        """Finds active students by department and semester.

        Args:
            department (str): Department name
            semester (int): Semester number
            university_id (int|None): Optional university scope to prevent cross-tenant leakage
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            base_query = "SELECT * FROM students WHERE department = %s AND semester = %s AND is_active = TRUE"
            params = [department, semester]

            if university_id is not None:
                base_query += " AND university_id = %s"
                params.append(university_id)

            cursor.execute(base_query, tuple(params))
            return cursor.fetchall()

        except Error as e:
            raise DatabaseError(f"Failed to find students by department/semester: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def count_by_university(university_id):
        """Counts active students for a university."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM students WHERE university_id = %s AND is_active = TRUE"
            cursor.execute(query, (university_id,))
            return cursor.fetchone()[0]
        except Error as e:
            raise DatabaseError(f"Failed to count students: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def update_status(student_id, is_active):
        """Updates active status for a student."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = "UPDATE students SET is_active = %s WHERE student_id = %s"
            cursor.execute(query, (is_active, student_id))
            conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            raise DatabaseError(f"Failed to update student status: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def update_student_profile(student_id, name, department, semester, email, password_hash=None):
        """Updates student basic profile; updates password if password_hash is provided."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            if password_hash:
                query = "UPDATE students SET name=%s, department=%s, semester=%s, email=%s, password_hash=%s WHERE student_id=%s"
                cursor.execute(query, (name, department, semester, email, password_hash, student_id))
            else:
                query = "UPDATE students SET name=%s, department=%s, semester=%s, email=%s WHERE student_id=%s"
                cursor.execute(query, (name, department, semester, email, student_id))

            conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            raise DatabaseError(f"Failed to update student: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def update_password(student_id, password_hash):
        """Updates student password hash."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE students SET password_hash = %s WHERE student_id = %s",
                (password_hash, student_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            raise DatabaseError(f"Failed to update student password: {e}")
        finally:
            close_connection(conn)
