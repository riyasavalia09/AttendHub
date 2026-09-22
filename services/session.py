import uuid
from datetime import datetime
from exceptions.custom_exceptions import SessionNotFoundError, DuplicateEntryError

class SessionService:
    """
    Service to manage lifecycle of user sessions using Data Structures.
    """

    def __init__(self, linked_list, session_set):
        """
        Constructor with Dependency Injection.
        :param linked_list: LinkedList instance for storing session details
        :param session_set: Set instance for fast O(1) session ID lookups
        """
        self.active_sessions = linked_list
        self.active_session_ids = session_set

    def create_session(self, user_id, role, university_id):
        """
        Creates a new session for a user.
        Raises DuplicateEntryError if collision occurs (rare).
        """
        session_id = str(uuid.uuid4())
        
        # Although UUID collision is virtually impossible, we enforce the rule
        if session_id in self.active_session_ids:
            raise DuplicateEntryError("Session collision detected")

        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'role': role,
            'university_id': university_id,
            'created_at': datetime.now()
        }

        # Add to Data Structures
        self.active_sessions.add(session_data)
        self.active_session_ids.add(session_id)
        
        return session_data

    def remove_session(self, session_id):
        """
        Removes a session (Logout).
        Raises SessionNotFoundError if session doesn't exist.
        """
        if session_id not in self.active_session_ids:
            raise SessionNotFoundError()

        # Remove from Set (O(1))
        self.active_session_ids.remove(session_id)

        # Remove from LinkedList (O(n))
        # We need to find the data object that matches this session_id to remove it
        # Since LinkedList.remove() typically removes by value reference, 
        # we first need to find the exact object or rely on custom remove logic.
        
        # Assuming our LinkedList.remove works by object equality or we iterate.
        # Let's use the find capability or iteration.
        
        node_to_remove = None
        current = self.active_sessions._head
        while current:
            if current.data.get('session_id') == session_id:
                node_to_remove = current.data
                break
            current = current.next
            
        if node_to_remove:
            self.active_sessions.remove(node_to_remove)
        else:
            # Consistency check failed (Set had it, List didn't)
            pass 

        return True

    def get_active_sessions(self):
        """
        Returns a list of all active session data.
        Traverses the LinkedList locally without exposing the node structure.
        """
        sessions = []
        current = self.active_sessions._head
        while current:
            sessions.append(current.data)
            current = current.next
        return sessions

    def is_session_active(self, session_id):
        """
        Checks if a session is currently active.
        Uses Set for O(1) lookup.
        """
        return session_id in self.active_session_ids
