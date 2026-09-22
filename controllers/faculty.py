from flask import request, session, make_response

import csv
import io
from datetime import datetime

from controllers.base_controller import BaseController
from exceptions.custom_exceptions import AuthenticationError, ValidationError

class FacultyController(BaseController):
    """
    Controller for Faculty operations.
    Delegates to LectureService and AttendanceService.
    """
    def __init__(
        self,
        lecture_service,
        attendance_service,
        faculty_service=None,
        student_service=None,
        analytics_service=None
    ):
        self.lecture_service = lecture_service
        self.attendance_service = attendance_service
        self.faculty_service = faculty_service
        self.student_service = student_service
        self.analytics_service = analytics_service

    def get_context(self):
        try:
            faculty_id = session.get('user_id')
            role = session.get('role')
            if not faculty_id or role != 'faculty':
                raise AuthenticationError('Unauthorized')

            if not self.faculty_service:
                raise ValidationError('Faculty service unavailable')

            ctx = self.faculty_service.get_context(int(faculty_id))
            return self.success_response(data=ctx, message='Faculty context', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_profile(self):
        try:
            faculty_id = session.get('user_id')
            role = session.get('role')
            if not faculty_id or role != 'faculty':
                raise AuthenticationError('Unauthorized')

            if not self.faculty_service:
                raise ValidationError('Faculty service unavailable')

            profile = self.faculty_service.get_profile(int(faculty_id))
            return self.success_response(data=profile, message='Faculty profile', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def start_lecture(self):
        try:
            data = request.get_json(silent=True) or {}
            faculty_id = session.get('user_id')
            
            if not faculty_id:
                raise AuthenticationError('Unauthorized')

            if not data.get('timetable_id'):
                raise ValidationError('timetable_id is required')

            lecture_id = self.lecture_service.start_lecture(
                faculty_id, 
                data.get('timetable_id')
            )
            return self.success_response(data={'lecture_id': lecture_id}, message='Lecture started', status_code=201)
        except Exception as e:
            return self.handle_exception(e)

    def end_lecture(self):
        try:
            data = request.get_json(silent=True) or {}
            lecture_id = data.get('lecture_id')
            if not lecture_id:
                raise ValidationError('lecture_id is required')
            self.lecture_service.end_lecture(lecture_id)
            return self.success_response(data=None, message='Lecture ended successfully', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def mark_attendance(self):
        try:
            data = request.get_json(silent=True) or {}
            lecture_id = data.get('lecture_id')
            students = data.get('students') # List of student IDs

            if not lecture_id:
                raise ValidationError('lecture_id is required')
            
            result = self.attendance_service.mark_attendance(lecture_id, students)
            return self.success_response(data=result, message='Attendance marked', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_attendance_history(self):
        try:
            lecture_id = request.args.get('lecture_id')
            if lecture_id:
                # Detail view
                history = self.attendance_service.get_attendance_by_lecture(lecture_id)
                return self.success_response(data=history, message='Attendance history', status_code=200)
            else:
                # List/Summary view logic
                faculty_id = session.get('user_id')
                # Fallback for testing
                if not faculty_id:
                    raise AuthenticationError('Unauthorized')

                subject = request.args.get('subject')
                from_date = request.args.get('from_date')
                to_date = request.args.get('to_date')

                history = self.attendance_service.get_faculty_attendance_history(
                    faculty_id=faculty_id,
                    subject=subject,
                    from_date=from_date,
                    to_date=to_date,
                )
                return self.success_response(data=history, message='Attendance history', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def export_attendance_history(self):
        """Export faculty lecture attendance history (summary list) as CSV."""
        try:
            faculty_id = session.get('user_id')
            role = session.get('role')
            if not faculty_id or role != 'faculty':
                raise AuthenticationError('Unauthorized')

            subject = request.args.get('subject')
            from_date = request.args.get('from_date')
            to_date = request.args.get('to_date')

            rows = self.attendance_service.get_faculty_attendance_history(
                faculty_id=faculty_id,
                subject=subject,
                from_date=from_date,
                to_date=to_date,
            )
            rows = rows if isinstance(rows, list) else []

            output = io.StringIO(newline='')
            writer = csv.writer(output)
            writer.writerow([
                'lecture_id',
                'lecture_date',
                'subject',
                'start_time',
                'end_time',
                'status',
                'present',
                'total',
            ])

            for r in rows:
                if not isinstance(r, dict):
                    continue
                stats = r.get('stats') if isinstance(r.get('stats'), dict) else {}
                writer.writerow([
                    r.get('lecture_id') or '',
                    r.get('lecture_date') or '',
                    r.get('subject') or '',
                    r.get('start_time') or '',
                    r.get('end_time') or '',
                    r.get('status') or '',
                    stats.get('present', ''),
                    stats.get('total', ''),
                ])

            csv_data = output.getvalue()
            resp = make_response(csv_data)
            resp.headers['Content-Type'] = 'text/csv; charset=utf-8'
            filename = f"attendance_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            resp.headers['Content-Disposition'] = f'attachment; filename={filename}'
            return resp
        except Exception as e:
            return self.handle_exception(e)

    def get_attendance_today(self):
        try:
            faculty_id = session.get('user_id')
            if not faculty_id:
                raise AuthenticationError('Unauthorized')

            data = self.attendance_service.get_today_lectures_with_status(faculty_id)
            return self.success_response(data=data, message="Today's lectures", status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_students_for_lecture(self):
        try:
            lecture_id = request.args.get('lecture_id')
            if not lecture_id:
                raise ValidationError('lecture_id is required')

            students = self.attendance_service.get_students_for_lecture(int(lecture_id))
            return self.success_response(data=students, message='Students for lecture', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_schedule(self):
        try:
            faculty_id = session.get('user_id')
            if not faculty_id:
                raise AuthenticationError('Unauthorized')
            
            schedule = self.lecture_service.get_todays_lectures(faculty_id)
            return self.success_response(data=schedule, message='Schedule', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_weekly_schedule(self):
        try:
            faculty_id = session.get('user_id')
            if not faculty_id:
                raise AuthenticationError('Unauthorized')

            schedule = self.lecture_service.get_weekly_schedule(int(faculty_id))
            return self.success_response(data=schedule, message='Weekly schedule', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def list_students(self):
        try:
            faculty_id = session.get('user_id')
            university_id = session.get('university_id')
            # Assuming faculty can see all students in their university
            # Or we could filter by department etc. for now simple list.
            
            # Using StudentRepository directly or via a specific service method?
            # FacultyController injects 'attendance_service' and 'lecture_service'.
            # Neither has 'get_all_students'.
            # Ideally should go through StudentService or just use repo if simple read.
            # But FacultyController doesn't have StudentService injected in app.py!
            # It has 'attendance_service' which has 'student_repo'.
            
            if not faculty_id or not university_id:
                raise AuthenticationError('Unauthorized')

            students = self.attendance_service.student_repo.find_all_by_university(university_id)
            return self.success_response(data=students, message='Students list', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def create_student(self):
        try:
            faculty_id = session.get('user_id')
            role = session.get('role')
            university_id = session.get('university_id')
            if not faculty_id or role != 'faculty' or not university_id:
                raise AuthenticationError('Unauthorized')

            if not self.student_service:
                raise ValidationError('Student service unavailable')

            data = request.get_json(silent=True) or {}
            student_id = self.student_service.create_student(
                university_id,
                data.get('enrollment_no'),
                data.get('name'),
                data.get('department'),
                data.get('semester', 1),
                data.get('email'),
                data.get('password')
            )
            return self.success_response(data={'student_id': student_id}, message='Student created', status_code=201)
        except Exception as e:
            return self.handle_exception(e)

    def get_dashboard_summary(self):
        try:
            faculty_id = session.get('user_id')
            university_id = session.get('university_id')
            role = session.get('role')

            if not faculty_id or not university_id or role != 'faculty':
                raise AuthenticationError('Unauthorized')

            all_slots = self.lecture_service.timetable_repo.find_by_faculty(int(faculty_id)) or []
            assigned_subjects = sorted({(s.get('subject') or '').strip() for s in all_slots if isinstance(s, dict) and s.get('subject')})

            total_students = self.attendance_service.student_repo.count_by_university(int(university_id))

            today_slots = self.lecture_service.get_todays_lectures(int(faculty_id)) or []
            lectures_today = len(today_slots)

            today_lecture_status = self.attendance_service.get_today_lectures_with_status(int(faculty_id)) or []
            attendance_pending = sum(1 for l in today_lecture_status if isinstance(l, dict) and not l.get('attendance_marked'))

            recent_activity = []
            for l in today_lecture_status:
                if not isinstance(l, dict):
                    continue
                recent_activity.append({
                    'activity': 'Lecture',
                    'subject': l.get('subject'),
                    'start_time': l.get('start_time'),
                    'end_time': l.get('end_time'),
                    'lecture_status': l.get('lecture_status'),
                    'attendance_marked': bool(l.get('attendance_marked')),
                })

            return self.success_response(
                data={
                    'assigned_subjects_count': len(assigned_subjects),
                    'total_students': int(total_students or 0),
                    'lectures_today': int(lectures_today or 0),
                    'attendance_pending': int(attendance_pending or 0),
                    'recent_activity': recent_activity,
                },
                message='Dashboard summary',
                status_code=200,
            )
        except Exception as e:
            return self.handle_exception(e)

    # ==============================
    # Analytics Endpoints
    # ==============================

    def get_lecture_stats(self):
        """Lecture attendance distribution (present/absent/percentage) for faculty."""
        try:
            faculty_id = session.get('user_id')
            role = session.get('role')
            if not faculty_id or role != 'faculty':
                raise AuthenticationError('Unauthorized')

            if not self.analytics_service:
                raise ValidationError('Analytics service unavailable')

            lecture_id = request.args.get('lecture_id')
            if not lecture_id:
                raise ValidationError('lecture_id is required')

            data = self.analytics_service.faculty_lecture_stats(
                faculty_id=int(faculty_id),
                lecture_id=int(lecture_id),
            )
            return self.success_response(data=data, message='Lecture stats', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_lecture_trend(self):
        """Attendance percentage trend over lectures for a given subject (scoped to faculty)."""
        try:
            faculty_id = session.get('user_id')
            role = session.get('role')
            if not faculty_id or role != 'faculty':
                raise AuthenticationError('Unauthorized')

            if not self.analytics_service:
                raise ValidationError('Analytics service unavailable')

            def _clean(value):
                if value is None:
                    return None
                value = str(value).strip()
                return value or None

            subject = _clean(request.args.get('subject'))
            from_date = _clean(request.args.get('from_date'))
            to_date = _clean(request.args.get('to_date'))
            data = self.analytics_service.faculty_lecture_trend(
                faculty_id=int(faculty_id),
                subject=subject,
                from_date=from_date,
                to_date=to_date,
            )
            return self.success_response(data=data, message='Lecture trend', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_overall_trend(self):
        """Attendance percentage trend over dates across all subjects (scoped to faculty)."""
        try:
            faculty_id = session.get('user_id')
            role = session.get('role')
            if not faculty_id or role != 'faculty':
                raise AuthenticationError('Unauthorized')

            if not self.analytics_service:
                raise ValidationError('Analytics service unavailable')

            def _clean(value):
                if value is None:
                    return None
                value = str(value).strip()
                return value or None

            from_date = _clean(request.args.get('from_date'))
            to_date = _clean(request.args.get('to_date'))

            data = self.analytics_service.faculty_overall_trend(
                faculty_id=int(faculty_id),
                from_date=from_date,
                to_date=to_date,
            )
            return self.success_response(data=data, message='Overall trend', status_code=200)
        except Exception as e:
            return self.handle_exception(e)
