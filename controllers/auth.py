from flask import request, session

from controllers.base_controller import BaseController
from exceptions.custom_exceptions import AppError, ValidationError

class AuthController(BaseController):
    """
    Controller for Authentication endpoints.
    Delegates business logic to AuthService.
    """
    def __init__(self, auth_service):
        self.auth_service = auth_service

    def admin_signup(self):
        try:
            data = request.get_json(silent=True) or {}
            result = self.auth_service.admin_signup(data)
            message = result.get('message') if isinstance(result, dict) else 'Registration successful'
            return self.success_response(data=result, message=message or 'Registration successful', status_code=201)
        except Exception as e:
            return self.handle_exception(e)

    def admin_login(self):
        try:
            data = request.get_json(silent=True) or {}
            if not data.get('email') or not data.get('password'):
                raise ValidationError('Email and password are required')
            session_data = self.auth_service.admin_login(data.get('email'), data.get('password'))
            self._create_flask_session(session_data)
            return self.success_response(data={"session": session_data}, message='Login successful', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def faculty_login(self):
        try:
            data = request.get_json(silent=True) or {}
            if not data.get('email') or not data.get('password'):
                raise ValidationError('Email and password are required')
            session_data = self.auth_service.faculty_login(data.get('email'), data.get('password'))
            self._create_flask_session(session_data)
            return self.success_response(data={"session": session_data}, message='Login successful', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def student_login(self):
        try:
            data = request.get_json(silent=True) or {}
            if not data.get('enrollment_no') or not data.get('password'):
                raise ValidationError('Enrollment number and password are required')
            session_data = self.auth_service.student_login(data.get('enrollment_no'), data.get('password'))
            self._create_flask_session(session_data)
            return self.success_response(data={"session": session_data}, message='Login successful', status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def logout(self):
        try:
            payload = request.get_json(silent=True) or {}
            session_id = payload.get('session_id')
            if not session_id:
                # Fallback to session cookie
                session_id = session.get('session_id')
                
            if session_id:
                self.auth_service.logout(session_id)
                session.clear()
                return self.success_response(data=None, message='Logged out successfully', status_code=200)
            raise ValidationError('No active session')
        except Exception as e:
            return self.handle_exception(e)

    def change_password(self):
        try:
            if not session.get('user_id') or not session.get('role'):
                raise AppError('Not authenticated', 401)

            data = request.get_json(silent=True) or {}
            current_password = data.get('current_password')
            new_password = data.get('new_password')

            result = self.auth_service.change_password(
                role=session.get('role'),
                user_id=session.get('user_id'),
                current_password=current_password,
                new_password=new_password,
            )
            return self.success_response(data=result, message=result.get('message', 'Password updated'), status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def forgot_password(self):
        try:
            data = request.get_json(silent=True) or {}
            role = (data.get('role') or '').strip().lower()
            identifier = data.get('identifier')
            result = self.auth_service.request_password_reset(role=role, identifier=identifier)
            return self.success_response(data=result, message=result.get('message', 'OK'), status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def reset_password(self):
        try:
            data = request.get_json(silent=True) or {}
            token = data.get('token')
            new_password = data.get('new_password')
            result = self.auth_service.reset_password_with_token(token=token, new_password=new_password)
            return self.success_response(data=result, message=result.get('message', 'Password reset'), status_code=200)
        except Exception as e:
            return self.handle_exception(e)

    def _create_flask_session(self, session_data):
        """Helper to set Flask session cookies"""
        session['user_id'] = session_data['user_id']
        session['role'] = session_data['role']
        session['session_id'] = session_data['session_id']
        if 'university_id' in session_data:
            session['university_id'] = session_data['university_id']

