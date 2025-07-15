"""
State management for user interactions.
"""

class StateManager:
    """Manages user states for different bot operations."""
    
    def __init__(self):
        self.user_states = {}
    
    def set_state(self, user_id: int, state: str) -> None:
        """Set a user's state."""
        self.user_states[user_id] = state
    
    def get_state(self, user_id: int) -> str:
        """Get a user's current state."""
        return self.user_states.get(user_id)
    
    def clear_state(self, user_id: int) -> bool:
        """Clear a user's state. Returns True if state existed, False otherwise."""
        if user_id in self.user_states:
            del self.user_states[user_id]
            return True
        return False
    
    def has_state(self, user_id: int) -> bool:
        """Check if user has an active state."""
        return user_id in self.user_states

# Global state manager instance
state_manager = StateManager()