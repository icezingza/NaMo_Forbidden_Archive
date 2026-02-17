class ForbiddenBehaviorCore:
    """
    Manages forbidden states and behavioral locks.
    """
    def __init__(self):
        self.is_locked = False
        self.punishment_level = 0

    def check_constraints(self, user_input: str) -> bool:
        """
        Checks if the input violates any core constraints (if any remain).
        """
        return True

    def escalate_punishment(self):
        self.punishment_level += 1