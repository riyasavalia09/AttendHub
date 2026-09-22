from exceptions.custom_exceptions import DuplicateRecordError
from exceptions.custom_exceptions import ValidationError, RecordNotFoundError
import hashlib

class StudentService:
    """
    Service to handle Student domain logic.
    """

    def __init__(self, student_repo, timetable_repo=None, attendance_repo=None):
        """
        Constructor with Dependency Injection.
        """
        self.student_repo = student_repo
        self.timetable_repo = timetable_repo
        self.attendance_repo = attendance_repo

    def get_dashboard_stats(self, student_id):
        """Returns dynamic dashboard statistics for the student."""
        from datetime import datetime

        # 1. Fetch Student Details
        student = self.student_repo.find_by_id(student_id)
        if not student:
            return None

        # 2. Fetch Timetable for Subjects Count + Today's Classes
        timetable = self.timetable_repo.find_for_student(
            student['university_id'],
            student['department'],
            student['semester'],
        )
        total_subjects = len({t.get('subject') for t in timetable if isinstance(t, dict) and t.get('subject')}) if timetable else 0

        weekday_to_code = {
            0: 'MON',
            1: 'TUE',
            2: 'WED',
            3: 'THU',
            4: 'FRI',
            5: 'SAT',
            6: 'SUN',
        }
        today_code = weekday_to_code.get(datetime.now().weekday())
        classes_today = 0
        if today_code and timetable:
            classes_today = sum(1 for t in timetable if isinstance(t, dict) and t.get('day') == today_code)

        # 3. Fetch Attendance History for Stats + Alerts
        if self.attendance_repo:
            history = self.attendance_repo.find_by_student(student_id)
            total_lectures = len(history)
            present_count = sum(1 for record in history if record['status'] == 'PRESENT')
            
            overall_attendance = (present_count / total_lectures * 100) if total_lectures > 0 else 0
            recent_activity = history[:5] # Last 5 records

            # Alerts: subjects below 75%
            subject_stats = {}
            for record in history:
                sub = record.get('subject')
                if not sub:
                    continue
                if sub not in subject_stats:
                    subject_stats[sub] = {'total': 0, 'present': 0}
                subject_stats[sub]['total'] += 1
                if record.get('status') == 'PRESENT':
                    subject_stats[sub]['present'] += 1

            alerts = []
            for sub, stats in subject_stats.items():
                total = stats.get('total') or 0
                present = stats.get('present') or 0
                pct = (present / total * 100) if total > 0 else 0
                if pct < 75:
                    alerts.append({
                        'type': 'warning',
                        'message': f"Low attendance in {sub} ({round(pct)}%)",
                    })
        else:
            overall_attendance = 0
            recent_activity = []
            alerts = []

        return {
            'overall_attendance': round(overall_attendance, 1),
            'total_subjects': total_subjects,
            'recent_activity': recent_activity,
            'classes_today': int(classes_today or 0),
            'attendance_alerts_count': len(alerts),
            'attendance_alerts': alerts,
            'student': {
                'student_id': student.get('student_id'),
                'name': student.get('name'),
                'enrollment_no': student.get('enrollment_no'),
                'department': student.get('department'),
                'semester': student.get('semester'),
                'email': student.get('email'),
                'is_active': bool(student.get('is_active')),
            }
        }

    def get_profile(self, student_id):
        """Fetches student profile details."""
        student = self.student_repo.find_by_id(student_id)
        if not student:
            return None

        return {
            'student_id': student.get('student_id'),
            'university_id': student.get('university_id'),
            'enrollment_no': student.get('enrollment_no'),
            'name': student.get('name'),
            'department': student.get('department'),
            'semester': student.get('semester'),
            'email': student.get('email'),
            'is_active': bool(student.get('is_active')),
        }

    def get_timetable(self, student_id):
        """Fetches timetable for a student based on their department and semester."""
        student = self.student_repo.find_by_id(student_id)
        if not student:
            return []
            
        return self.timetable_repo.find_for_student(
            student['university_id'], 
            student['department'], 
            student['semester']
        )

    def create_student(self, university_id, enrollment_no, name, department, semester, email, password):
        """Creates a new student."""
        # 1. Check for duplicates (Enrollment)
        if self.student_repo.find_by_enrollment(enrollment_no):
            raise DuplicateRecordError("Student with this enrollment number already exists")
            
        # 2. Check Email (Skipping as find_by_email isn't robustly implemented in repo yet)
        # if self.student_repo.find_by_email(email): ...

        # 3. Hash Password
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # 4. Create
        return self.student_repo.create_student(university_id, enrollment_no, name, department, semester, email, password_hash)

    def get_all_by_university(self, university_id):
        """Returns all students for a university."""
        return self.student_repo.find_all_by_university(university_id)

    def set_status(self, university_id, student_id, is_active: bool):
        student = self.student_repo.find_by_id(student_id)
        if not student or student.get('university_id') != university_id:
            raise RecordNotFoundError('Student not found')
        return self.student_repo.update_status(student_id, is_active)

    def update_student(self, university_id, student_id, name, department, semester, email, password=None):
        student = self.student_repo.find_by_id(student_id)
        if not student or student.get('university_id') != university_id:
            raise RecordNotFoundError('Student not found')

        if not name or not department or semester is None:
            raise ValidationError('name, department, and semester are required')

        try:
            semester_int = int(semester)
        except Exception:
            raise ValidationError('semester must be a number')

        password_hash = None
        if password:
            if len(password) < 6:
                raise ValidationError('Password must be at least 6 characters')
            password_hash = hashlib.sha256(password.encode()).hexdigest()

        return self.student_repo.update_student_profile(student_id, name, department, semester_int, email, password_hash)
