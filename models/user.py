class User:
    """Domain model representing a user"""
    
    def __init__(self, user_id, name, email, role, university_id, is_active=True):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role
        self.university_id = university_id
        self.is_active = is_active
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'university_id': self.university_id,
            'is_active': self.is_active
        }
    
    @staticmethod
    def from_dict(data, role):
        if role == 'admin':
            return User(
                user_id=data.get('admin_id'),
                name=data.get('name'),
                email=data.get('email'),
                role='admin',
                university_id=data.get('university_id'),
                is_active=data.get('is_verified', True)
            )
        elif role == 'faculty':
            return User(
                user_id=data.get('faculty_id'),
                name=data.get('name'),
                email=data.get('email'),
                role='faculty',
                university_id=data.get('university_id'),
                is_active=data.get('is_active', True)
            )
        elif role == 'student':
            return User(
                user_id=data.get('student_id'),
                name=data.get('name'),
                email=data.get('email', data.get('enrollment_no')),
                role='student',
                university_id=data.get('university_id'),
                is_active=data.get('is_active', True)
            )
        return None


class AuthAttempt:
    """Domain model representing an authentication attempt"""
    
    def __init__(self, email, role, success, timestamp, reason=None):
        self.email = email
        self.role = role
        self.success = success
        self.timestamp = timestamp
        self.reason = reason
    
    def to_dict(self):
        return {
            'email': self.email,
            'role': self.role,
            'success': self.success,
            'timestamp': self.timestamp,
            'reason': self.reason
        }
