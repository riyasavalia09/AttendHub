from datetime import datetime
from exceptions.custom_exceptions import PermissionDeniedError

class AuthorizationService:
    """
    Service to handle centralized role-based access control (RBAC).
    """

    def __init__(self, role_permission_map, audit_stack):
        """
        Constructor with Dependency Injection.
        
        :param role_permission_map: Dict[str, Tuple[str]] - Immutable mapping of roles to permissions
        :param audit_stack: Stack - For logging authorization attempts
        """
        if not isinstance(role_permission_map, dict):
            raise ValueError("Role permission map must be a dictionary")
            
        self._role_map = role_permission_map
        self.audit_stack = audit_stack
        
        # Optimize lookup by converting tuples to sets (internal optimization)
        # Structure: {'admin': {'perm1', 'perm2'}, ...}
        self._fast_lookup = {
            role: set(perms) for role, perms in role_permission_map.items()
        }

    def authorize(self, role, permission):
        """
        Checks if a role has the required permission.
        Logs the attempt and raises PermissionDeniedError on failure.
        """
        has_permission = False
        
        # Check permission using Set (O(1))
        if role in self._fast_lookup:
            if permission in self._fast_lookup[role]:
                has_permission = True
        
        # Audit Log (Stack)
        audit_entry = {
            'event': 'AUTHZ_CHECK',
            'role': role,
            'permission': permission,
            'result': 'GRANTED' if has_permission else 'DENIED',
            'timestamp': datetime.now()
        }
        self.audit_stack.push(audit_entry)
        
        if not has_permission:
            raise PermissionDeniedError(role, permission)
            
        return True
