"""Player model for Mafia AI simulator.
Each player is backed by an Ollama LLM instance.
"""
from __future__ import annotations

from typing import List
import random

from context import ContextAggregator
from ollama_api import OllamaAPI


class Player:
    """Represents a single AI-controlled player."""

    def __init__(
        self,
        name: str,
        role: str,
        persona: str,
        api: OllamaAPI,
        context: ContextAggregator,
    ) -> None:
        self.name = name
        assert role in {"civilian", "mafia"}
        self.role = role
        self.persona = persona
        self.api = api
        self.chat_context = context
        self.alive: bool = True

    # ------------------------------------------------------------------
    # Messaging helpers
    # ------------------------------------------------------------------
    def tag(self) -> str:
        return f"{self.name.upper()} ({self.role.upper()})"

    def receive_message(self, message: str) -> None:
        """Add incoming message to local context."""
        self.chat_context.add(message)

    def make_decision(self, system_prompt: str) -> str:
        """Make a decision by querying Ollama.

        Args:
            system_prompt: High-level instruction prompt specifying what the
                player should decide / respond with.
        Returns:
            The LLM response text.
        """
        # Filter history based on role rules.
        if self.role == "civilian":
            visible_history = [m for m in self.chat_context.history() if m.startswith("[DAY")]
        else:  # mafia sees everything (day + night)
            visible_history = self.chat_context.history()
        context_messages = "\n".join(visible_history)
        prompt = (
            f"You are {self.name}, persona: {self.persona}. Role in the Mafia game: {self.role}.\n"
            f"Game context (recent messages):\n{context_messages}\n\n"
            f"Instruction: {system_prompt}"
        )
        try:
            response = self.api.send_request(prompt=prompt)
        except Exception as exc:
            # Fallback to random decision on failure
            print(f"[WARN] Ollama request failed for {self.name}: {exc}")
            response = ""  # empty = abstain
        return response.strip()

    # ------------------------------------------------------------------
    # Phase-specific helpers
    # ------------------------------------------------------------------
    def choose_night_target(self, possible_targets: List["Player"]) -> str:
        """Return the name of the chosen night victim (mafia only)."""
        if self.role != "mafia":
            return ""
        instruction = (
            "You are acting during the NIGHT phase with fellow mafia."
            " Choose exactly ONE civilian name from the list to eliminate tonight: "
            f"{', '.join(p.name for p in possible_targets)}."
            " Respond ONLY with the chosen name."
        )
        decision = self.make_decision(instruction)
        if not decision:
            decision = random.choice(possible_targets).name
        return decision

    def choose_vote(self, suspects: List["Player"]) -> str:
        """Choose a suspect to vote out during the day."""
        instruction = (
            "It is DAY. Choose ONE suspect to eliminate from the following alive players: "
            f"{', '.join(p.name for p in suspects)}."
            " Respond ONLY with the chosen name."
        )
        decision = self.make_decision(instruction)
        if decision not in [p.name for p in suspects]:
            decision = random.choice(suspects).name
        return decision
