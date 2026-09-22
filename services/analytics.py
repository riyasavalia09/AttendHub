from exceptions.custom_exceptions import ValidationError


class AnalyticsService:
    """Attendance analytics service.

    Rules:
    - Repository does aggregation (SQL GROUP BY / SUM/COUNT)
    - Service does business calculations (percentages, risk levels)
    """

    def __init__(self, attendance_repo, student_repo=None):
        self.attendance_repo = attendance_repo
        self.student_repo = student_repo

    @staticmethod
    def _risk_level(overall_percentage: float) -> str:
        if overall_percentage >= 85:
            return 'SAFE'
        if overall_percentage >= 75:
            return 'WARNING'
        return 'CRITICAL'

    @staticmethod
    def _pct(present: int, total: int) -> int:
        if not total:
            return 0
        return int(round((present / total) * 100))

    @staticmethod
    def _validate_date_range(from_date: str = None, to_date: str = None) -> None:
        """Validate YYYY-MM-DD date range (inclusive)."""
        parsed_from = None
        parsed_to = None
        if from_date:
            try:
                from datetime import date as _date
                parsed_from = _date.fromisoformat(from_date)
            except ValueError:
                raise ValidationError('Invalid from_date. Expected YYYY-MM-DD')
        if to_date:
            try:
                from datetime import date as _date
                parsed_to = _date.fromisoformat(to_date)
            except ValueError:
                raise ValidationError('Invalid to_date. Expected YYYY-MM-DD')
        if parsed_from and parsed_to and parsed_from > parsed_to:
            raise ValidationError('Invalid date range. from_date must be <= to_date')

    def admin_student_attendance_summary(
        self,
        university_id: int,
        student_id: int,
        subject: str = None,
        from_date: str = None,
        to_date: str = None,
    ) -> dict:
        if not university_id or not student_id:
            raise ValidationError('university_id and student_id are required')

        subject_norm = (subject or '').strip() or None

        self._validate_date_range(from_date=from_date, to_date=to_date)

        # Ensure student belongs to this university (no cross-tenant access)
        if self.student_repo:
            student = self.student_repo.find_by_id(int(student_id))
            if not student or int(student.get('university_id') or 0) != int(university_id):
                raise ValidationError('Invalid student_id')

        rows = self.attendance_repo.get_subject_counts_for_student_in_university_filtered(
            university_id=int(university_id),
            student_id=int(student_id),
            subject=subject_norm,
            from_date=from_date,
            to_date=to_date,
        )
        totals = self.attendance_repo.get_overall_counts_for_student_in_university_filtered(
            university_id=int(university_id),
            student_id=int(student_id),
            subject=subject_norm,
            from_date=from_date,
            to_date=to_date,
        )

        subjects = []
        present_counts = []
        absent_counts = []
        percentages = []

        for r in rows or []:
            if not isinstance(r, dict):
                continue
            subject = (r.get('subject') or '').strip()
            if not subject:
                continue
            present = int(r.get('present_count') or 0)
            absent = int(r.get('absent_count') or 0)
            total = int(r.get('total_count') or 0)

            subjects.append(subject)
            present_counts.append(present)
            absent_counts.append(absent)
            percentages.append(self._pct(present, total))

        overall_present = int((totals or {}).get('present_count') or 0)
        overall_total = int((totals or {}).get('total_count') or 0)
        overall_percentage = self._pct(overall_present, overall_total)

        return {
            'subjects': subjects,
            'present_counts': present_counts,
            'absent_counts': absent_counts,
            'percentages': percentages,
            'overall_percentage': overall_percentage,
            'risk_level': self._risk_level(overall_percentage),
        }

    def admin_lowest_attendance_students(self, university_id: int, limit: int = 5) -> dict:
        if not university_id:
            raise ValidationError('university_id is required')

        limit_int = int(limit or 5)
        if limit_int <= 0 or limit_int > 50:
            limit_int = 5

        rows = self.attendance_repo.get_lowest_attendance_students(
            university_id=int(university_id),
            limit=limit_int,
        )

        students = []
        percentages = []
        for r in rows or []:
            if not isinstance(r, dict):
                continue
            name = (r.get('student_name') or '').strip() or 'Unknown'
            present = int(r.get('present_count') or 0)
            total = int(r.get('total_count') or 0)
            students.append(name)
            percentages.append(self._pct(present, total))

        return {
            'students': students,
            'percentages': percentages,
        }

    def admin_lowest_attendance_students_filtered(
        self,
        university_id: int,
        limit: int = 5,
        from_date: str = None,
        to_date: str = None,
    ) -> dict:
        if not university_id:
            raise ValidationError('university_id is required')

        self._validate_date_range(from_date=from_date, to_date=to_date)

        limit_int = int(limit or 5)
        if limit_int <= 0 or limit_int > 50:
            limit_int = 5

        rows = self.attendance_repo.get_lowest_attendance_students_filtered(
            university_id=int(university_id),
            limit=limit_int,
            from_date=from_date,
            to_date=to_date,
        )

        students = []
        percentages = []
        for r in rows or []:
            if not isinstance(r, dict):
                continue
            name = (r.get('student_name') or '').strip() or 'Unknown'
            present = int(r.get('present_count') or 0)
            total = int(r.get('total_count') or 0)
            students.append(name)
            percentages.append(self._pct(present, total))

        return {
            'students': students,
            'percentages': percentages,
        }

    def admin_department_averages(
        self,
        university_id: int,
        from_date: str = None,
        to_date: str = None,
    ) -> dict:
        if not university_id:
            raise ValidationError('university_id is required')

        self._validate_date_range(from_date=from_date, to_date=to_date)

        rows = self.attendance_repo.get_department_attendance_counts_filtered(
            university_id=int(university_id),
            from_date=from_date,
            to_date=to_date,
        )

        departments = []
        percentages = []
        for r in rows or []:
            if not isinstance(r, dict):
                continue
            dept = (r.get('department') or '').strip() or 'Unknown'
            present = int(r.get('present_count') or 0)
            total = int(r.get('total_count') or 0)
            departments.append(dept)
            percentages.append(self._pct(present, total))

        return {
            'departments': departments,
            'percentages': percentages,
        }

    def admin_university_trend(
        self,
        university_id: int,
        from_date: str = None,
        to_date: str = None,
    ) -> dict:
        if not university_id:
            raise ValidationError('university_id is required')

        self._validate_date_range(from_date=from_date, to_date=to_date)

        rows = self.attendance_repo.get_university_trend_by_date_filtered(
            university_id=int(university_id),
            from_date=from_date,
            to_date=to_date,
        )

        dates = []
        percentages = []
        for r in rows or []:
            if not isinstance(r, dict):
                continue
            dates.append(r.get('lecture_date'))
            present = int(r.get('present_count') or 0)
            total = int(r.get('total_count') or 0)
            percentages.append(self._pct(present, total))

        avg = int(round(sum(percentages) / len(percentages))) if percentages else 0
        return {
            'dates': dates,
            'attendance_percentages': percentages,
            'average_percentage': avg,
            'risk_level': self._risk_level(avg),
        }

    def faculty_lecture_stats(self, faculty_id: int, lecture_id: int) -> dict:
        if not faculty_id or not lecture_id:
            raise ValidationError('faculty_id and lecture_id are required')

        counts = self.attendance_repo.get_lecture_attendance_distribution(
            faculty_id=int(faculty_id),
            lecture_id=int(lecture_id),
        )
        total = int((counts or {}).get('total_students') or 0)
        present = int((counts or {}).get('present') or 0)
        absent = int((counts or {}).get('absent') or 0)

        return {
            'total_students': total,
            'present': present,
            'absent': absent,
            'percentage': self._pct(present, total),
        }

    def faculty_lecture_trend(self, faculty_id: int, subject: str, from_date: str = None, to_date: str = None) -> dict:
        if not faculty_id:
            raise ValidationError('faculty_id is required')
        subject_norm = (subject or '').strip()
        if not subject_norm:
            raise ValidationError('subject is required')

        self._validate_date_range(from_date=from_date, to_date=to_date)

        rows = self.attendance_repo.get_lecture_trend_by_subject_filtered(
            faculty_id=int(faculty_id),
            subject=subject_norm,
            from_date=from_date,
            to_date=to_date,
        )

        dates = []
        percentages = []
        for r in rows or []:
            if not isinstance(r, dict):
                continue
            dates.append(r.get('lecture_date'))
            present = int(r.get('present_count') or 0)
            total = int(r.get('total_count') or 0)
            percentages.append(self._pct(present, total))

        avg = int(round(sum(percentages) / len(percentages))) if percentages else 0

        return {
            'dates': dates,
            'attendance_percentages': percentages,
            'average_percentage': avg,
            'risk_level': self._risk_level(avg),
        }

    def faculty_overall_trend(self, faculty_id: int, from_date: str = None, to_date: str = None) -> dict:
        if not faculty_id:
            raise ValidationError('faculty_id is required')

        self._validate_date_range(from_date=from_date, to_date=to_date)

        rows = self.attendance_repo.get_faculty_overall_trend_by_date_filtered(
            faculty_id=int(faculty_id),
            from_date=from_date,
            to_date=to_date,
        )

        dates = []
        percentages = []
        for r in rows or []:
            if not isinstance(r, dict):
                continue
            dates.append(r.get('lecture_date'))
            present = int(r.get('present_count') or 0)
            total = int(r.get('total_count') or 0)
            percentages.append(self._pct(present, total))

        avg = int(round(sum(percentages) / len(percentages))) if percentages else 0
        return {
            'dates': dates,
            'attendance_percentages': percentages,
            'average_percentage': avg,
            'risk_level': self._risk_level(avg),
        }

    def student_attendance_chart(self, student_id: int, subject: str = None, from_date: str = None, to_date: str = None) -> dict:
        if not student_id:
            raise ValidationError('student_id is required')

        subject_norm = (subject or '').strip() or None

        self._validate_date_range(from_date=from_date, to_date=to_date)

        rows = self.attendance_repo.get_subject_counts_for_student_filtered(
            student_id=int(student_id),
            subject=subject_norm,
            from_date=from_date,
            to_date=to_date,
        )
        totals = self.attendance_repo.get_overall_counts_for_student_filtered(
            student_id=int(student_id),
            subject=subject_norm,
            from_date=from_date,
            to_date=to_date,
        )

        subjects = []
        percentages = []
        for r in rows or []:
            if not isinstance(r, dict):
                continue
            subject = (r.get('subject') or '').strip()
            if not subject:
                continue
            present = int(r.get('present_count') or 0)
            total = int(r.get('total_count') or 0)
            subjects.append(subject)
            percentages.append(self._pct(present, total))

        overall_present = int((totals or {}).get('present_count') or 0)
        overall_total = int((totals or {}).get('total_count') or 0)
        overall = self._pct(overall_present, overall_total)

        return {
            'subjects': subjects,
            'percentages': percentages,
            'overall': overall,
            'risk_level': self._risk_level(overall),
        }

    def student_recent_trend(
        self,
        student_id: int,
        limit: int = 5,
        subject: str = None,
        from_date: str = None,
        to_date: str = None,
    ) -> dict:
        if not student_id:
            raise ValidationError('student_id is required')

        subject_norm = (subject or '').strip() or None

        self._validate_date_range(from_date=from_date, to_date=to_date)

        limit_int = int(limit or 5)
        if limit_int <= 0 or limit_int > 50:
            limit_int = 5

        rows = self.attendance_repo.get_recent_lecture_attendance_for_student(
            student_id=int(student_id),
            limit=limit_int,
            subject=subject_norm,
            from_date=from_date,
            to_date=to_date,
        )

        # Repo returns DESC; convert to ASC for chart readability.
        rows = list(rows or [])
        rows.reverse()

        labels = []
        values = []
        for r in rows:
            if not isinstance(r, dict):
                continue
            labels.append(r.get('lecture_date'))
            status = (r.get('status') or '').strip().upper()
            values.append(100 if status == 'PRESENT' else 0)

        avg = int(round(sum(values) / len(values))) if values else 0
        return {
            'dates': labels,
            'attendance_percentages': values,
            'average_percentage': avg,
            'risk_level': self._risk_level(avg),
        }
