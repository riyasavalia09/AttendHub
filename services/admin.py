class AdminService:
    """
    Service to handle Admin domain logic.
    """

    def __init__(self, admin_repo, faculty_repo, student_repo, timetable_repo, lecture_repo, report_repo=None, audit_stack=None):
        self.admin_repo = admin_repo
        self.faculty_repo = faculty_repo
        self.student_repo = student_repo
        self.timetable_repo = timetable_repo
        self.lecture_repo = lecture_repo
        self.report_repo = report_repo
        self.audit_stack = audit_stack
        
    def get_dashboard_stats(self, university_id):
        """Fetches summary statistics for the dashboard."""
        
        # Get recent activity from stack
        recent_activity = []
        if self.audit_stack:
            # Stack.to_list() returns all items, 0 is top (most recent)
            all_logs = self.audit_stack.to_list()
            # Take top 5 and serialize for JSON
            for log in all_logs[:5]:
                log_copy = log.copy() # Safe copy
                if 'time' in log_copy:
                    # Format datetime to string
                    log_copy['time'] = log_copy['time'].strftime("%Y-%m-%d %H:%M:%S")
                recent_activity.append(log_copy)

        return {
            'total_faculty': self.faculty_repo.count_by_university(university_id),
            'total_students': self.student_repo.count_by_university(university_id),
            'active_timetables': self.timetable_repo.count_by_university(university_id),
            'today_lectures': self.lecture_repo.count_today_by_university(university_id),
            'recent_activity': recent_activity
        }

    def process_timetable_upload(self, university_id, rows):
        """
        Processes bulk timetable upload from CSV rows.
                Supported formats:
                - 6 columns (UI): Department, Semester, Day, Time, Subject, Faculty Name/Email
                    where Time is like "09:00 - 10:00".
                - 7 columns (legacy): Day, Start Time, End Time, Subject, Faculty Email, Department, Semester
        """
        import re
        from datetime import timedelta, time

        success_count = 0
        errors = []
        
        # Mapping for Days if needed (assuming input might be Full names)
        day_map = {
            'Monday': 'MON', 'Tuesday': 'TUE', 'Wednesday': 'WED', 
            'Thursday': 'THU', 'Friday': 'FRI', 'Saturday': 'SAT',
            'MON': 'MON', 'TUE': 'TUE', 'WED': 'WED', 
            'THU': 'THU', 'FRI': 'FRI', 'SAT': 'SAT'
        }

        def is_header_row(row):
            if not row:
                return False
            joined = ' '.join([str(c).strip().lower() for c in row if c is not None])
            return any(k in joined for k in ['day', 'department', 'semester', 'subject', 'faculty'])

        # Skip header if present
        if rows and is_header_row(rows[0]):
            rows = rows[1:]

        def parse_time_range(value: str):
            if not value:
                return None, None
            s = value.strip()
            # Accept: "09:00-10:00", "09:00 - 10:00", "09:00 to 10:00"
            parts = re.split(r"\s*(?:-|to)\s*", s, maxsplit=1)
            if len(parts) != 2:
                return None, None
            return parts[0].strip(), parts[1].strip()

        def resolve_faculty(identifier: str):
            if not identifier:
                return None
            ident = identifier.strip()
            if '@' in ident:
                return self.faculty_repo.find_by_email(ident)
            return self.faculty_repo.find_by_name_and_university(ident, university_id)

        def normalize_day(day_raw: str):
            if not day_raw:
                return None
            raw = day_raw.strip()
            return day_map.get(raw, day_map.get(raw.capitalize()))
             
        for i, row in enumerate(rows):
            try:
                row = [c.strip() if isinstance(c, str) else c for c in row]

                department = None
                semester = None
                day_raw = None
                start_time = None
                end_time = None
                subject = None
                faculty_identifier = None

                if len(row) >= 7:
                    # Legacy: Day, Start, End, Subject, Faculty Email, Department, Semester
                    day_raw = str(row[0] or '').strip()
                    start_time = str(row[1] or '').strip()
                    end_time = str(row[2] or '').strip()
                    subject = str(row[3] or '').strip()
                    faculty_identifier = str(row[4] or '').strip()
                    department = str(row[5] or '').strip()
                    semester = str(row[6] or '').strip()
                elif len(row) >= 6:
                    # UI: Department, Semester, Day, Time, Subject, Faculty Name/Email
                    department = str(row[0] or '').strip()
                    semester = str(row[1] or '').strip()
                    day_raw = str(row[2] or '').strip()
                    time_range = str(row[3] or '').strip()
                    subject = str(row[4] or '').strip()
                    faculty_identifier = str(row[5] or '').strip()

                    start_time, end_time = parse_time_range(time_range)
                else:
                    errors.append(
                        f"Row {i+1}: Insufficient columns. Expected 6 (Department, Semester, Day, Time, Subject, Faculty) or 7 (Day, Start, End, Subject, Faculty Email, Dept, Sem)."
                    )
                    continue

                if not department or not semester or not day_raw or not subject or not faculty_identifier:
                    errors.append(f"Row {i+1}: Missing required values.")
                    continue

                day = normalize_day(day_raw)
                if not day:
                    errors.append(f"Row {i+1}: Invalid Day '{day_raw}'.")
                    continue

                if not start_time or not end_time:
                    errors.append(f"Row {i+1}: Invalid time range. Use format like '09:00 - 10:00'.")
                    continue

                try:
                    semester_int = int(str(semester).strip())
                except Exception:
                    errors.append(f"Row {i+1}: Invalid semester '{semester}'.")
                    continue

                # Resolve Faculty by email (preferred) or by name
                faculty = resolve_faculty(faculty_identifier)
                if not faculty or faculty.get('university_id') != university_id:
                    errors.append(f"Row {i+1}: Faculty not found '{faculty_identifier}'.")
                    continue

                faculty_id = faculty.get('faculty_id')
                
                # Insert
                self.timetable_repo.create_timetable_entry(
                    university_id, faculty_id, department, semester_int, subject, day, start_time, end_time
                )
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {i+1}: {str(e)}")
                
        return {
            'success_count': success_count,
            'errors': errors,
            'message': f"Processed {success_count} entries. {len(errors)} errors found."
        }

    def get_timetable(self, university_id):
        """Retrieves formatted timetable for list view."""
        from datetime import timedelta, time

        def to_time_str(value):
            if value is None:
                return None
            if isinstance(value, timedelta):
                total_seconds = int(value.total_seconds())
                hours = (total_seconds // 3600) % 24
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            if isinstance(value, time):
                return value.strftime("%H:%M:%S")
            return value

        rows = self.timetable_repo.get_all_by_university(university_id) or []
        for r in rows:
            if isinstance(r, dict):
                r['start_time'] = to_time_str(r.get('start_time'))
                r['end_time'] = to_time_str(r.get('end_time'))
                timetable_id = r.get('timetable_id')
                r['has_lectures'] = bool(self.timetable_repo.has_existing_lectures(timetable_id)) if timetable_id else False
        return rows

    def get_reports(self, university_id):
        """Retrieves reports for the university."""
        if self.report_repo:
            return self.report_repo.get_all_by_university(university_id)
        return []
