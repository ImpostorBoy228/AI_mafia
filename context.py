"""Context management for Mafia AI simulator.
Keeps track of recent messages and trims history for efficiency.
"""
from __future__ import annotations

from collections import deque
from typing import Deque, List


class ContextAggregator:
    """Stores a sliding window of recent messages.

    Messages are stored as strings already tagged (e.g. "[DAY] [ALICE (CIVILIAN) -> ALL] Hello").
    The window keeps the newest *max_messages* items.
    """

    def __init__(self, max_messages: int = 20):
        self.max_messages: int = max_messages
        self._messages: Deque[str] = deque(maxlen=max_messages)

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------
    def add(self, message: str) -> None:
        """Add a fully-formatted message to the context."""
        # Normalise whitespace and store
        self._messages.append(message.strip())

    def history(self) -> List[str]:
        """Return a list with the current context in chronological order."""
        return list(self._messages)

    def clear_day_cycle(self) -> None:
        """Clear messages at the transition from night to next day (optional)."""
        self._messages.clear()
