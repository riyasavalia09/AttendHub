import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'attendhub_db')
    
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    ROLE_PERMISSIONS = {
        'admin': ('create_faculty', 'create_student', 'manage_timetable', 'view_reports'),
        'faculty': ('start_lecture', 'mark_attendance', 'create_student', 'view_reports'),
        'student': ('mark_self_attendance', 'view_own_attendance')
    }
    
    @staticmethod
    def get_db_connection_params():
        return {
            'host': Config.MYSQL_HOST,
            'port': Config.MYSQL_PORT,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DATABASE
        }
