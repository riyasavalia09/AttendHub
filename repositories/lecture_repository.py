from db_connection import get_connection, close_connection
from exceptions.custom_exceptions import DatabaseError
from mysql.connector import Error

class LectureRepository:
    """
    Repository for accessing 'lectures' table.
    """
    
    @staticmethod
    def create_lecture(timetable_id, lecture_date):
        """Creates a new lecture session."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO lectures (timetable_id, lecture_date, status)
                VALUES (%s, %s, 'ONGOING')
            """
            cursor.execute(query, (timetable_id, lecture_date))
            conn.commit()
            
            return cursor.lastrowid
            
        except Error as e:
            raise DatabaseError(f"Failed to create lecture: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def count_today_by_university(university_id):
        """Counts lectures scheduled/ongoing for today."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """
                SELECT COUNT(*) 
                FROM lectures l
                JOIN timetable t ON l.timetable_id = t.timetable_id
                WHERE t.university_id = %s AND l.lecture_date = CURDATE()
            """
            cursor.execute(query, (university_id,))
            return cursor.fetchone()[0]
        except Error as e:
            raise DatabaseError(f"Failed to count today's lectures: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_active_lecture(timetable_id, lecture_date):
        """Finds an active lecture for a specific timetable slot and date."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT * FROM lectures 
                WHERE timetable_id = %s AND lecture_date = %s AND status = 'ONGOING'
            """
            cursor.execute(query, (timetable_id, lecture_date))
            
            return cursor.fetchone()
            
        except Error as e:
            raise DatabaseError(f"Failed to find active lecture: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_by_timetable_and_date(timetable_id, today_date):
        """Finds a lecture for a specific timetable slot and date."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT * FROM lectures
                WHERE timetable_id = %s AND lecture_date = %s
                LIMIT 1
            """
            cursor.execute(query, (timetable_id, today_date))
            return cursor.fetchone()

        except Error as e:
            raise DatabaseError(f"Failed to find lecture by timetable/date: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_by_id(lecture_id):
        """Finds lecture by ID."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM lectures WHERE lecture_id = %s"
            cursor.execute(query, (lecture_id,))
            
            return cursor.fetchone()
            
        except Error as e:
            raise DatabaseError(f"Failed to find lecture by ID: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def end_lecture(lecture_id):
        """Ends a lecture session."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = """
                UPDATE lectures 
                SET status = 'ENDED', ended_at = CURRENT_TIMESTAMP 
                WHERE lecture_id = %s
            """
            cursor.execute(query, (lecture_id,))
            conn.commit()
            
            return cursor.rowcount > 0
            
        except Error as e:
            raise DatabaseError(f"Failed to end lecture: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def update_status(lecture_id, status):
        """Updates lecture status for a specific lecture."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                UPDATE lectures
                SET status = %s
                WHERE lecture_id = %s
            """
            cursor.execute(query, (status, lecture_id))
            conn.commit()
            return cursor.rowcount > 0

        except Error as e:
            raise DatabaseError(f"Failed to update lecture status: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_faculty_history(faculty_id, subject=None, from_date=None, to_date=None):
        """Retrieves lecture history for a faculty member.

        Optional filters:
        - subject: exact match on timetable.subject
        - from_date/to_date: YYYY-MM-DD (inclusive) applied to lectures.lecture_date
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            where = ["t.faculty_id = %s"]
            params = [faculty_id]

            if subject:
                where.append("t.subject = %s")
                params.append(subject)

            # Validate ISO date strings if provided
            if from_date:
                from datetime import date as _date
                _date.fromisoformat(from_date)
                where.append("l.lecture_date >= %s")
                params.append(from_date)

            if to_date:
                from datetime import date as _date
                _date.fromisoformat(to_date)
                where.append("l.lecture_date <= %s")
                params.append(to_date)

            query = f"""
                SELECT
                    l.lecture_id,
                    DATE_FORMAT(l.lecture_date, '%Y-%m-%d') AS lecture_date,
                    l.status,
                    t.subject,
                    TIME_FORMAT(t.start_time, '%H:%i:%S') AS start_time,
                    TIME_FORMAT(t.end_time, '%H:%i:%S') AS end_time,
                    t.timetable_id
                FROM lectures l
                JOIN timetable t ON l.timetable_id = t.timetable_id
                WHERE {' AND '.join(where)}
                ORDER BY l.lecture_date DESC, t.start_time DESC
            """
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
            
        except Error as e:
            raise DatabaseError(f"Failed to get faculty history: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_today_lectures_by_faculty(faculty_id):
        """Returns today's lectures for a faculty member.

        Includes timetable details needed for UI (subject/time/department/semester).
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    l.lecture_id,
                    l.timetable_id,
                    l.lecture_date,
                    l.status,
                    t.subject,
                    t.start_time,
                    t.end_time,
                    t.department,
                    t.semester
                FROM lectures l
                JOIN timetable t ON l.timetable_id = t.timetable_id
                WHERE t.faculty_id = %s AND l.lecture_date = CURDATE()
                ORDER BY t.start_time ASC
            """
            cursor.execute(query, (faculty_id,))
            return cursor.fetchall()

        except Error as e:
            raise DatabaseError(f"Failed to find today's lectures for faculty: {e}")
        finally:
            close_connection(conn)
