from exceptions.custom_exceptions import StackUnderflowError

class StackNode:
    """Node for Stack implementation"""
    def __init__(self, data):
        self.data = data
        self.next = None


class Stack:
    """Custom Stack implementation for tracking authentication attempts"""
    
    def __init__(self):
        self.top = None
        self._size = 0
    
    def push(self, data):
        """Push an item to the stack"""
        new_node = StackNode(data)
        new_node.next = self.top
        self.top = new_node
        self._size += 1
    
    def pop(self):
        """Pop the top item"""
        if self.is_empty():
            raise StackUnderflowError("Cannot pop from empty stack")
        
        data = self.top.data
        self.top = self.top.next
        self._size -= 1
        return data
    
    def peek(self):
        """View the top element without removing"""
        if self.is_empty():
            raise StackUnderflowError("Cannot peek empty stack")
        return self.top.data
    
    def is_empty(self):
        """Check if stack is empty"""
        return self.top is None
    
    def size(self):
        """Get stack size"""
        return self._size
    
    def to_list(self):
        """Convert stack to list for viewing"""
        result = []
        current = self.top
        while current:
            result.append(current.data)
            current = current.next
        return result
