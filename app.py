from flask import Flask, render_template, Blueprint, request

from config import Config
from controllers.base_controller import BaseController
from exceptions.custom_exceptions import AppError

# 1. Import Data Structures
from data_structures.queue import Queue
from data_structures.stack import Stack
from data_structures.linked_list import LinkedList

# 2. Import Repositories
from repositories.admin_repository import AdminRepository
from repositories.university_repository import UniversityRepository
from repositories.faculty_repository import FacultyRepository
from repositories.student_repository import StudentRepository
from repositories.timetable_repository import TimetableRepository
from repositories.lecture_repository import LectureRepository
from repositories.attendance_repository import AttendanceRepository
from repositories.report_repository import ReportRepository
from repositories.password_reset_repository import PasswordResetRepository

# 3. Import Services
from services.auth import AuthService
from services.admin import AdminService
from services.faculty import FacultyService
from services.student import StudentService
from services.lecture import LectureService
from services.attendance import AttendanceService
from services.analytics import AnalyticsService
from services.timetable import TimetableService

# 4. Import Controllers
from controllers.auth import AuthController
from controllers.admin import AdminController
from controllers.faculty import FacultyController
from controllers.student import StudentController

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY


# ==========================================
# GLOBAL ERROR HANDLERS (API CONSISTENCY)
# ==========================================

@app.errorhandler(AppError)
def handle_app_error(err: AppError):
    return BaseController.error_response(message=err.message, status_code=err.code)


@app.errorhandler(404)
def handle_not_found(_err):
    if request.path.startswith('/api/'):
        return BaseController.error_response(message='Not Found', status_code=404)
    return 'Not Found', 404


@app.errorhandler(405)
def handle_method_not_allowed(_err):
    if request.path.startswith('/api/'):
        return BaseController.error_response(message='Method Not Allowed', status_code=405)
    return 'Method Not Allowed', 405


@app.errorhandler(Exception)
def handle_unexpected_error(_err):
    if request.path.startswith('/api/'):
        return BaseController.error_response(message='Internal Server Error', status_code=500)
    return 'Internal Server Error', 500

# ==========================================
# COMPOSITION ROOT - APPLICATION WIRING
# ==========================================

# --- A. Instantiate Data Structures ---
# Auth & System DS
login_queue = Queue()
audit_stack = Stack()
active_sessions = LinkedList()

# Lecture & Attendance DS
lecture_queue = Queue()
active_lectures_list = LinkedList()
attendance_queue = Queue()
# Using Python's built-in set for attendance duplicate check as per service design
attendance_set = set() 
# Using Python's built-in set for session duplicate check
session_set = set() # Note: AuthService handles this internally currently, or we can inject it if we refactored slightly. 
# Looking at AuthService: items are passed in __init__.

# --- B. Instantiate Repositories ---
# (Repositories are static classes in this design, but passing keys if needed)
admin_repo = AdminRepository
faculty_repo = FacultyRepository
student_repo = StudentRepository
university_repo = UniversityRepository
password_reset_repo = PasswordResetRepository
timetable_repo = TimetableRepository
lecture_repo = LectureRepository
attendance_repo = AttendanceRepository
report_repo = ReportRepository

# --- C. Instantiate Services (Dependency Injection) ---

# 1. Auth Service
auth_service = AuthService(
    admin_repo=admin_repo,
    faculty_repo=faculty_repo,
    student_repo=student_repo,
    university_repo=university_repo,
    password_reset_repo=password_reset_repo,
    queue=login_queue,
    stack=audit_stack,
    linked_list=active_sessions
)

# 2. Admin Service (Management Logic)
admin_service = AdminService(
    admin_repo=admin_repo,
    faculty_repo=faculty_repo,
    student_repo=student_repo,
    timetable_repo=timetable_repo,
    lecture_repo=lecture_repo,
    report_repo=report_repo,
    audit_stack=audit_stack
)

# 3. Faculty Service (Administrative Logic - CRUD)
faculty_mgmt_service = FacultyService(faculty_repo, audit_stack=audit_stack)

# 4. Student Service (Administrative/View Logic)
student_mgmt_service = StudentService(student_repo, timetable_repo, attendance_repo)

# 4.1 Timetable Service (Edit Workflow Logic)
timetable_service = TimetableService(timetable_repo=timetable_repo)

# 5. Lecture Service (Operational Logic)
lecture_service = LectureService(
    timetable_repo=timetable_repo,
    lecture_repo=lecture_repo,
    queue=lecture_queue,
    linked_list=active_lectures_list
)

# 6. Attendance Service (Operational Logic)
attendance_service = AttendanceService(
    attendance_repo=attendance_repo,
    student_repo=student_repo,
    lecture_repo=lecture_repo,
    queue=attendance_queue,
    attendance_set=attendance_set
)

# --- D. Instantiate Controllers (Dependency Injection) ---

auth_controller = AuthController(auth_service)

admin_controller = AdminController(
    admin_service=admin_service,
    faculty_service=faculty_mgmt_service,
    student_service=student_mgmt_service,
    timetable_service=timetable_service
)

faculty_controller = FacultyController(
    lecture_service=lecture_service,
    attendance_service=attendance_service,
    faculty_service=faculty_mgmt_service,
    student_service=student_mgmt_service
)

student_controller = StudentController(
    attendance_service=attendance_service,
    student_service=student_mgmt_service
)

# 7. Analytics Service (Decision-Oriented Dashboards)
analytics_service = AnalyticsService(attendance_repo=attendance_repo, student_repo=student_repo)

# Inject analytics service into controllers
admin_controller.analytics_service = analytics_service
faculty_controller.analytics_service = analytics_service
student_controller.analytics_service = analytics_service

# --- E. Create & Register Blueprints ---

# 1. Auth Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_bp.add_url_rule('/admin/signup', 'admin_signup', auth_controller.admin_signup, methods=['POST'])
auth_bp.add_url_rule('/admin/login', 'admin_login', auth_controller.admin_login, methods=['POST'])
auth_bp.add_url_rule('/faculty/login', 'faculty_login', auth_controller.faculty_login, methods=['POST'])
auth_bp.add_url_rule('/student/login', 'student_login', auth_controller.student_login, methods=['POST'])
auth_bp.add_url_rule('/logout', 'logout', auth_controller.logout, methods=['POST'])
auth_bp.add_url_rule('/change-password', 'change_password', auth_controller.change_password, methods=['POST'])
auth_bp.add_url_rule('/forgot-password', 'forgot_password', auth_controller.forgot_password, methods=['POST'])
auth_bp.add_url_rule('/reset-password', 'reset_password', auth_controller.reset_password, methods=['POST'])
app.register_blueprint(auth_bp)

# 2. Admin Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
admin_bp.add_url_rule('/dashboard/summary', 'dashboard_summary', admin_controller.get_dashboard_summary, methods=['GET'])
admin_bp.add_url_rule('/faculty/create', 'create_faculty', admin_controller.create_faculty, methods=['POST'])
admin_bp.add_url_rule('/faculty/update', 'update_faculty', admin_controller.update_faculty, methods=['POST'])
admin_bp.add_url_rule('/faculty/status', 'set_faculty_status', admin_controller.set_faculty_status, methods=['POST'])
admin_bp.add_url_rule('/student/create', 'create_student', admin_controller.create_student, methods=['POST'])
admin_bp.add_url_rule('/student/update', 'update_student', admin_controller.update_student, methods=['POST'])
admin_bp.add_url_rule('/student/status', 'set_student_status', admin_controller.set_student_status, methods=['POST'])
admin_bp.add_url_rule('/faculty/list', 'list_faculty', admin_controller.list_faculty, methods=['GET'])
admin_bp.add_url_rule('/student/list', 'list_students', admin_controller.list_students, methods=['GET'])
admin_bp.add_url_rule('/timetable/upload', 'upload_timetable', admin_controller.upload_timetable, methods=['POST'])
admin_bp.add_url_rule('/timetable/list', 'list_timetable', admin_controller.list_timetable, methods=['GET'])
admin_bp.add_url_rule('/timetable/<int:timetable_id>', 'get_timetable_item', admin_controller.get_timetable_item, methods=['GET'])
admin_bp.add_url_rule('/timetable/<int:timetable_id>', 'update_timetable_item', admin_controller.update_timetable, methods=['PUT'])
admin_bp.add_url_rule('/reports/list', 'list_reports', admin_controller.list_reports, methods=['GET'])
admin_bp.add_url_rule('/university/profile', 'get_university_profile', admin_controller.get_university_profile, methods=['GET'])
admin_bp.add_url_rule('/university/profile/update', 'update_university_profile', admin_controller.update_university_profile, methods=['POST'])
admin_bp.add_url_rule('/student/attendance-summary', 'student_attendance_summary', admin_controller.get_student_attendance_summary, methods=['GET'])
admin_bp.add_url_rule('/attendance/lowest', 'attendance_lowest', admin_controller.get_lowest_attendance_students, methods=['GET'])
admin_bp.add_url_rule('/analytics/departments-avg', 'departments_avg', admin_controller.get_department_averages, methods=['GET'])
admin_bp.add_url_rule('/analytics/university-trend', 'university_trend', admin_controller.get_university_trend, methods=['GET'])

app.register_blueprint(admin_bp)

# 3. Faculty Blueprint
faculty_bp = Blueprint('faculty', __name__, url_prefix='/api/faculty')
faculty_bp.add_url_rule('/context', 'context', faculty_controller.get_context, methods=['GET'])
faculty_bp.add_url_rule('/dashboard/summary', 'dashboard_summary', faculty_controller.get_dashboard_summary, methods=['GET'])
faculty_bp.add_url_rule('/profile', 'profile', faculty_controller.get_profile, methods=['GET'])
faculty_bp.add_url_rule('/lecture/start', 'start_lecture', faculty_controller.start_lecture, methods=['POST'])
faculty_bp.add_url_rule('/lecture/end', 'end_lecture', faculty_controller.end_lecture, methods=['POST'])
faculty_bp.add_url_rule('/schedule/today', 'get_schedule', faculty_controller.get_schedule, methods=['GET'])
faculty_bp.add_url_rule('/schedule/weekly', 'get_weekly_schedule', faculty_controller.get_weekly_schedule, methods=['GET'])
faculty_bp.add_url_rule('/students/list', 'list_students', faculty_controller.list_students, methods=['GET'])
faculty_bp.add_url_rule('/student/create', 'create_student', faculty_controller.create_student, methods=['POST'])
faculty_bp.add_url_rule('/attendance/mark', 'mark_attendance', faculty_controller.mark_attendance, methods=['POST'])
faculty_bp.add_url_rule('/attendance/history', 'get_history', faculty_controller.get_attendance_history, methods=['GET'])
faculty_bp.add_url_rule('/attendance/history/export', 'export_history', faculty_controller.export_attendance_history, methods=['GET'])
faculty_bp.add_url_rule('/attendance/today', 'attendance_today', faculty_controller.get_attendance_today, methods=['GET'])
faculty_bp.add_url_rule('/attendance/students', 'attendance_students', faculty_controller.get_students_for_lecture, methods=['GET'])
faculty_bp.add_url_rule('/lecture/stats', 'lecture_stats', faculty_controller.get_lecture_stats, methods=['GET'])
faculty_bp.add_url_rule('/lecture/trend', 'lecture_trend', faculty_controller.get_lecture_trend, methods=['GET'])
faculty_bp.add_url_rule('/analytics/overall-trend', 'overall_trend', faculty_controller.get_overall_trend, methods=['GET'])
app.register_blueprint(faculty_bp)

# 4. Student Blueprint
student_bp = Blueprint('student', __name__, url_prefix='/api/student')
student_bp.add_url_rule('/dashboard/summary', 'dashboard_summary', student_controller.get_dashboard_summary, methods=['GET'])
student_bp.add_url_rule('/attendance/history', 'get_history', student_controller.get_attendance_history, methods=['GET'])
student_bp.add_url_rule('/attendance', 'get_attendance_report', student_controller.get_attendance_report, methods=['GET'])
student_bp.add_url_rule('/profile', 'get_profile', student_controller.get_profile, methods=['GET'])
student_bp.add_url_rule('/timetable', 'get_timetable', student_controller.get_timetable, methods=['GET'])
student_bp.add_url_rule('/attendance/chart', 'attendance_chart', student_controller.get_attendance_chart, methods=['GET'])
student_bp.add_url_rule('/attendance/recent-trend', 'attendance_recent_trend', student_controller.get_recent_trend, methods=['GET'])
app.register_blueprint(student_bp)


# ==========================================
# FRONTEND ROUTES (Static Templates)
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin/login")
def admin_login_page():
    return render_template("admin/login.html")

@app.route("/admin/signup")
def admin_signup_page():
    return render_template("admin/signup.html")

@app.route("/admin/dashboard")
def admin_dashboard_page():
    return render_template("admin/dashboard.html")

@app.route("/admin/university-profile")
def admin_university_profile_page():
    return render_template("admin/university-profile.html")

@app.route("/admin/faculty")
def admin_faculty_page():
    return render_template("admin/manage-faculty.html")

@app.route("/admin/students")
def admin_students_page():
    return render_template("admin/manage-students.html")

@app.route("/admin/timetable")
def admin_timetable_page():
    return render_template("admin/manage-timetable.html")

@app.route("/admin/reports")
def admin_reports_page():
    return render_template("admin/reports.html")

@app.route("/admin/analysis")
def admin_analysis_page():
    return render_template("admin/analysis.html")

@app.route("/admin/system-config")
def admin_system_config_page():
    return render_template("admin/system-config.html")

@app.route("/admin/plan")
def admin_plan_page():
    return render_template("admin/plan-subscription.html")

@app.route("/faculty/login")
def faculty_login_page():
    return render_template("faculty/login.html")

@app.route("/faculty/dashboard")
def faculty_dashboard_page():
    return render_template("faculty/dashboard.html")

@app.route("/faculty/profile")
def faculty_profile_page():
    return render_template("faculty/profile.html")

@app.route("/faculty/schedule")
def faculty_schedule_page():
    return render_template("faculty/schedule.html")

@app.route("/faculty/start-lecture")
def faculty_start_lecture_page():
    return render_template("faculty/start-lecture.html")

@app.route("/faculty/mark-attendance")
def faculty_mark_attendance_page():
    return render_template("faculty/mark-attendance.html")

@app.route("/faculty/students")
def faculty_students_page():
    return render_template("faculty/student-list.html")

@app.route("/faculty/reports")
def faculty_reports_page():
    return render_template("faculty/reports.html")

@app.route("/faculty/analysis")
def faculty_analysis_page():
    return render_template("faculty/analysis.html")

@app.route("/student/login")
def student_login_page():
    return render_template("student/login.html")

@app.route("/student/dashboard")
def student_dashboard_page():
    return render_template("student/dashboard.html")

@app.route("/student/attendance")
def student_attendance_page():
    return render_template("student/attendance.html")

@app.route("/student/history")
def student_history_page():
    return render_template("student/history.html")

@app.route("/student/profile")
def student_profile_page():
    return render_template("student/profile.html")

@app.route("/student/timetable")
def student_timetable_page():
    return render_template("student/timetable.html")

@app.route("/student/reports")
def student_reports_page():
    return render_template("student/reports.html")

@app.route("/student/analysis")
def student_analysis_page():
    return render_template("student/analysis.html")

@app.route("/forgot-password")
def forgot_password_page():
    return render_template("forgot-password.html")

if __name__ == "__main__":
    app.run(debug=False)

