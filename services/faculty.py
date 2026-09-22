
import hashlib
from exceptions.custom_exceptions import DuplicateRecordError, ValidationError, RecordNotFoundError

class FacultyService:
    """
    Service to handle Faculty domain logic.
    """

    def __init__(self, faculty_repo, audit_stack=None):
        """
        Constructor with Dependency Injection.
        """
        self.faculty_repo = faculty_repo
        self.audit_stack = audit_stack

    def create_faculty(self, university_id, name, email, department, password):
        """Creates a new faculty member."""
        # 1. Check for duplicates
        if self.faculty_repo.find_by_email(email):
            raise DuplicateRecordError("Faculty with this email already exists")

        # 2. Hash Password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # 3. Create Record
        faculty_id = self.faculty_repo.create_faculty(university_id, name, email, department, hashed_password)

        # 4. Audit Log
        if self.audit_stack:
            from datetime import datetime
            self.audit_stack.push({
                'event': 'FACULTY_CREATED',
                'user': 'Admin', # Ideally we'd pass the current admin user here
                'role': 'admin',
                'time': datetime.now()
            })

        return faculty_id

    def get_all_by_university(self, university_id):
        """Returns all faculty for a university."""
        return self.faculty_repo.find_all_by_university(university_id)

    def set_status(self, university_id, faculty_id, is_active: bool):
        faculty = self.faculty_repo.find_by_id(faculty_id)
        if not faculty or faculty.get('university_id') != university_id:
            raise RecordNotFoundError('Faculty not found')
        return self.faculty_repo.update_status(faculty_id, is_active)

    def update_faculty(self, university_id, faculty_id, name, email, department, password=None):
        faculty = self.faculty_repo.find_by_id(faculty_id)
        if not faculty or faculty.get('university_id') != university_id:
            raise RecordNotFoundError('Faculty not found')

        if not name or not email or not department:
            raise ValidationError('name, email, and department are required')

        password_hash = None
        if password:
            if len(password) < 6:
                raise ValidationError('Password must be at least 6 characters')
            password_hash = hashlib.sha256(password.encode()).hexdigest()

        return self.faculty_repo.update_faculty_profile(faculty_id, name, email, department, password_hash)

    def get_context(self, faculty_id: int):
        """Returns minimal faculty context for UI layout scripts."""
        faculty = self.faculty_repo.find_by_id(faculty_id)
        if not faculty:
            raise RecordNotFoundError('Faculty not found')

        return {
            'faculty': {
                'faculty_id': faculty.get('faculty_id'),
                'name': faculty.get('name'),
                'email': faculty.get('email'),
                'department': faculty.get('department'),
                'university_id': faculty.get('university_id'),
            }
        }

    def get_profile(self, faculty_id: int):
        """Returns faculty profile data safe for UI consumption."""
        faculty = self.faculty_repo.find_by_id(faculty_id)
        if not faculty:
            raise RecordNotFoundError('Faculty not found')

        return {
            'faculty': {
                'faculty_id': faculty.get('faculty_id'),
                'name': faculty.get('name'),
                'email': faculty.get('email'),
                'department': faculty.get('department'),
                'is_active': faculty.get('is_active'),
                'university_id': faculty.get('university_id'),
            }
        }
