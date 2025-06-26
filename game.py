"""Main game loop for the Mafia AI simulator."""
from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import Dict, List

from context import ContextAggregator
from player import Player
from ollama_api import OllamaAPI
from state import GameState

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "config.json"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_config() -> Dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as fp:
        return json.load(fp)


def init_players(cfg: Dict) -> List[Player]:
    api = OllamaAPI(**cfg.get("ollama", {}))
    max_ctx = cfg.get("context", {}).get("max_messages", 20)
    players: List[Player] = []
    shared_context = ContextAggregator(max_ctx)

    for p_cfg in cfg["players"]:
        players.append(
            Player(
                name=p_cfg["name"],
                role=p_cfg["role"],
                persona=p_cfg["persona"],
                api=api,
                context=shared_context,
            )
        )
    return players


# Translation disabled as per user request -> str:
    """Translate *text* to Russian using the same LLM. Fallback to original text."""
    if api is None:
        return text
    try:
        ru = api.send_request(
            prompt="Translate the following text to Russian while keeping meaning and player names intact:\n" + text,
        )
        return ru.strip() or text
    except Exception:
        return text


def log(message: str) -> None:
    """Append *message* to log file."""
    logfile = LOG_DIR / "game.log"
    with open(logfile, "a", encoding="utf-8") as fp:
        fp.write(message + "\n")

    # always print original language
        
    
        print(message)


# ---------------------------------------------------------------------------
# Game Phases
# ---------------------------------------------------------------------------

def night_phase(players: List[Player], state: GameState, mafia_names: List[str]):
    """Mafia choose a victim."""
    state.phase = "night"
    state.night += 1
    living = [p for p in players if state.is_alive(p.name)]
    mafia_players = [p for p in living if p.name in mafia_names]
    civilians = [p for p in living if p.name not in mafia_names]

    if not civilians:
        return  # nothing to kill

    # Each mafia proposes a target, majority vote
    votes: Dict[str, int] = {}
    for mafia in mafia_players:
        target_name = mafia.choose_night_target(civilians)
        votes[target_name] = votes.get(target_name, 0) + 1
    victim = max(votes.items(), key=lambda kv: kv[1])[0]
    state.kill(victim, state.night)

    msg = f"[NIGHT {state.night}] Mafia killed {victim}."
    for p in players:
        p.receive_message(msg)
    log(msg)


def day_phase(players: List[Player], state: GameState, mafia_names: List[str]):
    state.phase = "day"
    state.day += 1

    living_players = [p for p in players if state.is_alive(p.name)]

    # Discussion round (simple prompt for each to generate a statement)
    for pl in living_players:
        prompt = "Share your thoughts about who might be mafia. Keep it short (1-2 sentences)."
        statement = pl.make_decision(prompt)
        msg = f"[DAY {state.day}] [{pl.tag()} -> ALL] {statement}"
        for p in players:
            p.receive_message(msg)
        log(msg)

    # Voting round
    suspects = living_players
    votes: Dict[str, str] = {}
    for pl in living_players:
        target = pl.choose_vote(suspects)
        votes[pl.name] = target
        log(f"[DAY {state.day}] {pl.name} voted for {target}")

    # Tally votes
    tally: Dict[str, int] = {}
    for tgt in votes.values():
        tally[tgt] = tally.get(tgt, 0) + 1
    eliminated = max(tally.items(), key=lambda kv: kv[1])[0]
    state.kill(eliminated, night=0)  # night=0 indicates day elimination
    state.add_vote_record(state.day, votes)

    msg = f"[DAY {state.day}] {eliminated} was eliminated by vote."
    for p in players:
        p.receive_message(msg)
    log(msg)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    cfg = load_config()
    players = init_players(cfg)
    mafia_names = [p.name for p in players if p.role == "mafia"]

    state = GameState([p.name for p in players])

    # Game loop
    while True:
        # Night phase
        night_phase(players, state, mafia_names)
        winner = state.check_win(mafia_names)
        if winner:
            break
        # Day phase
        day_phase(players, state, mafia_names)
        winner = state.check_win(mafia_names)
        if winner:
            break

    # Game finished – print translated result
    log(f"Game over! Winner: {winner.upper()}")


if __name__ == "__main__":
    main()
