"""
Monkey patch for OpenAI client to fix the AttributeError in SyncHttpxClientWrapper.__del__
"""

from enum import Enum


class ClientState(Enum):
    """Mock ClientState enum to match what OpenAI expects"""

    OPENED = "opened"
    CLOSED = "closed"


def patch_openai_client():
    """
    Apply monkey patch to fix 'SyncHttpxClientWrapper' has no attribute '_state' error.
    This patch adds the missing _state attribute to the SyncHttpxClientWrapper class.
    """
    try:
        from openai._base_client import SyncHttpxClientWrapper

        # Only patch if it doesn't already have the attribute
        if not hasattr(SyncHttpxClientWrapper, "_state"):
            # Add the _state attribute to the class
            SyncHttpxClientWrapper._state = ClientState.OPENED

            # Save the original __del__ method
            original_del = SyncHttpxClientWrapper.__del__

            # Define a new __del__ method that safely handles the attribute
            def safe_del(self):
                if not hasattr(self, "_state"):
                    self._state = ClientState.OPENED
                try:
                    original_del(self)
                except AttributeError:
                    pass  # Ignore attribute errors during garbage collection

            # Replace the original __del__ method
            SyncHttpxClientWrapper.__del__ = safe_del

            return True
    except (ImportError, AttributeError):
        pass

    return False
