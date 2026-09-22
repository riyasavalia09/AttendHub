from flask import request, session

from controllers.base_controller import BaseController
from exceptions.custom_exceptions import AuthenticationError, ValidationError
from repositories.admin_repository import AdminRepository
from repositories.university_repository import UniversityRepository

class AdminController(BaseController):
    """
    Controller for Admin-only endpoints.
    Delegates to Admin, Faculty, and Student services.
    """
    def __init__(self, admin_service, faculty_service, student_service, timetable_service=None, analytics_service=None):
        self.admin_service = admin_service
        self.faculty_service = faculty_service
        self.student_service = student_service
        self.timetable_service = timetable_service
        self.analytics_service = analytics_service

    def get_dashboard_summary(self):
        try:
            university_id = session.get('university_id') # Ensure session['university_id'] is set on login!
            if not university_id:
                raise AuthenticationError('Unauthorized')

            stats = self.admin_service.get_dashboard_stats(university_id)
            return self.success_response(data=stats, message='Dashboard summary', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_university_profile(self):
        try:
            university_id = session.get('university_id')
            user_id = session.get('user_id')
            role = session.get('role')
            if not university_id or not user_id or role != 'admin':
                raise AuthenticationError('Unauthorized')

            university = UniversityRepository.find_by_id(university_id)
            if not university:
                return self.success_response(data={'university': None, 'admin': None}, message='University not found', status_code=200)

            admin = AdminRepository.find_by_id(user_id)

            def _to_iso(value):
                try:
                    return value.isoformat() if value else None
                except Exception:
                    return str(value) if value is not None else None

            university_id_value = university.get('university_id')
            university_payload = {
                'university_id': university_id_value,
                'university_id_display': f"UNI-{int(university_id_value):04d}" if university_id_value is not None else None,
                'university_name': university.get('university_name'),
                'domain': university.get('domain'),
                'registered_address': university.get('registered_address'),
                'official_contact_email': university.get('official_contact_email'),
                'official_contact_phone': university.get('official_contact_phone'),
                'website_url': university.get('website_url'),
                'plan': university.get('plan'),
                'is_active': bool(university.get('is_active')),
                'created_at': _to_iso(university.get('created_at')),
                'updated_at': _to_iso(university.get('updated_at')),
            }

            admin_payload = None
            if admin:
                admin_payload = {
                    'admin_id': admin.get('admin_id'),
                    'name': admin.get('name'),
                    'email': admin.get('email'),
                    'is_verified': bool(admin.get('is_verified')),
                    'created_at': _to_iso(admin.get('created_at')),
                }

            return self.success_response(data={'university': university_payload, 'admin': admin_payload}, message='University profile', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def update_university_profile(self):
        try:
            university_id = session.get('university_id')
            user_id = session.get('user_id')
            role = session.get('role')
            if not university_id or not user_id or role != 'admin':
                raise AuthenticationError('Unauthorized')

            data = request.get_json(silent=True) or {}
            university_name = data.get('university_name')
            registered_address = data.get('registered_address')
            official_contact_email = data.get('official_contact_email')
            official_contact_phone = data.get('official_contact_phone')
            website_url = data.get('website_url')

            def _norm(value):
                if value is None:
                    return None
                return str(value).strip()

            updated = UniversityRepository.update_profile(
                university_id,
                university_name=_norm(university_name),
                registered_address=_norm(registered_address),
                official_contact_email=_norm(official_contact_email),
                official_contact_phone=_norm(official_contact_phone),
                website_url=_norm(website_url),
            )

            university = UniversityRepository.find_by_id(university_id)

            def _to_iso(value):
                try:
                    return value.isoformat() if value else None
                except Exception:
                    return str(value) if value is not None else None

            university_id_value = university.get('university_id') if university else None
            university_payload = None
            if university:
                university_payload = {
                    'university_id': university_id_value,
                    'university_id_display': f"UNI-{int(university_id_value):04d}" if university_id_value is not None else None,
                    'university_name': university.get('university_name'),
                    'domain': university.get('domain'),
                    'registered_address': university.get('registered_address'),
                    'official_contact_email': university.get('official_contact_email'),
                    'official_contact_phone': university.get('official_contact_phone'),
                    'website_url': university.get('website_url'),
                    'plan': university.get('plan'),
                    'is_active': bool(university.get('is_active')),
                    'created_at': _to_iso(university.get('created_at')),
                    'updated_at': _to_iso(university.get('updated_at')),
                }
            return self.success_response(
                data={'updated': bool(updated), 'university': university_payload},
                message='University profile updated',
                status_code=200,
            )
        except Exception as e:
            return self.handle_exception(e)

    def create_faculty(self):
        try:
            # Authorization check implicitly or explicitly
            # if session.get('role') != 'admin': raise AuthorizationError()
            
            data = request.get_json(silent=True) or {}
            university_id = session.get('university_id')
            if not university_id:
                raise AuthenticationError('Unauthorized')

            faculty_id = self.faculty_service.create_faculty(
                university_id,
                data.get('name'),
                data.get('email'),
                data.get('department'),
                data.get('password')
            )
            return self.success_response(data={'faculty_id': faculty_id}, message='Faculty created', status_code=201)
        except Exception as e:
            return self.handle_exception(e)

    def update_faculty(self):
        try:
            data = request.get_json(silent=True) or {}
            university_id = session.get('university_id')
            if not university_id:
                raise AuthenticationError('Unauthorized')

            faculty_id = data.get('faculty_id')
            if not faculty_id:
                raise ValidationError('faculty_id is required')

            updated = self.faculty_service.update_faculty(
                university_id,
                int(faculty_id),
                data.get('name'),
                data.get('email'),
                data.get('department'),
                data.get('password')
            )

            if not updated:
                return self.success_response(data={'updated': False}, message='No changes applied', status_code=200)
            return self.success_response(data={'updated': True}, message='Faculty updated', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def set_faculty_status(self):
        try:
            data = request.get_json(silent=True) or {}
            university_id = session.get('university_id')
            if not university_id:
                raise AuthenticationError('Unauthorized')

            faculty_id = data.get('faculty_id')
            if not faculty_id:
                raise ValidationError('faculty_id is required')

            if 'is_active' not in data:
                raise ValidationError('is_active is required')

            is_active = bool(data.get('is_active'))
            changed = self.faculty_service.set_status(university_id, int(faculty_id), is_active)
            return self.success_response(data={'updated': changed, 'is_active': is_active}, message='Faculty status updated', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def create_student(self):
        try:
            data = request.get_json(silent=True) or {}
            university_id = session.get('university_id')
            if not university_id:
                raise AuthenticationError('Unauthorized')

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

    def update_student(self):
        try:
            data = request.get_json(silent=True) or {}
            university_id = session.get('university_id')
            if not university_id:
                raise AuthenticationError('Unauthorized')

            student_id = data.get('student_id')
            if not student_id:
                raise ValidationError('student_id is required')

            updated = self.student_service.update_student(
                university_id,
                int(student_id),
                data.get('name'),
                data.get('department'),
                data.get('semester'),
                data.get('email'),
                data.get('password')
            )
            if not updated:
                return self.success_response(data={'updated': False}, message='No changes applied', status_code=200)
            return self.success_response(data={'updated': True}, message='Student updated', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def set_student_status(self):
        try:
            data = request.get_json(silent=True) or {}
            university_id = session.get('university_id')
            if not university_id:
                raise AuthenticationError('Unauthorized')

            student_id = data.get('student_id')
            if not student_id:
                raise ValidationError('student_id is required')
            if 'is_active' not in data:
                raise ValidationError('is_active is required')

            is_active = bool(data.get('is_active'))
            changed = self.student_service.set_status(university_id, int(student_id), is_active)
            return self.success_response(data={'updated': changed, 'is_active': is_active}, message='Student status updated', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def list_faculty(self):
        try:
            university_id = session.get('university_id')
            if not university_id:
                raise AuthenticationError('Unauthorized')
            faculty_list = self.faculty_service.get_all_by_university(university_id)
            return self.success_response(data=faculty_list, message='Faculty list', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def list_students(self):
        try:
            university_id = session.get('university_id')
            if not university_id:
                raise AuthenticationError('Unauthorized')
            student_list = self.student_service.get_all_by_university(university_id)
            return self.success_response(data=student_list, message='Student list', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def upload_timetable(self):
        try:
            university_id = session.get('university_id')
            if not university_id:
                raise AuthenticationError('Unauthorized')
            
            if 'file' not in request.files:
                raise ValidationError('No file part')
                
            file = request.files['file']
            if file.filename == '':
                raise ValidationError('No selected file')
            
            if file:
                # Process CSV
                import csv
                import io
                
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                csv_input = csv.reader(stream)
                
                # Skip header if present (Assuming users provide header)
                # But safer to just try parsing row by row. 
                # Let's assume standard format: Department, Semester, Day, Time(Start), Time(End), Subject, Faculty Email/Name
                # Let's refine format based on UI hint: "Department, Semester, Day, Time, Subject, Faculty Name"
                # Actually, parsing time might be tricky if "Time" is one column "09:00 - 10:00".
                # Let's simplify and Delegate file object to Service or do basic parsing here.
                # Service is better for business logic (finding faculty ID by name, etc).
                
                # I'll pass the stream or list of rows to service.
                rows = list(csv_input)
                result = self.admin_service.process_timetable_upload(university_id, rows)
                if result.get('success_count', 0) == 0:
                    # Treat as error so UI doesn't show a false success message.
                    return self.error_response(message=result.get('message', 'No entries were imported'), status_code=400, data=result)

                return self.success_response(data=result, message=result.get('message', 'Timetable processed'), status_code=201)
        except Exception as e:
            return self.handle_exception(e)

    def list_timetable(self):
        try:
            university_id = session.get('university_id')
            if not university_id:
                raise AuthenticationError('Unauthorized')
            timetable = self.admin_service.get_timetable(university_id)
            return self.success_response(data=timetable, message='Timetable list', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_timetable_item(self, timetable_id):
        try:
            university_id = session.get('university_id')
            if not university_id:
                raise AuthenticationError('Unauthorized')
            if not self.timetable_service:
                raise ValidationError('Timetable service unavailable')

            row = self.timetable_service.get_timetable_by_id(timetable_id)
            return self.success_response(data=row, message='Timetable detail', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def update_timetable(self, timetable_id):
        try:
            university_id = session.get('university_id')
            if not university_id:
                raise AuthenticationError('Unauthorized')
            if not self.timetable_service:
                raise ValidationError('Timetable service unavailable')

            data = request.get_json(silent=True) or {}
            self.timetable_service.edit_timetable(timetable_id, data)
            return self.success_response(
                data={"message": "Timetable updated successfully"},
                message='Timetable updated successfully',
                status_code=200
            )
        except Exception as e:
            return self.handle_exception(e)

    def list_reports(self):
        try:
            university_id = session.get('university_id')
            if not university_id:
                raise AuthenticationError('Unauthorized')
            
            reports = self.admin_service.get_reports(university_id)
            return self.success_response(data=reports, message='Reports list', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    # ==============================
    # Analytics Endpoints
    # ==============================

    def get_student_attendance_summary(self):
        """Student-wise attendance analysis for Admin."""
        try:
            university_id = session.get('university_id')
            role = session.get('role')
            if not university_id or role != 'admin':
                raise AuthenticationError('Unauthorized')

            if not self.analytics_service:
                raise ValidationError('Analytics service unavailable')

            student_id = request.args.get('student_id')
            if not student_id:
                raise ValidationError('student_id is required')

            def _clean(value):
                if value is None:
                    return None
                value = str(value).strip()
                return value or None

            subject = _clean(request.args.get('subject'))
            from_date = _clean(request.args.get('from_date'))
            to_date = _clean(request.args.get('to_date'))

            data = self.analytics_service.admin_student_attendance_summary(
                university_id=int(university_id),
                student_id=int(student_id),
                subject=subject,
                from_date=from_date,
                to_date=to_date,
            )
            return self.success_response(data=data, message='Student attendance summary', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_lowest_attendance_students(self):
        """Lowest attendance students (Top 5) for Admin."""
        try:
            university_id = session.get('university_id')
            role = session.get('role')
            if not university_id or role != 'admin':
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
            limit = _clean(request.args.get('limit'))

            data = self.analytics_service.admin_lowest_attendance_students_filtered(
                university_id=int(university_id),
                limit=int(limit or 5),
                from_date=from_date,
                to_date=to_date,
            )
            return self.success_response(data=data, message='Lowest attendance students', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_department_averages(self):
        """Department-wise average attendance % for Admin."""
        try:
            university_id = session.get('university_id')
            role = session.get('role')
            if not university_id or role != 'admin':
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

            data = self.analytics_service.admin_department_averages(
                university_id=int(university_id),
                from_date=from_date,
                to_date=to_date,
            )
            return self.success_response(data=data, message='Department averages', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def get_university_trend(self):
        """University attendance trend by date (Admin)."""
        try:
            university_id = session.get('university_id')
            role = session.get('role')
            if not university_id or role != 'admin':
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

            data = self.analytics_service.admin_university_trend(
                university_id=int(university_id),
                from_date=from_date,
                to_date=to_date,
            )
            return self.success_response(data=data, message='University trend', status_code=200)
        except Exception as e:
            return self.handle_exception(e)
