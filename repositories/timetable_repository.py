from db_connection import get_connection, close_connection
from exceptions.custom_exceptions import DatabaseError
from mysql.connector import Error

class TimetableRepository:
    """
    Repository for accessing 'timetable' table.
    """
    
    @staticmethod
    def create_timetable_entry(university_id, faculty_id, department, semester, subject, day, start_time, end_time):
        """Creates a new timetable entry."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO timetable (university_id, faculty_id, department, semester, subject, day, start_time, end_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (university_id, faculty_id, department, semester, subject, day, start_time, end_time))
            conn.commit()
            
            return cursor.lastrowid
            
        except Error as e:
            raise DatabaseError(f"Failed to create timetable entry: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def count_by_university(university_id):
        """Counts timetable entries for a university."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM timetable WHERE university_id = %s"
            cursor.execute(query, (university_id,))
            return cursor.fetchone()[0]
        except Error as e:
            raise DatabaseError(f"Failed to count timetables: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_by_id(timetable_id):
        """Finds a timetable entry by ID."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM timetable WHERE timetable_id = %s"
            cursor.execute(query, (timetable_id,))
            return cursor.fetchone()

        except Error as e:
            raise DatabaseError(f"Failed to find timetable entry by ID: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_by_id(timetable_id):
        """Alias method to fetch a timetable entry by ID."""
        return TimetableRepository.find_by_id(timetable_id)

    @staticmethod
    def update_timetable(timetable_id, data):
        """Updates a timetable entry."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                UPDATE timetable
                SET
                    subject = %s,
                    faculty_id = %s,
                    day = %s,
                    start_time = %s,
                    end_time = %s,
                    department = %s,
                    semester = %s
                WHERE timetable_id = %s
            """
            cursor.execute(
                query,
                (
                    data.get('subject'),
                    data.get('faculty_id'),
                    data.get('day'),
                    data.get('start_time'),
                    data.get('end_time'),
                    data.get('department'),
                    data.get('semester'),
                    timetable_id,
                ),
            )
            conn.commit()
            return cursor.rowcount

        except Error as e:
            raise DatabaseError(f"Failed to update timetable entry: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def has_existing_lectures(timetable_id):
        """Returns True if any lecture exists for the timetable entry."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM lectures WHERE timetable_id = %s"
            cursor.execute(query, (timetable_id,))
            row = cursor.fetchone()
            return (row[0] if row else 0) > 0
        except Error as e:
            raise DatabaseError(f"Failed to check existing lectures: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def has_time_conflict(faculty_id, day, start_time, end_time, exclude_id=None):
        """Returns True if another timetable row overlaps for same faculty/day."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT 1
                FROM timetable
                WHERE faculty_id = %s
                  AND UPPER(day) = UPPER(%s)
                  AND (%s IS NULL OR timetable_id <> %s)
                  AND start_time < %s
                  AND end_time > %s
                LIMIT 1
            """
            cursor.execute(query, (faculty_id, day, exclude_id, exclude_id, end_time, start_time))
            return cursor.fetchone() is not None
        except Error as e:
            raise DatabaseError(f"Failed to check faculty time conflict: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def has_faculty_time_conflict(faculty_id, day, start_time, end_time, exclude_id=None):
        """Backward-compatible alias."""
        return TimetableRepository.has_time_conflict(
            faculty_id=faculty_id,
            day=day,
            start_time=start_time,
            end_time=end_time,
            exclude_id=exclude_id,
        )

    @staticmethod
    def find_by_faculty(faculty_id):
        """Finds timetable entries for a specific faculty member."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Ordering by day and time for better usability
            query = """
                SELECT * FROM timetable 
                WHERE faculty_id = %s 
                ORDER BY FIELD(day, 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'), start_time
            """
            cursor.execute(query, (faculty_id,))
            
            return cursor.fetchall()
            
        except Error as e:
            raise DatabaseError(f"Failed to find timetable for faculty: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_by_faculty_and_day(faculty_id, day):
        """Finds timetable entries for a faculty member for a specific day."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT * FROM timetable
                WHERE faculty_id = %s AND UPPER(day) = %s
                ORDER BY start_time
            """
            cursor.execute(query, (faculty_id, str(day).upper()))
            return cursor.fetchall()

        except Error as e:
            raise DatabaseError(f"Failed to find timetable for faculty/day: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_all_by_university(university_id):
        """Finds all timetable entries for a university joining with faculty name."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT t.*, f.name as faculty_name, f.department 
                FROM timetable t
                JOIN faculty f ON t.faculty_id = f.faculty_id
                WHERE t.university_id = %s 
                ORDER BY FIELD(day, 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'), t.start_time
            """
            cursor.execute(query, (university_id,))
            
            return cursor.fetchall()
            
        except Error as e:
            raise DatabaseError(f"Failed to list university timetable: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_for_student(university_id, department, semester):
        """Finds timetable filtered by department and semester for students."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT
                    t.timetable_id,
                    t.university_id,
                    t.faculty_id,
                    t.department,
                    t.semester,
                    t.subject,
                    t.day,
                    TIME_FORMAT(t.start_time, '%H:%i:%S') AS start_time,
                    TIME_FORMAT(t.end_time, '%H:%i:%S') AS end_time,
                    f.name as faculty_name
                FROM timetable t
                JOIN faculty f ON t.faculty_id = f.faculty_id
                WHERE t.university_id = %s AND t.department = %s AND t.semester = %s
                ORDER BY FIELD(day, 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'), t.start_time
            """
            cursor.execute(query, (university_id, department, semester))
            
            return cursor.fetchall()
            
        except Error as e:
            raise DatabaseError(f"Failed to fetch student timetable: {e}")
        finally:
            close_connection(conn)
