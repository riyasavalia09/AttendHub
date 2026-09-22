from exceptions.custom_exceptions import LinkedListEmptyError

class Node:
    """
    Generic Node class for LinkedList.
    Stores data payload and reference to next node.
    """
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    """
    Custom Singly LinkedList implementation.
    
    Used for:
    - Tracking active user sessions
    - Tracking ongoing lectures
    """
    
    def __init__(self):
        self._head = None
        self._size = 0
    
    def add(self, data):
        """Add new data to the end of the list"""
        new_node = Node(data)
        
        if self._head is None:
            self._head = new_node
        else:
            current = self._head
            while current.next:
                current = current.next
            current.next = new_node
        
        self._size += 1
    
    def remove(self, data):
        """Remove the first occurrence of data by value"""
        if self.is_empty():
            raise LinkedListEmptyError("Cannot remove from empty list")
        
        if self._head.data == data:
            self._head = self._head.next
            self._size -= 1
            return True
        
        current = self._head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                self._size -= 1
                return True
            current = current.next
        
        return False
    
    def find(self, data):
        """Find data in the list. Returns data if found, else None"""
        if self.is_empty():
            return None
            
        current = self._head
        while current:
            if current.data == data:
                return current.data
            current = current.next
        return None
    
    def is_empty(self):
        """Check if list is empty"""
        return self._head is None
    
    def size(self):
        """Get list size"""
        return self._size
    
    def to_list(self):
        """Convert to Python list (Utility/Debugging)"""
        result = []
        current = self._head
        while current:
            result.append(current.data)
            current = current.next
        return result
