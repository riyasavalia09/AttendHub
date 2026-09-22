import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from exceptions.custom_exceptions import (
    AuthenticationError, 
    InvalidCredentialsError, 
    ValidationError, 
    DuplicateEntryError,
    DuplicateRecordError
)

class AuthService:
    """
    Service to handle Authentication and Authorization logic.
    Follows OOPS principles and uses Custom Data Structures.
    """

    def __init__(self, admin_repo, faculty_repo, student_repo, university_repo,
                 password_reset_repo,
                 queue, stack, linked_list):
        """
        Constructor with Dependency Injection.
        """
        # Repositories
        self.admin_repo = admin_repo
        self.faculty_repo = faculty_repo
        self.student_repo = student_repo
        self.university_repo = university_repo
        self.password_reset_repo = password_reset_repo
        
        # Data Structures
        self.login_queue = queue           # Queue: Validates strict processing order
        self.audit_stack = stack           # Stack: Audit logs (Last-In-First-Check)
        self.active_sessions = linked_list # LinkedList: Active sessions list
        
        # Internal State (No Global State)
        self._active_session_ids = set()   # Set: O(1) duplicate check
        
        # Immutable Role-Permission Mapping (Tuple)
        self._role_permissions = (
            ('admin', ('manage_faculty', 'manage_students', 'view_reports', 'manage_timetable')),
            ('faculty', ('mark_attendance', 'view_schedule', 'view_profile', 'create_student')),
            ('student', ('view_attendance', 'view_timetable'))
        )

    # --- Helper Methods ---

    def _hash_password(self, password):
        """Hashes password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _validate_new_password(self, new_password: str):
        if not isinstance(new_password, str) or not new_password.strip():
            raise ValidationError('New password is required')
        if len(new_password) < 6:
            raise ValidationError('Password must be at least 6 characters')

    def _validate_input(self, data, required_fields):
        """Validates dictionary input."""
        if not isinstance(data, dict):
            raise ValidationError("Invalid data format")
        
        missing = [f for f in required_fields if f not in data or not data[f]]
        if missing:
            raise ValidationError(f"Missing required fields: {', '.join(missing)}")

    def _create_session(self, user_id, role, name, email):
        """Creates session, adds to LinkedList and Set."""
        session_id = str(uuid.uuid4())
        
        # Prevent duplicate sessions for same user (Optional Rule, currently by session_id)
        # Using Set for O(1) duplicate check of session_id
        if session_id in self._active_session_ids:
             # Highly unlikely with UUID, but strictly following rule
             raise DuplicateEntryError("Session collision")

        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'role': role,
            'name': name,
            'email': email,
            'login_time': datetime.now()
        }
        
        self.active_sessions.add(session_data)
        self._active_session_ids.add(session_id)
        
        # Audit Log (Stack)
        self.audit_stack.push({
            'event': 'LOGIN_SUCCESS',
            'user': email,
            'role': role,
            'time': datetime.now()
        })
        
        return session_data

    # --- Public Methods ---

    def admin_signup(self, data: dict):
        """
        Registers a new University and its Admin.
        """
        self._validate_input(data, {'university_name', 'location', 'admin_name', 'email', 'password'})

        email = (data.get('email') or '').strip().lower()
        if not email:
            raise ValidationError('Email is required')

        # Prevent duplicates before creating a university record
        existing_admin = self.admin_repo.find_by_email(email)
        if existing_admin:
            raise DuplicateRecordError('Admin email already exists')
        
        # 1. Create University
        univ_id = self.university_repo.create_university(
            data['university_name'], 
            data['location']
        )
        
        # 2. Hash Password
        hashed_pw = self._hash_password(data['password'])
        
        # 3. Create Admin
        admin_id = self.admin_repo.create_admin(
            univ_id, 
            data['admin_name'], 
            email, 
            hashed_pw
        )
        
        return {'university_id': univ_id, 'admin_id': admin_id, 'message': 'Registration successful'}

    def admin_login(self, email: str, password: str):
        """Handles Admin login."""
        # 1. Enqueue Request
        self.login_queue.enqueue({'role': 'admin', 'email': email, 'ts': datetime.now()})
        
        # 2. Process Request
        req = self.login_queue.dequeue() # Simulate processing
        
        # 3. Authentication
        admin = self.admin_repo.find_by_email(req['email'])
        
        if admin and admin['password_hash'] == self._hash_password(password):
            session_data = self._create_session(admin['admin_id'], 'admin', admin['name'], admin['email'])
            session_data['university_id'] = admin['university_id'] # Add university_id to session
            return session_data
        
        # Failure Audit
        self.audit_stack.push({'event': 'LOGIN_FAIL', 'user': email, 'role': 'admin'})
        raise InvalidCredentialsError()

    def faculty_login(self, email: str, password: str):
        """Handles Faculty login."""
        self.login_queue.enqueue({'role': 'faculty', 'email': email, 'ts': datetime.now()})
        req = self.login_queue.dequeue()
        
        faculty = self.faculty_repo.find_by_email(req['email'])
        
        if faculty and faculty['is_active'] and faculty['password_hash'] == self._hash_password(password):
            session_data = self._create_session(faculty['faculty_id'], 'faculty', faculty['name'], faculty['email'])
            session_data['university_id'] = faculty.get('university_id')
            return session_data
            
        self.audit_stack.push({'event': 'LOGIN_FAIL', 'user': email, 'role': 'faculty'})
        raise InvalidCredentialsError()

    def student_login(self, enrollment_no: str, password: str):
        """Handles Student login."""
        self.login_queue.enqueue({'role': 'student', 'id': enrollment_no, 'ts': datetime.now()})
        req = self.login_queue.dequeue()
        
        student = self.student_repo.find_by_enrollment(req['id'])
        
        if not student:
            self.audit_stack.push({'event': 'LOGIN_FAIL', 'user': enrollment_no, 'role': 'student'})
            raise InvalidCredentialsError("Invalid enrollment number or password")

        # Verify password using hash
        if student['password_hash'] != self._hash_password(password):
             self.audit_stack.push({'event': 'LOGIN_FAIL', 'user': enrollment_no, 'role': 'student'})
             raise InvalidCredentialsError("Invalid enrollment number or password")

        session_data = self._create_session(student['student_id'], 'student', student['name'], student['email'])
        session_data['university_id'] = student.get('university_id')
        return session_data

    def logout(self, session_id: str):
        """Logs out a user by invalidating session."""
        # Note: In a real LinkedList, removing by property requires traversal
        # Our custom LinkedList.remove(data) removes by exact object match usually.
        # Here we iterate to find the matching dict.
        
        # Custom find logic for our Linked List structure
        current = self.active_sessions._head
        found = None
        
        while current:
            if current.data.get('session_id') == session_id:
                found = current.data
                break
            current = current.next
            
        if found:
            self.active_sessions.remove(found)
            if session_id in self._active_session_ids:
                self._active_session_ids.remove(session_id)
            return True
            
        return False

    # --- Password Management ---

    def change_password(self, role: str, user_id: int, current_password: str, new_password: str):
        """Change password for a logged-in user."""
        if role not in ('admin', 'faculty', 'student'):
            raise ValidationError('Invalid role')
        if not current_password:
            raise ValidationError('Current password is required')
        self._validate_new_password(new_password)
        if current_password == new_password:
            raise ValidationError('New password must be different')

        user = None
        if role == 'admin':
            user = self.admin_repo.find_by_id(user_id)
        elif role == 'faculty':
            user = self.faculty_repo.find_by_id(user_id)
        else:
            user = self.student_repo.find_by_id(user_id)

        if not user:
            raise AuthenticationError('User not found')

        if user.get('password_hash') != self._hash_password(current_password):
            raise InvalidCredentialsError('Current password is incorrect')

        new_hash = self._hash_password(new_password)
        if role == 'admin':
            ok = self.admin_repo.update_password(user_id, new_hash)
        elif role == 'faculty':
            ok = self.faculty_repo.update_password(user_id, new_hash)
        else:
            ok = self.student_repo.update_password(user_id, new_hash)

        if not ok:
            raise AuthenticationError('Failed to update password')

        self.audit_stack.push({'event': 'PASSWORD_CHANGED', 'role': role, 'user_id': user_id, 'time': datetime.now()})
        return {'message': 'Password updated successfully'}

    def request_password_reset(self, role: str, identifier: str):
        """Creates a password reset token. (Email/SMS delivery not implemented; token returned for dev/testing.)"""
        if role not in ('admin', 'faculty', 'student'):
            raise ValidationError('Invalid role')
        if not identifier or not str(identifier).strip():
            raise ValidationError('Identifier is required')

        identifier = str(identifier).strip()

        user = None
        if role == 'admin':
            user = self.admin_repo.find_by_email(identifier)
        elif role == 'faculty':
            user = self.faculty_repo.find_by_email(identifier)
        else:
            user = self.student_repo.find_by_enrollment(identifier)

        # Do not leak whether the user exists
        generic_message = 'If the account exists, a reset token has been generated.'
        if not user:
            self.audit_stack.push({'event': 'PASSWORD_RESET_REQUESTED_UNKNOWN', 'role': role, 'identifier': identifier, 'time': datetime.now()})
            return {'message': generic_message}

        raw_token = secrets.token_urlsafe(24)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = datetime.now() + timedelta(minutes=15)

        user_id = user.get('admin_id') or user.get('faculty_id') or user.get('student_id')
        university_id = user.get('university_id')

        self.password_reset_repo.create_token(role, int(user_id), int(university_id) if university_id is not None else None, token_hash, expires_at)
        self.audit_stack.push({'event': 'PASSWORD_RESET_REQUESTED', 'role': role, 'user_id': user_id, 'time': datetime.now()})

        # Returning token since outbound email/SMS isn't wired.
        return {
            'message': generic_message,
            'token': raw_token,
            'expires_in_seconds': 15 * 60
        }

    def reset_password_with_token(self, token: str, new_password: str):
        """Resets a password using a previously issued token."""
        if not token or not str(token).strip():
            raise ValidationError('Token is required')
        self._validate_new_password(new_password)

        token_hash = hashlib.sha256(str(token).strip().encode()).hexdigest()
        row = self.password_reset_repo.find_valid_by_hash(token_hash)
        if not row:
            raise ValidationError('Invalid or expired token')

        role = row.get('role')
        user_id = int(row.get('user_id'))
        new_hash = self._hash_password(new_password)

        if role == 'admin':
            ok = self.admin_repo.update_password(user_id, new_hash)
        elif role == 'faculty':
            ok = self.faculty_repo.update_password(user_id, new_hash)
        elif role == 'student':
            ok = self.student_repo.update_password(user_id, new_hash)
        else:
            raise ValidationError('Invalid role in token')

        if not ok:
            raise AuthenticationError('Failed to reset password')

        self.password_reset_repo.mark_used(int(row.get('token_id')))
        self.audit_stack.push({'event': 'PASSWORD_RESET_COMPLETED', 'role': role, 'user_id': user_id, 'time': datetime.now()})
        return {'message': 'Password reset successfully'}
