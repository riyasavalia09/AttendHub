AttendHub — Role-Based University Attendance Management System

<p align="center">Smart • Secure • Role-Based Attendance Management

A full-stack university attendance management platform built with Python, Flask, MySQL, HTML, CSS, JavaScript and Bootstrap.

</p>---

## Overview

AttendHub is a web-based attendance management system designed to digitize and simplify university attendance operations.

The system provides dedicated interfaces for Administrators, Faculty Members, and Students, with role-based access to attendance, timetable, lecture, user management, analytics, and reporting features.

The project follows a layered backend architecture that separates controllers, business logic, database operations, and data structures, making the application easier to maintain, extend, and understand.

---

## Problem Statement

Traditional attendance management can involve repetitive manual work, scattered records, difficulty tracking attendance percentages, and limited visibility into attendance trends.

AttendHub addresses these challenges by providing a centralized platform where:

- Administrators manage the academic environment and users.
- Faculty members manage lectures and student attendance.
- Students monitor their own attendance and academic records.
- Attendance data can be analyzed through dashboards and reports.

---

## Key Features

## Admin Module

- Admin authentication
- University profile management
- Faculty management
- Student management
- Timetable management
- Lecture management
- Attendance analytics
- Attendance summaries
- Reports and statistics
- Role-based access control
- Password management

##  Faculty Module

- Faculty authentication
- Faculty dashboard
- Personal profile
- Timetable viewing
- Lecture management
- Start/end lecture workflow
- Student attendance marking
- Attendance history
- Student-wise attendance information
- Attendance analytics
- Attendance trends
- Attendance reports

## Student Module

- Student authentication
- Student dashboard
- Personal profile
- Timetable viewing
- Attendance overview
- Attendance history
- Attendance percentage
- Attendance analytics
- Attendance trends
- Attendance reports

---

## Authentication & Authorization

AttendHub implements role-based authentication and authorization.

User Roles

                    ┌───────────────┐
                    │     Admin     │
                    └───────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
         University      Faculty       Students
          Management    Management     Management

                    ┌───────────────┐
                    │    Faculty    │
                    └───────┬───────┘
                            │
                     Attendance /
                    Lecture Management

                    ┌───────────────┐
                    │    Student    │
                    └───────┬───────┘
                            │
                    Attendance /
                     Profile /
                     Timetable

Protected routes and role-specific functionality prevent users from accessing features outside their assigned responsibilities.

---

##  System Architecture

AttendHub uses a layered architecture to separate responsibilities.

┌─────────────────────────────────────────────┐
│                 Frontend                    │
│        HTML • CSS • JavaScript              │
│               Bootstrap                     │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│              Flask Application               │
│                  app.py                     │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│               Controllers                   │
│       Request Handling & API Routes         │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│                 Services                    │
│             Business Logic                 │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│               Repositories                  │
│             Database Access                │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│                   MySQL                    │
│               Relational DB                │
└─────────────────────────────────────────────┘

Why this architecture?

The application separates:

- HTTP/API handling
- Business logic
- Database operations
- Authentication and authorization
- Data structure implementations

This reduces coupling and makes individual modules easier to maintain and test.

---

##  Project Structure

AttendHub/
│
├── app.py
├── config.py
├── db_connection.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── db.sql
├── seed_data.py
│
├── controllers/
│   ├── admin.py
│   ├── auth.py
│   ├── base_controller.py
│   ├── faculty.py
│   └── student.py
│
├── services/
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
│   ├── admin_repository.py
│   ├── attendance_repository.py
│   ├── faculty_repository.py
│   ├── lecture_repository.py
│   ├── password_reset_repository.py
│   ├── report_repository.py
│   ├── student_repository.py
│   ├── timetable_repository.py
│   └── university_repository.py
│
├── models/
├── exceptions/
│
├── data_structures/
│   ├── linked_list.py
│   ├── queue.py
│   └── stack.py
│
├── templates/
│   ├── index.html
│   ├── forgot-password.html
│   ├── admin/
│   ├── faculty/
│   └── student/
│
└── static/
    ├── CSS/
    └── JS/

---

## Technology Stack

Category| Technologies
Backend| Python, Flask
Frontend| HTML5, CSS3, JavaScript
UI| Bootstrap 5
Database| MySQL
Database Connector| MySQL Connector/Python
Authentication| Session-based Authentication
Authorization| Role-Based Access Control
Data Structures| Stack, Queue, Linked List
Configuration| Environment Variables
Version Control| Git & GitHub

---

## Data Structures Implementation

One of the technical aspects of AttendHub is the practical use of data structures within application workflows.

Stack

Used for operations where Last-In-First-Out (LIFO) behavior is useful.

Stack
 ↓
Latest operation
 ↓
Previous operation
 ↓
Older operation

Queue

Used for workflows where First-In-First-Out (FIFO) processing is required.

Front → [Request 1] [Request 2] [Request 3] ← Rear

Linked List

Used for dynamic sequential data and session/lecture-related tracking.

These implementations demonstrate how academic data-structure concepts can be integrated into a real-world web application.

---

## Database Design

AttendHub uses MySQL as its relational database.

Important entities include:

University
    │
    ├── Admin
    │
    ├── Faculty
    │
    └── Student
          │
          └── Attendance
          
Faculty
   │
   └── Lectures
          │
          └── Attendance

University
   │
   └── Timetable

Main Database Tables

- "universities"
- "admins"
- "faculty"
- "students"
- "timetable"
- "lectures"
- "attendance"
- "reports"

The database uses relational constraints such as:

- Primary Keys
- Foreign Keys
- Unique Constraints
- Indexes
- Aggregation Queries

---

## Attendance Analytics

The analytics module provides insights such as:

- Student attendance percentage
- Attendance summaries
- Attendance history
- Attendance trends
- Faculty/lecture statistics
- Low-attendance identification
- Aggregated attendance information

These features help convert raw attendance records into meaningful information for administrators, faculty, and students.

---

## Security Features

AttendHub includes several security-oriented mechanisms:

- Session-based authentication
- Role-based authorization
- Password hashing
- Protected routes
- Environment-based configuration
- Input validation
- Database constraints
- Centralized exception handling

Sensitive configuration such as database passwords and secret keys should be stored in ".env" and should never be committed to GitHub.

---

##  Installation & Setup

1. Clone the repository

git clone <YOUR-GITHUB-REPOSITORY-URL>
cd AttendHub

2. Create a virtual environment

python -m venv venv

Windows

venv\Scripts\activate

macOS/Linux

source venv/bin/activate

---

3. Install dependencies

pip install -r requirements.txt

---

4. Configure environment variables

Create a ".env" file in the project root.

Use ".env.example" as the template.

SECRET_KEY=your-secret-key

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DATABASE=aa

«Do not commit the ".env" file to GitHub.»

---

5. Configure MySQL

Make sure MySQL is installed and running.

Create the required database and execute:

db.sql

The SQL file contains the schema required by AttendHub.

---

6. Run the application

python app.py

Open:

http://127.0.0.1:5000

<!-- ---
## Screenshots

Screenshots of the following interfaces can be added here:

Login

Add login page screenshot here.

Admin Dashboard

Add admin dashboard screenshot here.

Faculty Dashboard

Add faculty dashboard screenshot here.

Student Dashboard

Add student dashboard screenshot here.

Attendance Analytics

Add analytics screenshot here.

Timetable

Add timetable screenshot here.

--- -->

##  Application Workflow

User
  │
  ▼
Login
  │
  ▼
Authentication
  │
  ▼
Role Detection
  │
  ├───────────────┬────────────────┐
  ▼               ▼                ▼
Admin           Faculty          Student
  │               │                │
  ▼               ▼                ▼
Management     Attendance       Attendance
Analytics      Lectures         Analytics
Reports        Timetable        Timetable
  │               │                │
  └───────────────┴────────────────┘
                  │
                  ▼
                MySQL

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
- Data structures
- Form validation
- Modular project architecture

---

## Future Enhancements

Possible future improvements include:

- QR-code based attendance
- Face-recognition based attendance
- Email/SMS attendance notifications
- Mobile application
- Cloud deployment
- Advanced predictive analytics
- Automated report generation
- Multi-university deployment
- Improved production-grade authentication and password security

---
## Learning Outcomes

Through this project, the following practical concepts were explored:

- Designing a multi-role web application
- Connecting Flask with MySQL
- Separating business logic from database operations
- Implementing authentication and authorization
- Working with relational database constraints
- Implementing data structures in application workflows
- Building dashboards and analytics
- Organizing a scalable project structure
- Managing configuration securely with environment variables

---

