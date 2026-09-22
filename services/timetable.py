from datetime import datetime

from exceptions.custom_exceptions import RecordNotFoundError, ValidationError


class TimetableService:
    """Service layer for timetable read/update workflows."""

    def __init__(self, timetable_repo):
        self.timetable_repo = timetable_repo

    @staticmethod
    def _normalize_day(day_value):
        day_raw = str(day_value or "").strip().upper()
        day_map = {
            "MONDAY": "MON",
            "TUESDAY": "TUE",
            "WEDNESDAY": "WED",
            "THURSDAY": "THU",
            "FRIDAY": "FRI",
            "SATURDAY": "SAT",
            "SUNDAY": "SUN",
            "MON": "MON",
            "TUE": "TUE",
            "WED": "WED",
            "THU": "THU",
            "FRI": "FRI",
            "SAT": "SAT",
            "SUN": "SUN",
        }
        day = day_map.get(day_raw)
        if not day:
            raise ValidationError("Invalid day value")
        return day

    @staticmethod
    def _normalize_time(value, label):
        raw = str(value or "").strip()
        if not raw:
            raise ValidationError(f"{label} is required")
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(raw, fmt).strftime("%H:%M:%S")
            except ValueError:
                continue
        raise ValidationError(f"Invalid {label} format")

    def get_timetable_by_id(self, timetable_id):
        try:
            timetable_id = int(timetable_id)
        except (TypeError, ValueError):
            raise ValidationError("Invalid timetable id")

        row = self.timetable_repo.get_by_id(timetable_id)
        if not row:
            raise RecordNotFoundError("Timetable entry not found")

        from datetime import date, datetime, time, timedelta

        def _to_json_value(value):
            if isinstance(value, timedelta):
                total_seconds = int(value.total_seconds())
                hours = (total_seconds // 3600) % 24
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            if isinstance(value, time):
                return value.strftime("%H:%M:%S")
            if isinstance(value, (datetime, date)):
                return value.isoformat()
            return value

        row = {k: _to_json_value(v) for k, v in row.items()}
        row['has_lectures'] = bool(self.timetable_repo.has_existing_lectures(timetable_id))
        return row

    def edit_timetable(self, timetable_id, data):
        try:
            timetable_id = int(timetable_id)
        except (TypeError, ValueError):
            raise ValidationError("Invalid timetable id")

        existing = self.timetable_repo.get_by_id(timetable_id)
        if not existing:
            raise RecordNotFoundError("Timetable entry not found")

        if self.timetable_repo.has_existing_lectures(timetable_id):
            raise ValidationError("Cannot edit timetable with existing lecture records")

        subject = str((data or {}).get('subject') or '').strip()
        department = str((data or {}).get('department') or '').strip()
        if not department:
            raise ValidationError("department is required")
        if not subject:
            raise ValidationError("subject is required")

        semester_raw = (data or {}).get('semester')
        if semester_raw is None or str(semester_raw).strip() == "":
            raise ValidationError("semester is required")
        try:
            semester = int(semester_raw)
        except (TypeError, ValueError):
            raise ValidationError("semester must be a valid integer")

        faculty_id_raw = (data or {}).get('faculty_id')
        if faculty_id_raw is None or str(faculty_id_raw).strip() == "":
            raise ValidationError("faculty_id is required")
        try:
            faculty_id = int(faculty_id_raw)
        except (TypeError, ValueError):
            raise ValidationError("faculty_id must be a valid integer")

        day = self._normalize_day((data or {}).get('day'))
        start_time = self._normalize_time((data or {}).get('start_time'), 'start_time')
        end_time = self._normalize_time((data or {}).get('end_time'), 'end_time')

        if start_time >= end_time:
            raise ValidationError("start_time must be earlier than end_time")

        if self.timetable_repo.has_time_conflict(
            faculty_id=faculty_id,
            day=day,
            start_time=start_time,
            end_time=end_time,
            exclude_id=timetable_id,
        ):
            raise ValidationError("Faculty has a time conflict for the selected slot")

        payload = {
            'subject': subject,
            'faculty_id': faculty_id,
            'day': day,
            'start_time': start_time,
            'end_time': end_time,
            'department': department,
            'semester': semester,
        }
        self.timetable_repo.update_timetable(timetable_id, payload)
        return True
