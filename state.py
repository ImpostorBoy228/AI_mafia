"""Game state tracking for Mafia AI simulator."""
from __future__ import annotations

from typing import Dict, List, Sequence
import random


class GameState:
    """Holds the mutable state of a Mafia game."""

    def __init__(self, players: Sequence[str]):
        self.day: int = 0
        self.night: int = 0
        self.phase: str = "init"  # one of: init, night, day, finished

        # player_name -> alive bool
        self.alive: Dict[str, bool] = {p: True for p in players}

        self.vote_log: List[Dict] = []  # each: {"day": n, "votes": {name: target}}
        self.kill_log: List[Dict] = []  # each: {"night": n, "victim": name}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def living_players(self) -> List[str]:
        return [p for p, alive in self.alive.items() if alive]

    def living_civilians(self, mafia: Sequence[str]) -> List[str]:
        return [p for p in self.living_players() if p not in mafia]

    def is_alive(self, name: str) -> bool:
        return self.alive.get(name, False)

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------
    def kill(self, name: str, night: int) -> None:
        if self.alive.get(name):
            self.alive[name] = False
            self.kill_log.append({"night": night, "victim": name})

    def add_vote_record(self, day: int, votes: Dict[str, str]):
        self.vote_log.append({"day": day, "votes": votes})

    # ------------------------------------------------------------------
    # Win conditions
    # ------------------------------------------------------------------
    def check_win(self, mafia_names: Sequence[str]) -> str | None:
        """Return winner: 'mafia', 'civilians', or None if game continues."""
        living = self.living_players()
        mafia_alive = [m for m in mafia_names if self.is_alive(m)]
        civilian_alive = [p for p in living if p not in mafia_names]

        if not mafia_alive:
            return "civilians"
        if len(mafia_alive) >= len(civilian_alive):
            return "mafia"
        return None
