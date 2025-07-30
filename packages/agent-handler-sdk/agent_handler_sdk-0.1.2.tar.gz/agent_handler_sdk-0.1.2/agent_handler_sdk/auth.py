# agent_handler_sdk/auth.py

class AuthContext:
    """
    Auth context for tool execution that provides secure access to secrets.
    
    This class provides an isolated container for secrets during tool execution.
    Each tool execution should receive its own instance.
    """
    def __init__(self, secrets=None):
        self._secrets = secrets or {}
    
    def get(self, key, default=None):
        """Get a secret value by key"""
        return self._secrets.get(key, default)