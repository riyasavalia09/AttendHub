from db_connection import get_connection, close_connection
from exceptions.custom_exceptions import DatabaseError, DuplicateRecordError
from mysql.connector import Error, IntegrityError
from mysql.connector.errorcode import ER_DUP_ENTRY

class AttendanceRepository:
    """
    Repository for accessing 'attendance' table.
    """
    
    @staticmethod
    def mark_attendance(lecture_id, student_id, status):
        """Marks attendance for a student in a lecture."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO attendance (lecture_id, student_id, status)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (lecture_id, student_id, status))
            conn.commit()
            
            return cursor.lastrowid
        except IntegrityError as e:
            if getattr(e, 'errno', None) == ER_DUP_ENTRY:
                raise DuplicateRecordError("Attendance already exists for this lecture and student") from e
            raise DatabaseError(f"Failed to mark attendance: {e}") from e
            
        except Error as e:
            raise DatabaseError(f"Failed to mark attendance: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def attendance_exists(lecture_id):
        """Returns True if any attendance row exists for this lecture."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM attendance WHERE lecture_id = %s LIMIT 1", (lecture_id,))
            return cursor.fetchone() is not None
        except Error as e:
            raise DatabaseError(f"Failed to check attendance existence: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def attendance_exists_for_lecture(lecture_id):
        """Backward-compatible alias for legacy callers."""
        return AttendanceRepository.attendance_exists(lecture_id)

    @staticmethod
    def get_count_summary(lecture_id):
        """
        Returns { total: int, present: int } for a lecture.
        Assumes attendance records exist for all students (Present/Absent).
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'PRESENT' THEN 1 ELSE 0 END) as present
                FROM attendance
                WHERE lecture_id = %s
            """
            cursor.execute(query, (lecture_id,))
            result = cursor.fetchone()
            
            # Handle standard None/Decimal returns
            return {
                'total': result['total'] if result else 0,
                'present': int(result['present']) if result and result['present'] else 0
            }
            
        except Error as e:
            raise DatabaseError(f"Failed to get attendance summary: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_by_lecture(lecture_id):
        """Finds all attendance records for a specific lecture."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT
                    a.attendance_id,
                    a.lecture_id,
                    a.student_id,
                    a.status,
                    a.marked_at,
                    s.enrollment_no,
                    s.name AS student_name,
                    s.department,
                    s.semester
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE a.lecture_id = %s
                ORDER BY s.enrollment_no ASC
            """
            cursor.execute(query, (lecture_id,))
            
            return cursor.fetchall()
            
        except Error as e:
            raise DatabaseError(f"Failed to list attendance: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def count_present_students(lecture_id):
        """Counts the number of students marked as PRESENT for a lecture."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) FROM attendance WHERE lecture_id = %s AND status = 'PRESENT'"
            cursor.execute(query, (lecture_id,))
            
            result = cursor.fetchone()
            return result[0] if result else 0
            
        except Error as e:
            raise DatabaseError(f"Failed to count present students: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def find_by_student(student_id):
        """Finds attendance history for a specific student."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT
                    a.status,
                    DATE_FORMAT(a.marked_at, '%Y-%m-%d %H:%i:%S') AS marked_at,
                    DATE_FORMAT(l.lecture_date, '%Y-%m-%d') AS lecture_date,
                    t.subject,
                    TIME_FORMAT(t.start_time, '%H:%i:%S') AS start_time,
                    TIME_FORMAT(t.end_time, '%H:%i:%S') AS end_time
                FROM attendance a
                JOIN lectures l ON a.lecture_id = l.lecture_id
                JOIN timetable t ON l.timetable_id = t.timetable_id
                WHERE a.student_id = %s
                ORDER BY l.lecture_date DESC, t.start_time DESC
            """
            cursor.execute(query, (student_id,))
            
            return cursor.fetchall()
            
        except Error as e:
            raise DatabaseError(f"Failed to fetch student attendance history: {e}")
        finally:
            close_connection(conn)

    # ==============================
    # Analytics (SQL Aggregations)
    # ==============================

    @staticmethod
    def get_subject_counts_for_student(student_id: int):
        """Returns per-subject attendance counts for a student.

        Output rows:
          { subject, present_count, absent_count, total_count }
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    t.subject AS subject,
                    COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present_count,
                    COALESCE(SUM(CASE WHEN a.status = 'ABSENT' THEN 1 ELSE 0 END), 0) AS absent_count,
                    COUNT(*) AS total_count
                FROM attendance a
                JOIN lectures l ON a.lecture_id = l.lecture_id
                JOIN timetable t ON l.timetable_id = t.timetable_id
                WHERE a.student_id = %s
                GROUP BY t.subject
                ORDER BY t.subject ASC
            """
            cursor.execute(query, (int(student_id),))
            return cursor.fetchall()

        except Error as e:
            raise DatabaseError(f"Failed to get student subject attendance counts: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_overall_counts_for_student(student_id: int):
        """Returns overall counts for a student's attendance."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present_count,
                    COUNT(*) AS total_count
                FROM attendance a
                WHERE a.student_id = %s
            """
            cursor.execute(query, (int(student_id),))
            return cursor.fetchone() or {'present_count': 0, 'total_count': 0}

        except Error as e:
            raise DatabaseError(f"Failed to get student overall attendance counts: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_subject_counts_for_student_in_university(university_id: int, student_id: int):
        """Same as get_subject_counts_for_student but scoped to a university."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    t.subject AS subject,
                    COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present_count,
                    COALESCE(SUM(CASE WHEN a.status = 'ABSENT' THEN 1 ELSE 0 END), 0) AS absent_count,
                    COUNT(*) AS total_count
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                JOIN lectures l ON a.lecture_id = l.lecture_id
                JOIN timetable t ON l.timetable_id = t.timetable_id
                WHERE s.university_id = %s AND s.student_id = %s
                GROUP BY t.subject
                ORDER BY t.subject ASC
            """
            cursor.execute(query, (int(university_id), int(student_id)))
            return cursor.fetchall()

        except Error as e:
            raise DatabaseError(f"Failed to get scoped student subject attendance counts: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_overall_counts_for_student_in_university(university_id: int, student_id: int):
        """Same as get_overall_counts_for_student but scoped to a university."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present_count,
                    COUNT(*) AS total_count
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE s.university_id = %s AND s.student_id = %s
            """
            cursor.execute(query, (int(university_id), int(student_id)))
            return cursor.fetchone() or {'present_count': 0, 'total_count': 0}

        except Error as e:
            raise DatabaseError(f"Failed to get scoped student overall attendance counts: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_subject_counts_for_student_in_university_filtered(
        university_id: int,
        student_id: int,
        subject: str = None,
        from_date: str = None,
        to_date: str = None,
    ):
        """Returns per-subject attendance counts for a student scoped to a university with optional filters.

        Filters:
        - subject: exact match on timetable.subject
        - from_date/to_date: inclusive date range on lectures.lecture_date (YYYY-MM-DD)
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            where = ["s.university_id = %s", "s.student_id = %s"]
            params = [int(university_id), int(student_id)]

            if subject:
                where.append("t.subject = %s")
                params.append(str(subject))
            if from_date:
                where.append("l.lecture_date >= %s")
                params.append(from_date)
            if to_date:
                where.append("l.lecture_date <= %s")
                params.append(to_date)

            query = f"""
                SELECT
                    t.subject AS subject,
                    COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present_count,
                    COALESCE(SUM(CASE WHEN a.status = 'ABSENT' THEN 1 ELSE 0 END), 0) AS absent_count,
                    COUNT(*) AS total_count
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                JOIN lectures l ON a.lecture_id = l.lecture_id
                JOIN timetable t ON l.timetable_id = t.timetable_id
                WHERE {' AND '.join(where)}
                GROUP BY t.subject
                ORDER BY t.subject ASC
            """
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

        except Error as e:
            raise DatabaseError(f"Failed to get filtered scoped student subject attendance counts: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_overall_counts_for_student_in_university_filtered(
        university_id: int,
        student_id: int,
        subject: str = None,
        from_date: str = None,
        to_date: str = None,
    ):
        """Returns overall attendance counts for a student scoped to a university with optional filters."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            where = ["s.university_id = %s", "s.student_id = %s"]
            params = [int(university_id), int(student_id)]

            if subject:
                where.append("t.subject = %s")
                params.append(str(subject))
            if from_date:
                where.append("l.lecture_date >= %s")
                params.append(from_date)
            if to_date:
                where.append("l.lecture_date <= %s")
                params.append(to_date)

            query = f"""
                SELECT
                    COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present_count,
                    COUNT(*) AS total_count
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                JOIN lectures l ON a.lecture_id = l.lecture_id
                JOIN timetable t ON l.timetable_id = t.timetable_id
                WHERE {' AND '.join(where)}
            """
            cursor.execute(query, tuple(params))
            return cursor.fetchone() or {'present_count': 0, 'total_count': 0}

        except Error as e:
            raise DatabaseError(f"Failed to get filtered scoped student overall attendance counts: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_lowest_attendance_students(university_id: int, limit: int = 5):
        """Returns lowest attendance students for a university.

        Output rows:
          { student_id, student_name, present_count, total_count }
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    s.student_id AS student_id,
                    s.name AS student_name,
                    COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present_count,
                    COUNT(a.attendance_id) AS total_count
                FROM students s
                JOIN attendance a ON a.student_id = s.student_id
                JOIN lectures l ON a.lecture_id = l.lecture_id
                JOIN timetable t ON l.timetable_id = t.timetable_id
                WHERE s.university_id = %s
                GROUP BY s.student_id, s.name
                HAVING COUNT(a.attendance_id) > 0
                ORDER BY (COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) / COUNT(a.attendance_id)) ASC
                LIMIT %s
            """
            cursor.execute(query, (int(university_id), int(limit)))
            return cursor.fetchall()

        except Error as e:
            raise DatabaseError(f"Failed to get lowest attendance students: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_lecture_attendance_distribution(faculty_id: int, lecture_id: int):
        """Returns attendance distribution for a lecture, scoped to the faculty."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    COUNT(a.attendance_id) AS total_students,
                    COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present,
                    COALESCE(SUM(CASE WHEN a.status = 'ABSENT' THEN 1 ELSE 0 END), 0) AS absent
                FROM attendance a
                JOIN lectures l ON a.lecture_id = l.lecture_id
                JOIN timetable t ON l.timetable_id = t.timetable_id
                WHERE a.lecture_id = %s AND t.faculty_id = %s
            """
            cursor.execute(query, (int(lecture_id), int(faculty_id)))
            return cursor.fetchone() or {'total_students': 0, 'present': 0, 'absent': 0}

        except Error as e:
            raise DatabaseError(f"Failed to get lecture attendance distribution: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_lecture_trend_by_subject(faculty_id: int, subject: str):
        """Returns per-lecture attendance totals for a faculty + subject.

        Output rows:
          { lecture_date, lecture_id, present_count, total_count }
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    DATE_FORMAT(l.lecture_date, '%Y-%m-%d') AS lecture_date,
                    l.lecture_id AS lecture_id,
                    COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present_count,
                    COUNT(a.attendance_id) AS total_count
                FROM lectures l
                JOIN timetable t ON l.timetable_id = t.timetable_id
                LEFT JOIN attendance a ON a.lecture_id = l.lecture_id
                WHERE t.faculty_id = %s AND t.subject = %s
                GROUP BY l.lecture_id, l.lecture_date
                ORDER BY l.lecture_date ASC, l.lecture_id ASC
            """
            cursor.execute(query, (int(faculty_id), str(subject)))
            return cursor.fetchall()

        except Error as e:
            raise DatabaseError(f"Failed to get lecture trend by subject: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_lecture_trend_by_subject_filtered(faculty_id: int, subject: str, from_date: str = None, to_date: str = None):
        """Returns per-lecture attendance totals for a faculty + subject with optional lecture_date range."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            where = ["t.faculty_id = %s", "t.subject = %s"]
            params = [int(faculty_id), str(subject)]

            if from_date:
                where.append("l.lecture_date >= %s")
                params.append(from_date)
            if to_date:
                where.append("l.lecture_date <= %s")
                params.append(to_date)

            query = f"""
                SELECT
                    DATE_FORMAT(l.lecture_date, '%Y-%m-%d') AS lecture_date,
                    l.lecture_id AS lecture_id,
                    COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present_count,
                    COUNT(a.attendance_id) AS total_count
                FROM lectures l
                JOIN timetable t ON l.timetable_id = t.timetable_id
                LEFT JOIN attendance a ON a.lecture_id = l.lecture_id
                WHERE {' AND '.join(where)}
                GROUP BY l.lecture_id, l.lecture_date
                ORDER BY l.lecture_date ASC, l.lecture_id ASC
            """
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

        except Error as e:
            raise DatabaseError(f"Failed to get filtered lecture trend by subject: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_subject_counts_for_student_filtered(student_id: int, subject: str = None, from_date: str = None, to_date: str = None):
        """Returns per-subject attendance counts for a student with optional filters.

        Filters:
        - subject: exact match on timetable.subject
        - from_date/to_date: inclusive date range on lectures.lecture_date (YYYY-MM-DD)

        Output rows:
          { subject, present_count, absent_count, total_count }
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            where = ["a.student_id = %s"]
            params = [int(student_id)]

            if subject:
                where.append("t.subject = %s")
                params.append(str(subject))
            if from_date:
                where.append("l.lecture_date >= %s")
                params.append(from_date)
            if to_date:
                where.append("l.lecture_date <= %s")
                params.append(to_date)

            query = f"""
                SELECT
                    t.subject AS subject,
                    COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present_count,
                    COALESCE(SUM(CASE WHEN a.status = 'ABSENT' THEN 1 ELSE 0 END), 0) AS absent_count,
                    COUNT(*) AS total_count
                FROM attendance a
                JOIN lectures l ON a.lecture_id = l.lecture_id
                JOIN timetable t ON l.timetable_id = t.timetable_id
                WHERE {' AND '.join(where)}
                GROUP BY t.subject
                ORDER BY t.subject ASC
            """
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

        except Error as e:
            raise DatabaseError(f"Failed to get filtered student subject attendance counts: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_overall_counts_for_student_filtered(student_id: int, subject: str = None, from_date: str = None, to_date: str = None):
        """Returns overall attendance counts for a student with optional filters."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            where = ["a.student_id = %s"]
            params = [int(student_id)]

            if subject:
                where.append("t.subject = %s")
                params.append(str(subject))
            if from_date:
                where.append("l.lecture_date >= %s")
                params.append(from_date)
            if to_date:
                where.append("l.lecture_date <= %s")
                params.append(to_date)

            query = f"""
                SELECT
                    COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present_count,
                    COUNT(*) AS total_count
                FROM attendance a
                JOIN lectures l ON a.lecture_id = l.lecture_id
                JOIN timetable t ON l.timetable_id = t.timetable_id
                WHERE {' AND '.join(where)}
            """
            cursor.execute(query, tuple(params))
            return cursor.fetchone() or {'present_count': 0, 'total_count': 0}

        except Error as e:
            raise DatabaseError(f"Failed to get filtered student overall attendance counts: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_lowest_attendance_students_filtered(
        university_id: int,
        limit: int = 5,
        from_date: str = None,
        to_date: str = None,
    ):
        """Returns lowest attendance students for a university with optional lecture_date range."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            where = ["s.university_id = %s"]
            params = [int(university_id)]

            if from_date:
                where.append("l.lecture_date >= %s")
                params.append(from_date)
            if to_date:
                where.append("l.lecture_date <= %s")
                params.append(to_date)

            query = f"""
                SELECT
                    s.student_id AS student_id,
                    s.name AS student_name,
                    COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present_count,
                    COUNT(a.attendance_id) AS total_count
                FROM students s
                JOIN attendance a ON a.student_id = s.student_id
                JOIN lectures l ON a.lecture_id = l.lecture_id
                WHERE {' AND '.join(where)}
                GROUP BY s.student_id, s.name
                HAVING COUNT(a.attendance_id) > 0
                ORDER BY (COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) / COUNT(a.attendance_id)) ASC
                LIMIT %s
            """
            params.append(int(limit))
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

        except Error as e:
            raise DatabaseError(f"Failed to get filtered lowest attendance students: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_department_attendance_counts_filtered(
        university_id: int,
        from_date: str = None,
        to_date: str = None,
    ):
        """Returns department-wise attendance totals for a university with optional lecture_date range.

        Output rows:
          { department, present_count, total_count }
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            where = ["s.university_id = %s"]
            params = [int(university_id)]

            if from_date:
                where.append("l.lecture_date >= %s")
                params.append(from_date)
            if to_date:
                where.append("l.lecture_date <= %s")
                params.append(to_date)

            query = f"""
                SELECT
                    COALESCE(NULLIF(TRIM(s.department), ''), 'Unknown') AS department,
                    COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present_count,
                    COUNT(a.attendance_id) AS total_count
                FROM students s
                JOIN attendance a ON a.student_id = s.student_id
                JOIN lectures l ON a.lecture_id = l.lecture_id
                WHERE {' AND '.join(where)}
                GROUP BY COALESCE(NULLIF(TRIM(s.department), ''), 'Unknown')
                HAVING COUNT(a.attendance_id) > 0
                ORDER BY department ASC
            """
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

        except Error as e:
            raise DatabaseError(f"Failed to get filtered department attendance counts: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_university_trend_by_date_filtered(
        university_id: int,
        from_date: str = None,
        to_date: str = None,
    ):
        """Returns university-wide attendance totals grouped by lecture_date.

        Output rows:
          { lecture_date, present_count, total_count }
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            where = ["s.university_id = %s"]
            params = [int(university_id)]

            if from_date:
                where.append("l.lecture_date >= %s")
                params.append(from_date)
            if to_date:
                where.append("l.lecture_date <= %s")
                params.append(to_date)

            query = f"""
                SELECT
                    DATE_FORMAT(l.lecture_date, '%Y-%m-%d') AS lecture_date,
                    COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present_count,
                    COUNT(a.attendance_id) AS total_count
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                JOIN lectures l ON a.lecture_id = l.lecture_id
                WHERE {' AND '.join(where)}
                GROUP BY l.lecture_date
                HAVING COUNT(a.attendance_id) > 0
                ORDER BY l.lecture_date ASC
            """
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

        except Error as e:
            raise DatabaseError(f"Failed to get filtered university trend: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_faculty_overall_trend_by_date_filtered(
        faculty_id: int,
        from_date: str = None,
        to_date: str = None,
    ):
        """Returns faculty-wide attendance totals grouped by lecture_date (all subjects)."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            where = ["t.faculty_id = %s"]
            params = [int(faculty_id)]

            if from_date:
                where.append("l.lecture_date >= %s")
                params.append(from_date)
            if to_date:
                where.append("l.lecture_date <= %s")
                params.append(to_date)

            query = f"""
                SELECT
                    DATE_FORMAT(l.lecture_date, '%Y-%m-%d') AS lecture_date,
                    COALESCE(SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END), 0) AS present_count,
                    COUNT(a.attendance_id) AS total_count
                FROM lectures l
                JOIN timetable t ON l.timetable_id = t.timetable_id
                LEFT JOIN attendance a ON a.lecture_id = l.lecture_id
                WHERE {' AND '.join(where)}
                GROUP BY l.lecture_date
                HAVING COUNT(a.attendance_id) > 0
                ORDER BY l.lecture_date ASC
            """
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

        except Error as e:
            raise DatabaseError(f"Failed to get filtered faculty overall trend: {e}")
        finally:
            close_connection(conn)

    @staticmethod
    def get_recent_lecture_attendance_for_student(
        student_id: int,
        limit: int = 5,
        subject: str = None,
        from_date: str = None,
        to_date: str = None,
    ):
        """Returns recent lecture attendance rows for a student (last N), optionally filtered.

        Output rows:
          { lecture_date, subject, status }
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            where = ["a.student_id = %s"]
            params = [int(student_id)]

            if subject:
                where.append("t.subject = %s")
                params.append(str(subject))
            if from_date:
                where.append("l.lecture_date >= %s")
                params.append(from_date)
            if to_date:
                where.append("l.lecture_date <= %s")
                params.append(to_date)

            query = f"""
                SELECT
                    DATE_FORMAT(l.lecture_date, '%Y-%m-%d') AS lecture_date,
                    t.subject AS subject,
                    a.status AS status
                FROM attendance a
                JOIN lectures l ON a.lecture_id = l.lecture_id
                JOIN timetable t ON l.timetable_id = t.timetable_id
                WHERE {' AND '.join(where)}
                ORDER BY l.lecture_date DESC, l.lecture_id DESC
                LIMIT %s
            """
            params.append(int(limit))
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

        except Error as e:
            raise DatabaseError(f"Failed to get recent student lecture attendance: {e}")
        finally:
            close_connection(conn)
