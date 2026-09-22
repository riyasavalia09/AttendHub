# AttendHub 

### Role-Based University Attendance & Analytics Platform

AttendHub is a full-stack university attendance management system built with **Python, Flask, MySQL, HTML, CSS, JavaScript, and Bootstrap**.

The platform provides separate functionality for **Administrators, Faculty, and Students**, with role-based access control, attendance management, lecture management, timetable management, analytics, reports, authentication, and password recovery.

---

##  Overview

AttendHub is designed to simplify and digitize university attendance workflows.

The system provides:

- Role-based authentication
- Separate Admin, Faculty, and Student dashboards
- Faculty and student management
- Lecture scheduling and management
- Attendance marking and tracking
- Attendance analytics
- Attendance reports
- University profile management
- Timetable management
- Password change and password recovery
- Session-based authentication
- Role-based authorization
- MySQL database integration
- Custom data structure implementations

---

##  Key Features

###  Authentication & Authorization

- Admin signup and login
- Faculty login
- Student login
- Logout functionality
- Change password
- Forgot password
- Password reset
- Session-based authentication
- Role-based access control
- Protected routes

###  Admin Module

Administrators can manage the university attendance system.

**Admin capabilities:**

- Manage faculty
- Manage students
- Activate/deactivate users
- Manage timetable
- Upload timetable
- Update timetable entries
- View university profile
- Update university profile
- View attendance reports
- View attendance summaries
- View department attendance averages
- View university attendance trends
- View students with low attendance
- Access analytics dashboard

###  Faculty Module

Faculty members can manage lectures and student attendance.

**Faculty capabilities:**

- Faculty dashboard
- View assigned students
- View schedule
- Start lectures
- Mark attendance
- View attendance information
- View reports
- View analytics
- Manage faculty profile

###  Student Module

Students can access their academic attendance information.

**Student capabilities:**

- Student dashboard
- View attendance
- View attendance history
- View timetable
- View reports
- View attendance analytics
- View student profile

---

##  System Architecture

AttendHub follows a layered architecture to separate application responsibilities.

| Layer | Responsibility |
|---|---|
| Frontend | HTML, CSS, JavaScript, Bootstrap |
| Flask Application | Application entry point and API configuration |
| Controllers | Request handling and API routes |
| Services | Business logic and application workflows |
| Repositories | Database access and data operations |
| MySQL | Relational database |

### Why this architecture?

The application separates:

- HTTP/API handling
- Business logic
- Database operations
- Authentication
- Authorization
- Data structure implementations

This separation makes the application easier to maintain, test, and extend.

---

## Project Structure

```text
AttendHub/
│
├── app.py
├── config.py
├── db_connection.py
├── db.sql
├── requirements.txt
├── .env.example
├── .gitignore
│
├── controllers/
│   ├── __init__.py
│   ├── admin.py
│   ├── auth.py
│   ├── base_controller.py
│   ├── faculty.py
│   └── student.py
│
├── services/
│   ├── __init__.py
│   ├── admin.py
│   ├── analytics.py
│   ├── attendance.py
│   ├── auth.py
│   ├── authorization.py
│   ├── faculty.py
│   ├── lecture.py
│   ├── session.py
│   ├── student.py
│   └── timetable.py
│
├── repositories/
│   ├── __init__.py
│   ├── admin_repository.py
│   ├── attendance_repository.py
│   ├── base_repository.py
│   ├── faculty_repository.py
│   ├── lecture_repository.py
│   ├── password_reset_repository.py
│   ├── report_repository.py
│   ├── student_repository.py
│   ├── timetable_repository.py
│   └── university_repository.py
│
├── models/
│   ├── __init__.py
│   ├── lecture.py
│   ├── university.py
│   └── user.py
│
├── data_structures/
│   ├── __init__.py
│   ├── linked_list.py
│   ├── queue.py
│   └── stack.py
│
├── exceptions/
│   ├── __init__.py
│   ├── auth.py
│   └── custom_exceptions.py
│
├── templates/
│   ├── index.html
│   ├── forgot-password.html
│   ├── admin/
│   ├── faculty/
│   └── student/
│
├── static/
│   ├── CSS/
│   └── JS/
│
└── database utility and migration scripts

## Technology Stack
Category
Technologies
Backend
Python, Flask
Frontend
HTML5, CSS3, JavaScript
UI Framework
Bootstrap 5
Database
MySQL
Database Connector
mysql-connector-python
Authentication
Session-based Authentication
Authorization
Role-Based Access Control
Data Structures
Stack, Queue, Linked List, Set
Configuration
Python dotenv
API
REST-style API
Version Control
Git & GitHub
## Data Structures Implementation
One of the important technical aspects of AttendHub is the practical implementation of data structures within application workflows.
Stack
A custom Stack implementation is used where Last-In-First-Out (LIFO) behavior is useful.
Example:
Top
 ↓
Latest Operation
Previous Operation
Older Operation
Queue
A custom Queue implementation follows First-In-First-Out (FIFO) behavior.
It can be used for sequential processing workflows such as requests and lecture-related operations.
Front
 ↓
First Request → Next Request → Latest Request
                                      ↓
                                     Rear
Linked List
A custom Singly Linked List is implemented for sequential data management.
It is used for tracking sequential application data such as active sessions and lecture-related information.
Set
Python's built-in set is used where uniqueness is important.
Examples:
Duplicate checking
Unique session tracking
Unique attendance-related values
## Database Design
AttendHub uses MySQL as its relational database.
Main Database Tables
Table
Purpose
universities
Stores university information
admins
Stores administrator information
faculty
Stores faculty information
students
Stores student information
timetable
Stores timetable and schedule information
lectures
Stores lecture records
attendance
Stores attendance records
reports
Stores/report-related attendance information
The database uses relational concepts such as:
Primary Keys
Foreign Keys
Unique Constraints
Indexes
Relational relationships
## Application Workflow
The general application workflow is:
User
  ↓
Login
  ↓
Authentication
  ↓
Role Detection
  ↓
Role-Based Dashboard
  ↓
Application Features
  ↓
Service Layer
  ↓
Repository Layer
  ↓
MySQL Database
User Roles
Role
Main Responsibilities
Admin
University, faculty, students, timetable, analytics and reports
Faculty
Lectures, schedules, attendance, analytics and reports
Student
Attendance, timetable, history, analytics and reports
## Analytics
AttendHub provides analytics-oriented functionality for attendance management.
Analytics features include:
Student attendance summary
Students with low attendance
Department-wise attendance averages
University attendance trends
Attendance reports
Faculty attendance information
Student attendance information
## API Structure
AttendHub uses Flask to organize API routes and application functionality.
Authentication APIs
/api/auth/admin/signup
/api/auth/admin/login
/api/auth/faculty/login
/api/auth/student/login
/api/auth/logout
/api/auth/change-password
/api/auth/forgot-password
/api/auth/reset-password
Admin APIs
/api/admin/dashboard/summary
/api/admin/faculty/create
/api/admin/faculty/update
/api/admin/faculty/status
/api/admin/student/create
/api/admin/student/update
/api/admin/student/status
/api/admin/faculty/list
/api/admin/student/list
/api/admin/timetable/upload
/api/admin/timetable/list
/api/admin/reports/list
/api/admin/university/profile
/api/admin/university/profile/update
Faculty APIs
Faculty routes handle:
Faculty dashboard
Faculty context
Lecture management
Attendance management
Student information
Reports
Analytics
Faculty profile
Student APIs
Student routes handle:
Student dashboard
Attendance
Attendance history
Timetable
Reports
Analytics
Student profile
## Security
AttendHub includes several security-related mechanisms:
Session-based authentication
Role-based authorization
Protected routes
Password reset workflow
Environment-based configuration
Secret key configuration
API error handling
Input validation
Sensitive configuration values are stored using environment variables instead of being hard-coded.
Never commit your actual .env file or database password to GitHub.
## Installation & Setup
1. Clone the Repository
git clone https://github.com/riyasaavaliya09/AttendHub.git
cd AttendHub
2. Create a Virtual Environment
python -m venv venv
Windows
venv\Scripts\activate
macOS / Linux
source venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
Main dependencies include:
Flask
mysql-connector-python
python-dotenv
## MySQL Configuration
Make sure MySQL Server is installed and running.
Create a .env file from .env.example.
Example:
SECRET_KEY=your-secret-key

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DATABASE=your-database-name
Update the values according to your local MySQL configuration.
## Database Setup
The main database schema is available in:
db.sql
Import the SQL file using MySQL Workbench or the MySQL command-line client.
After importing the database, make sure the database credentials in .env match your MySQL configuration.
## Run the Application
Start the Flask application:
python app.py
The application will be available at:
http://127.0.0.1:5000
Open the URL in your browser.
## Database Utility & Migration Scripts
The project also contains database-related utility and patch scripts for maintaining and updating the database.
Examples include:
db_patch_analytics_indexes.sql
db_patch_lecture_state.sql
db_patch_password_reset.sql
db_patch_reports.sql
db_patch_timetable_sunday.sql
db_patch_university_profile.sql
init_db.py
patch_db.py
migrate_lecture_snapshots.py
seed_data.py
insert_dummy_data.py
Use these scripts according to the project's database setup and migration requirements.
## Error Handling
AttendHub contains custom exception handling to provide consistent application behavior.
The project includes:
Authentication exceptions
Custom application exceptions
Validation errors
Record-not-found handling
API error responses
HTTP error handling
Protected route handling
## Project Highlights
AttendHub demonstrates practical implementation of:
Full-stack web development
Flask backend development
REST-style API design
Layered software architecture
Role-based access control
Session-based authentication
MySQL database design
Repository-based data access
Service-layer business logic
Custom data structures
Attendance management
Attendance analytics
Timetable management
Git and GitHub workflow
## Future Scope
Possible future improvements include:
Email notifications
Mobile application
Advanced attendance prediction
Automated attendance using face recognition
Advanced analytics dashboards
Cloud deployment
Automated database backups
Low-attendance notifications
Multi-campus support
## Learning Outcomes
Through AttendHub, the project demonstrates practical understanding of:
Python programming
Flask web development
Frontend development
REST APIs
MySQL
Database connectivity
Authentication and authorization
Software architecture
Data structures
Git and GitHub
Modular application development
