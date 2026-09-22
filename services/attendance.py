from exceptions.custom_exceptions import (
    LectureNotActiveError, 
    AttendanceAlreadyMarkedError, 
    ValidationError,
    RecordNotFoundError
)

class AttendanceService:
    """
    Service to handle attendance marking logic.
    """

    def __init__(self, attendance_repo, student_repo, lecture_repo, queue, attendance_set):
        """
        Constructor with Dependency Injection.
        """
        self.attendance_repo = attendance_repo
        self.student_repo = student_repo
        self.lecture_repo = lecture_repo
        self.request_queue = queue      # Queue for submission requests
        self.attendance_set = attendance_set # Set for in-memory duplicate check (lecture_id, student_id)

    def mark_attendance(self, lecture_id, attendance_list):
        """
        Marks attendance for a list of students for a specific lecture.
        Input: List of { 'student_id': int, 'status': 'PRESENT'|'ABSENT' }
        """
        try:
            lecture_id = int(lecture_id)
        except (TypeError, ValueError):
            raise ValidationError("lecture_id must be a valid integer")

        if not isinstance(attendance_list, list):
            raise ValidationError("Attendance list must be a list")

        # 1. Enqueue request
        self.request_queue.enqueue({
            'lecture_id': lecture_id,
            'students': attendance_list
        })

        # 2. Process request
        req = self.request_queue.dequeue()
        req_lecture_id = req['lecture_id']

        # 3. Validate lecture state before insert
        lecture = self.lecture_repo.find_by_id(req_lecture_id)
        if not lecture:
            raise RecordNotFoundError("Lecture not found")

        lecture_status = (lecture.get('status') or '').upper()
        if lecture_status != 'ONGOING':
            raise LectureNotActiveError()

        if self.attendance_repo.attendance_exists(req_lecture_id):
            raise AttendanceAlreadyMarkedError()

        marked_count = 0
        seen = set()

        # 4. Insert attendance rows. If any insert fails, status update is never executed.
        for item in req['students']:
            if not isinstance(item, dict):
                raise ValidationError("Each attendance row must be an object")

            student_id = item.get('student_id')
            if student_id is None:
                raise ValidationError("student_id is required")

            try:
                student_id = int(student_id)
            except (TypeError, ValueError):
                raise ValidationError("student_id must be a valid integer")

            status = str(item.get('status', 'PRESENT')).upper()
            if status not in ('PRESENT', 'ABSENT'):
                raise ValidationError("status must be PRESENT or ABSENT")

            key = (req_lecture_id, student_id)
            if key in seen:
                continue
            seen.add(key)

            self.attendance_repo.mark_attendance(req_lecture_id, student_id, status)
            marked_count += 1

        # 5. Update lecture state only after successful inserts
        updated = self.lecture_repo.update_status(req_lecture_id, "MARKED")
        if not updated:
            raise ValidationError("Failed to update lecture status")

        from repositories.timetable_repository import TimetableRepository
        timetable = TimetableRepository.find_by_id(lecture.get('timetable_id')) if lecture.get('timetable_id') else None
        subject = timetable.get('subject') if timetable else None

        return {
            "lecture_id": req_lecture_id,
            "subject": subject,
            "status": "MARKED",
            "attendance_marked": True,
            "count": marked_count,
        }

    def get_today_classes_with_status(self, faculty_id):
        """Returns only today's timetable classes with attendance-driven state."""
        from datetime import datetime, timedelta, time
        from repositories.timetable_repository import TimetableRepository

        def to_time_str(value):
            if value is None:
                return None
            if isinstance(value, timedelta):
                total_seconds = int(value.total_seconds())
                hours = (total_seconds // 3600) % 24
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            if isinstance(value, time):
                return value.strftime('%H:%M:%S')
            return value

        try:
            faculty_id = int(faculty_id)
        except (TypeError, ValueError):
            raise ValidationError("faculty_id must be a valid integer")

        today_day_full = datetime.now().strftime("%A").upper()
        day_map = {
            'MONDAY': 'MON',
            'TUESDAY': 'TUE',
            'WEDNESDAY': 'WED',
            'THURSDAY': 'THU',
            'FRIDAY': 'FRI',
            'SATURDAY': 'SAT',
            'SUNDAY': 'SUN',
        }
        today_day = day_map.get(today_day_full, today_day_full[:3])
        today_date = datetime.now().date()

        today_slots = TimetableRepository.find_by_faculty_and_day(faculty_id, today_day) or []

        result = []
        for slot in today_slots:
            timetable_id = slot.get('timetable_id')
            lecture = self.lecture_repo.find_by_timetable_and_date(timetable_id, today_date) if timetable_id else None
            lecture_id = lecture.get('lecture_id') if lecture else None

            if lecture_id:
                attendance_marked = bool(self.attendance_repo.attendance_exists(lecture_id))
                status = 'MARKED' if attendance_marked else 'ONGOING'
            else:
                attendance_marked = False
                status = 'NOT_STARTED'

            result.append({
                'timetable_id': timetable_id,
                'subject': slot.get('subject'),
                'start_time': to_time_str(slot.get('start_time')),
                'end_time': to_time_str(slot.get('end_time')),
                'lecture_id': lecture_id,
                'status': status,
                'lecture_status': status,
                'attendance_marked': attendance_marked,
            })

        result.sort(key=lambda x: x.get('start_time') or '')
        return result

    def get_today_lectures_with_status(self, faculty_id):
        """Backward-compatible wrapper for existing controller calls."""
        return self.get_today_classes_with_status(faculty_id)

    def get_attendance_by_lecture(self, lecture_id):
        """Retrieves attendance list for a lecture."""
        try:
            lecture_id = int(lecture_id)
        except (TypeError, ValueError):
            raise ValidationError("lecture_id must be a valid integer")

        lecture = self.lecture_repo.find_by_id(lecture_id)
        if not lecture:
            raise RecordNotFoundError("Lecture not found")

        if (lecture.get('status') or '').upper() != 'MARKED':
            raise ValidationError("Attendance preview is available only for MARKED lectures")

        return self.attendance_repo.find_by_lecture(lecture_id)

    def get_students_for_lecture(self, lecture_id):
        """Returns class-wise students for a given lecture.

        Business rule:
        - Fetch lecture by lecture_id
        - Get timetable_id
        - Fetch timetable details
        - Filter students by timetable.department and timetable.semester
        """
        lecture = self.lecture_repo.find_by_id(lecture_id)
        if not lecture:
            raise RecordNotFoundError("Lecture not found")

        timetable_id = lecture.get('timetable_id')
        if not timetable_id:
            raise ValidationError('Lecture has no timetable_id')

        # TimetableRepository isn't injected into this service currently;
        # import the repository here to keep SQL out of the service.
        from repositories.timetable_repository import TimetableRepository

        timetable = TimetableRepository.find_by_id(timetable_id)
        if not timetable:
            raise RecordNotFoundError('Timetable entry not found')

        department = timetable.get('department')
        semester = timetable.get('semester')
        university_id = timetable.get('university_id')

        if not department or semester is None:
            raise ValidationError('Timetable missing department/semester')

        return self.student_repo.find_by_department_and_semester(
            department=department,
            semester=semester,
            university_id=university_id,
        )

    def get_faculty_attendance_history(self, faculty_id, subject=None, from_date=None, to_date=None):
        """Aggregates lecture history + attendance stats for faculty.

        Optional filters:
        - subject: exact subject match
        - from_date/to_date: YYYY-MM-DD (inclusive)
        """
        lectures = self.lecture_repo.get_faculty_history(
            faculty_id=faculty_id,
            subject=subject,
            from_date=from_date,
            to_date=to_date,
        )
        
        # Enrich with attendance counts
        # (N+1 query problem acceptable for small scale/pagination, optimized in SQL usually)
        result = []
        for l in lectures:
             stats = self.attendance_repo.get_count_summary(l['lecture_id'])
             l['stats'] = stats
             result.append(l)
             
        return result

    def get_student_history(self, student_id):
        """Retrieves attendance history for a student."""
        return self.attendance_repo.find_by_student(student_id)

    def get_student_dashboard_stats(self, student_id):
        """
        Calculates dashboard summary stats: Overall %, Subject count, Alerts.
        """
        history = self.attendance_repo.find_by_student(student_id)
        
        if not history:
             return {
                 'overall_attendance': 0,
                 'subjects_count': 0,
                 'alerts': []
             }
             
        total_lectures = len(history)
        present_count = sum(1 for r in history if r['status'] == 'PRESENT')
        overall_pct = round((present_count / total_lectures * 100), 1) if total_lectures > 0 else 0
        
        # Breakdown by subject
        subjects = {}
        for r in history:
            sub = r['subject']
            if sub not in subjects:
                subjects[sub] = {'total': 0, 'present': 0}
            subjects[sub]['total'] += 1
            if r['status'] == 'PRESENT':
                subjects[sub]['present'] += 1
                
        subjects_count = len(subjects)
        
        # Generate Alerts (e.g. < 75%)
        alerts = []
        for sub, stats in subjects.items():
            pct = (stats['present'] / stats['total']) * 100
            if pct < 75:
                alerts.append({
                    'type': 'warning',
                    'message': f"Low attendance in {sub} ({round(pct)}%)"
                })
                
        return {
            'overall_attendance': overall_pct,
            'subjects_count': subjects_count,
            'alerts': alerts
        }

    def get_student_attendance_summary(self, student_id):
        """Retrieves summary stats for student."""
        history = self.attendance_repo.find_by_student(student_id)
        total = len(history)
        present = sum(1 for record in history if record['status'] == 'PRESENT')
        percentage = (present / total * 100) if total > 0 else 0.0
        return {
            'total_lectures': total,
            'present_count': present,
            'attendance_percentage': round(percentage, 2),
            'history': history # Include full history if needed, or separate
        }

    def get_student_detailed_report(self, student_id):
        """
        Generates detailed subject-wise attendance report for the attendance page.
        """
        history = self.attendance_repo.find_by_student(student_id)
        
        # Overall Stats
        total_lectures = len(history)
        present_count = sum(1 for r in history if r['status'] == 'PRESENT')
        absent_count = total_lectures - present_count
        overall_pct = round((present_count / total_lectures * 100), 1) if total_lectures > 0 else 0
        
        # Subject-wise Stats
        subject_stats = {}
        for r in history:
            sub = r['subject']
            # Assuming subject is just the name for now
            if sub not in subject_stats:
                subject_stats[sub] = {'total': 0, 'present': 0}
            
            subject_stats[sub]['total'] += 1
            if r['status'] == 'PRESENT':
                subject_stats[sub]['present'] += 1
        
        # Format for UI
        subjects_list = []
        for sub, stats in subject_stats.items():
            total = stats['total']
            present = stats['present']
            absent = total - present
            pct = round((present / total * 100), 1) if total > 0 else 0
            
            status_label = "Good"
            if pct < 50:
                status_label = "Critical"
            elif pct < 75:
                status_label = "Warning"
            elif pct < 85:
                 status_label = "Satisfactory"

            subjects_list.append({
                'name': sub,
                'code': '', # Placeholder
                'total': total,
                'present': present,
                'absent': absent,
                'percentage': pct,
                'status': status_label
            })
            
        return {
            'summary': {
                'overallPercentage': overall_pct,
                'totalLectures': total_lectures,
                'totalPresent': present_count,
                'totalAbsent': absent_count
            },
            'subjects': subjects_list
        }
