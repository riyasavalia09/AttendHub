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

| Category | Technologies |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML5, CSS3, JavaScript |
| UI Framework | Bootstrap 5 |
| Database | MySQL |
| Database Connectivity | MySQL Connector/Python |
| Authentication | Session-based Authentication |
| Authorization | Role-Based Access Control |
| Data Structures | Stack, Queue, Linked List |
| Configuration | Environment Variables |
| Version Control | Git & GitHub |

---

## Data Structures Implementation

One of the technical aspects of AttendHub is the practical use of data structures within application workflows.

### Stack

Used for operations where **Last-In-First-Out (LIFO)** behavior is useful.

**Example:**

```text
Stack
 ├── Latest operation
 ├── Previous operation
 └── Older operation
