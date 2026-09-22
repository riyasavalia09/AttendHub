# AttendHub

A Role-Based University Attendance Management and Analytics Platform built using Python, Flask, HTML, CSS, JavaScript, Bootstrap 5, and MySQL.

AttendHub is designed to simplify university attendance management by providing separate functionality for administrators, faculty members, and students. The system provides attendance tracking, lecture management, timetable management, analytics, reports, authentication, authorization, and role-based access control.

---

## Features

### Authentication & Authorization

- Admin signup and login
- Faculty login
- Student login
- Session-based authentication
- Role-based authorization
- Protected routes
- Password change functionality
- Forgot password workflow
- Password reset functionality
- Secure environment-based configuration

### Admin

- University management
- Faculty management
- Student management
- Faculty status management
- Student status management
- Timetable management
- Attendance management
- Analytics
- Reports
- University profile management

### Faculty

- Faculty dashboard
- Lecture management
- Lecture scheduling
- Attendance management
- Student information
- Attendance analytics
- Reports
- Faculty profile management

### Student

- Student dashboard
- Attendance information
- Attendance history
- Timetable
- Attendance analytics
- Reports
- Student profile management

---

## Analytics

AttendHub provides analytics-oriented functionality for attendance monitoring and reporting.

Analytics features include:

- Student attendance summary
- Students with low attendance
- Department-wise attendance averages
- University attendance trends
- Attendance reports
- Faculty attendance information
- Student attendance information

These features help users understand attendance patterns and monitor academic attendance effectively.

---

## System Architecture

AttendHub follows a layered architecture to separate different application responsibilities.

    Frontend
        |
        | HTML + CSS + JavaScript + Bootstrap
        v
    Flask Application
        |
        v
    Controllers
        |
        | Request Handling & API Routes
        v
    Services
        |
        | Business Logic
        v
    Repositories
        |
        | Database Access
        v
    MySQL
        |
        v
    Relational Database

### Why this architecture?

The application separates:

- HTTP/API handling
- Business logic
- Database operations
- Authentication and authorization
- Data structure implementations

This reduces coupling and makes individual modules easier to maintain, test, and extend.

---

## Project Structure

    AttendHub/
    |
    |-- app.py
    |-- config.py
    |-- db_connection.py
    |-- db.sql
    |-- requirements.txt
    |-- .env.example
    |-- .gitignore
    |-- README.md
    |
    |-- controllers/
    |   |-- __init__.py
    |   |-- admin.py
    |   |-- auth.py
    |   |-- base_controller.py
    |   |-- faculty.py
    |   |-- student.py
    |
    |-- services/
    |   |-- admin.py
    |   |-- analytics.py
    |   |-- attendance.py
    |   |-- auth.py
    |   |-- authorization.py
    |   |-- faculty.py
    |   |-- lecture.py
    |   |-- session.py
    |   |-- student.py
    |   |-- timetable.py
    |
    |-- repositories/
    |   |-- admin_repository.py
    |   |-- attendance_repository.py
    |   |-- faculty_repository.py
    |   |-- lecture_repository.py
    |   |-- password_reset_repository.py
    |   |-- report_repository.py
    |   |-- student_repository.py
    |   |-- timetable_repository.py
    |   |-- university_repository.py
    |
    |-- models/
    |   |-- __init__.py
    |   |-- lecture.py
    |   |-- university.py
    |   |-- user.py
    |
    |-- data_structures/
    |   |-- __init__.py
    |   |-- linked_list.py
    |   |-- queue.py
    |   |-- stack.py
    |
    |-- exceptions/
    |   |-- __init__.py
    |   |-- auth.py
    |   |-- custom_exceptions.py
    |
    |-- templates/
    |   |-- index.html
    |   |-- forgot-password.html
    |   |-- password.html
    |   |-- admin/
    |   |-- faculty/
    |   |-- student/
    |
    |-- static/
        |-- css/
        |-- js/

---

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

A Stack is used for operations where Last-In-First-Out (LIFO) behavior is useful.

Example:

    Stack
    |
    |-- Latest operation
    |-- Previous operation
    |-- Older operation

### Queue

A Queue is used for workflows where First-In-First-Out (FIFO) processing is required.

Example:

    Queue
    |
    |-- First request
    |-- Second request
    |-- Next request

### Linked List

A Linked List is used for dynamic sequential data and session or lecture-related tracking.

These implementations demonstrate how academic data-structure concepts can be integrated into a real-world web application.

---

## Database Design

AttendHub uses MySQL as its relational database.

### Main Entities

    University
    |
    |-- Admin
    |-- Faculty
    |-- Student
    |-- Attendance

    Faculty
    |
    |-- Lectures
    |-- Attendance

    University
    |
    |-- Timetable

### Main Database Tables

- universities
- admins
- faculty
- students
- timetable
- lectures
- attendance
- reports

### Database Constraints

The database uses relational constraints such as:

- Primary Keys
- Foreign Keys
- Unique Constraints
- Indexes
- Aggregation Queries

The SQL schema required by AttendHub is provided in the db.sql file.

---

## API Structure

AttendHub uses Flask to organize API routes and application functionality.

### Authentication APIs

    /api/auth/admin/signup
    /api/auth/admin/login
    /api/auth/faculty/login
    /api/auth/student/login
    /api/auth/logout
    /api/auth/change-password
    /api/auth/forgot-password
    /api/auth/reset-password

### Admin APIs

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
    /api/admin/faculty/details
    /api/admin/reports/list
    /api/admin/university/profile
    /api/admin/university/profile/update

### Faculty APIs

Faculty functionality includes:

- Faculty dashboard
- Faculty routes
- Faculty password management
- Faculty content management
- Lecture management
- Attendance management
- Student information
- Reports
- Analytics
- Faculty profile

### Student APIs

Student functionality includes:

- Student profile
- Student attendance
- Attendance history
- Timetable
- Reports
- Analytics
- Student information

---

## Security

AttendHub includes several security-related mechanisms to protect users and application resources.

### Security Features

- Session-based authentication
- Role-based authorization
- Protected routes
- Password reset workflow
- Environment-based configuration
- Secret key configuration
- API error handling
- Input validation
- Password protection
- Role-specific access control

Protected routes and role-specific functionality prevent users from accessing features outside their assigned responsibilities.

### Environment Variables

Sensitive configuration values should be stored in environment variables instead of being committed to the repository.

Example:

    SECRET_KEY=your_secret_key
    DB_HOST=localhost
    DB_USER=your_database_user
    DB_PASSWORD=your_database_password
    DB_NAME=attendhub

Use the .env.example file as a reference.

Never commit your actual .env file, passwords, secret keys, or other sensitive credentials to GitHub.

---

## Application Workflow

    User
      |
      v
    Login
      |
      v
    Authentication
      |
      v
    Role Detection
      |
      +-------------------+-------------------+
      |                   |                   |
      v                   v                   v
    Admin              Faculty             Student
      |                   |                   |
      |                   |                   |
      v                   v                   v
    Management          Lectures           Attendance
    Attendance          Attendance         Attendance History
    Analytics            Analytics          Timetable
    Reports              Reports            Analytics
    Timetable            Profile            Reports
      |                   |                   |
      +-------------------+-------------------+
                          |
                          v
                        MySQL

---

## Installation & Setup

### 1. Clone the Repository

    git clone https://github.com/riyasavaliya09/AttendHub.git
    cd AttendHub

### 2. Create a Virtual Environment

    python -m venv venv

### 3. Activate the Virtual Environment

#### Windows

    venv\Scripts\activate

#### macOS / Linux

    source venv/bin/activate

### 4. Install Dependencies

    pip install -r requirements.txt

### 5. Configure Environment Variables

Create a .env file using .env.example as a reference.

Example:

    SECRET_KEY=your_secret_key
    DB_HOST=localhost
    DB_USER=your_database_user
    DB_PASSWORD=your_database_password
    DB_NAME=attendhub

### 6. Setup the Database

Create the MySQL database and execute the SQL schema provided in:

    db.sql

You can import the SQL file using MySQL Workbench or the MySQL command line.

### 7. Run the Application

    python app.py

### 8. Open in Browser

    http://127.0.0.1:5000

---

## Project Highlights

AttendHub demonstrates practical implementation of:

- Full-stack web development
- Flask backend development
- REST-style API design
- Role-based access control
- Authentication and sessions
- MySQL database design
- Repository-based data access
- Service-layer business logic
- Attendance analytics
- Data structure implementation
- Secure environment configuration

---

## Future Scope

Possible future improvements include:

- Email notifications for low attendance
- Mobile application support
- Advanced attendance analytics
- Automated attendance using QR codes
- AI-based attendance insights
- Cloud deployment
- Real-time notifications
- Advanced reporting and visualization
- Automated database backup and recovery

---
