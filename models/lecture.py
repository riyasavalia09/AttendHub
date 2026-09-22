from datetime import datetime

class Lecture:
    def __init__(self, lecture_id, faculty_id, subject_code, topic, start_time=None, is_active=True):
        self.id = lecture_id
        self.faculty_id = faculty_id
        self.subject_code = subject_code
        self.topic = topic
        self.start_time = start_time if start_time else datetime.now()
        self.is_active = is_active

class Attendance:
    def __init__(self, attendance_id, lecture_id, student_id, status, timestamp):
        self.id = attendance_id
        self.lecture_id = lecture_id
        self.student_id = student_id
        self.status = status
        self.timestamp = timestamp
