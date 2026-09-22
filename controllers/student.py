from flask import request, session

from controllers.base_controller import BaseController
from exceptions.custom_exceptions import AuthenticationError, RecordNotFoundError, ValidationError

class StudentController(BaseController):
    """
    Controller for Student operations.
    Exposes read-only attendance endpoints.
    """
    def __init__(self, attendance_service, student_service, analytics_service=None):
        self.attendance_service = attendance_service
        self.student_service = student_service
        self.analytics_service = analytics_service

    def get_profile(self):
        try:
            student_id = session.get('user_id')
            if not student_id:
                raise AuthenticationError('Unauthorized')
            
            profile = self.student_service.get_profile(student_id)
            if not profile:
                raise RecordNotFoundError('Student not found')
            return self.success_response(data=profile, message='Profile', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_timetable(self):
        try:
            student_id = session.get('user_id')
            if not student_id:
                raise AuthenticationError('Unauthorized')
                
            timetable = self.student_service.get_timetable(student_id)
            return self.success_response(data=timetable, message='Timetable', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_attendance_history(self):
        try:
            student_id = session.get('user_id')
            # Fallback for testing
            if not student_id:
                student_id = request.args.get('student_id')
            
            if not student_id:
                raise AuthenticationError('Unauthorized')

            history = self.attendance_service.get_student_history(student_id)
            return self.success_response(data=history, message='Attendance history', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_attendance_summary(self):
        try:
            student_id = session.get('user_id')
            if not student_id:
                student_id = request.args.get('student_id')
            
            if not student_id:
                raise AuthenticationError('Unauthorized')

            summary = self.attendance_service.get_student_attendance_summary(student_id)
            return self.success_response(data=summary, message='Attendance summary', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_dashboard_summary(self):
        try:
            student_id = session.get('user_id')
            # Fallback for testing allow query param if strictly needed, mostly session
            if not student_id:
                student_id = request.args.get('student_id')
                
            if not student_id:
                raise AuthenticationError('Unauthorized')

            stats = self.student_service.get_dashboard_stats(student_id)
            return self.success_response(data=stats, message='Dashboard summary', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_attendance_report(self):
        try:
            student_id = session.get('user_id')
            if not student_id:
                student_id = request.args.get('student_id')
            
            if not student_id:
                raise AuthenticationError('Unauthorized')

            report = self.attendance_service.get_student_detailed_report(student_id)
            return self.success_response(data=report, message='Attendance report', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    # ==============================
    # Analytics Endpoints
    # ==============================

    def get_attendance_chart(self):
        """Personal attendance dashboard chart data for the logged-in student."""
        try:
            student_id = session.get('user_id')
            role = session.get('role')
            if not student_id or role != 'student':
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

            data = self.analytics_service.student_attendance_chart(
                int(student_id),
                subject=subject,
                from_date=from_date,
                to_date=to_date,
            )
            return self.success_response(data=data, message='Attendance chart', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_recent_trend(self):
        """Recent attendance trend for the logged-in student (last N lectures)."""
        try:
            student_id = session.get('user_id')
            role = session.get('role')
            if not student_id or role != 'student':
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
            limit = _clean(request.args.get('limit'))

            data = self.analytics_service.student_recent_trend(
                student_id=int(student_id),
                limit=int(limit or 5),
                subject=subject,
                from_date=from_date,
                to_date=to_date,
            )
            return self.success_response(data=data, message='Recent trend', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

