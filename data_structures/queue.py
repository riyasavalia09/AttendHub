from exceptions.custom_exceptions import QueueUnderflowError

class QueueNode:
    """Node for Queue implementation"""
    def __init__(self, data):
        self.data = data
        self.next = None


class Queue:
    """
    Custom FIFO Queue implementation.
    
    Used for:
    - Login request buffering
    - Attendance submission processing
    """
    
    def __init__(self):
        self.front = None
        self.rear = None
        self._size = 0
    
    def enqueue(self, data):
        """Add an item to the rear of the queue"""
        new_node = QueueNode(data)
        
        if self.rear is None:
            self.front = self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        
        self._size += 1
    
    def dequeue(self):
        """Remove and return the front item"""
        if self.is_empty():
            raise QueueUnderflowError("Cannot dequeue from empty queue")
        
        data = self.front.data
        self.front = self.front.next
        
        if self.front is None:
            self.rear = None
        
        self._size -= 1
        return data
    
    def peek(self):
        """View the front element without removing"""
        if self.is_empty():
            raise QueueUnderflowError("Cannot peek empty queue")
        return self.front.data
    
    def is_empty(self):
        """Check if queue is empty"""
        return self.front is None

    
    def size(self):
        """Get queue size"""
        return self._size
