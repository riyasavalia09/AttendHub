from datetime import date
from exceptions.custom_exceptions import LectureAlreadyActiveError, ValidationError

class LectureService:
    """
    Service to handle lecture lifecycle management.
    """

    def __init__(self, timetable_repo, lecture_repo, queue, linked_list):
        """
        Constructor with Dependency Injection.
        """
        self.timetable_repo = timetable_repo
        self.lecture_repo = lecture_repo
        self.request_queue = queue        # Queue for start requests
        self.active_lectures = linked_list # LinkedList for tracking ongoing lectures

    def start_lecture(self, faculty_id, timetable_id):
        """
        Starts a new lecture session.
        Enqueues request, checks conflicts, and creates record.
        """
        # 1. Enqueue Request
        request_data = {
            'faculty_id': faculty_id, 
            'timetable_id': timetable_id, 
            'date': date.today()
        }
        self.request_queue.enqueue(request_data)
        
        # 2. Process Request (Simulated immediate processing)
        req = self.request_queue.dequeue()
        
        # 3. Validation: Check if faculty already has an active lecture in our LinkedList tracking
        # We traverse our active_lectures list to see if this faculty is busy
        current = self.active_lectures._head
        while current:
            if current.data.get('faculty_id') == req['faculty_id']:
                raise LectureAlreadyActiveError("Faculty already has an ongoing lecture session")
            current = current.next

        # 4. Check DB for duplicates for this timetable slot today
        existing_any = self.lecture_repo.find_by_timetable_and_date(req['timetable_id'], req['date'])
        if existing_any:
            if existing_any.get('status') == 'ONGOING':
                raise LectureAlreadyActiveError("This lecture slot is already active today")
            # ENDED (or any other status) exists for today -> do not allow creating another due to unique key
            raise ValidationError("This lecture has already been completed for today")

        # 5. Create Lecture in DB
        lecture_id = self.lecture_repo.create_lecture(req['timetable_id'], req['date'])

        # 6. Add to Active LinkedList
        lecture_node_data = {
            'lecture_id': lecture_id,
            'timetable_id': req['timetable_id'],
            'faculty_id': req['faculty_id'],
            'started_at': req['date']
        }
        self.active_lectures.add(lecture_node_data)

        return lecture_id

    def end_lecture(self, lecture_id):
        """
        Ends an ongoing lecture.
        Updates DB and removes from Active LinkedList.
        """
        # 1. Update DB
        success = self.lecture_repo.end_lecture(lecture_id)
        if not success:
            raise ValidationError("Lecture not found or already ended")

        # 2. Remove from LinkedList
        # We need to find the node data to remove it
        node_to_remove = None
        current = self.active_lectures._head
        while current:
            if current.data.get('lecture_id') == lecture_id:
                node_to_remove = current.data
                break
            current = current.next

        if node_to_remove:
            self.active_lectures.remove(node_to_remove)

        return True

    def get_active_lectures(self):
        """
        Returns list of all active lectures from memory.
        """
        lectures = []
        current = self.active_lectures._head
        while current:
            lectures.append(current.data)
            current = current.next
        return lectures

    def get_todays_lectures(self, faculty_id):
        """
        Gets the schedule for the faculty member for today.
        """
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

        all_slots = self.timetable_repo.find_by_faculty(faculty_id)
        
        # Filter for today (assuming 'Monday', 'Tuesday' in DB)
        today_str = date.today().strftime('%A')
        # Map to enum if needed, database seems to have 'Monday' etc based on repo code I saw
        # Actually repo has ORDER BY FIELD(day, 'Monday', ...) so it expects full names?
        # Let's check TimetableRepository again.
        
        # Repo insert used 'MON', 'TUE' in one place, but 'Monday' in find_by_faculty ORDER BY?
        # Let's double check repo code.
        
        todays = [
            slot
            for slot in (all_slots or [])
            if slot.get('day')
            and (
                slot['day'].upper() == today_str[:3].upper()
                or slot['day'].upper() == today_str.upper()
            )
        ]

        for slot in todays:
            if isinstance(slot, dict):
                slot['start_time'] = to_time_str(slot.get('start_time'))
                slot['end_time'] = to_time_str(slot.get('end_time'))

        return todays

    def get_weekly_schedule(self, faculty_id):
        """Gets the weekly timetable entries for the faculty member."""
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

        slots = self.timetable_repo.find_by_faculty(faculty_id) or []
        for slot in slots:
            if isinstance(slot, dict):
                slot['start_time'] = to_time_str(slot.get('start_time'))
                slot['end_time'] = to_time_str(slot.get('end_time'))
        return slots
