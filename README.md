# AI_mafia Codebase Documentation

## Overview

**AI_mafia** is a Python-based simulator of the classic Mafia party game, where all players are controlled by Large Language Models (LLMs) using the Ollama API. Each AI player has a unique persona, and the game logic coordinates their interactions, decisions, and game state.

---

## Modules and Their Functionality

### 1. `game.py`
**Purpose:**  
Main game loop and orchestration for the Mafia AI simulator.

**Key Components:**
- **Configuration Loading:**  
  `load_config()` loads game settings from `config.json`.
- **Player Initialization:**  
  `init_players(cfg)` creates AI player objects from config, each with persona, role, and context.
- **Logging:**  
  `log(message)` writes logs to file and prints to console for transparency.
- **Game Phases:**  
  - `night_phase(players, state, mafia_names)`: Mafia selects a victim to eliminate.
  - `day_phase(players, state, mafia_names)`: Players discuss, vote, and eliminate a suspect.
- **Game Loop:**  
  `main()` manages the game cycle: alternating night and day phases, checking win conditions, and logging results.
- **Translation Stub:**  
  Contains a disabled translation function for Russian.

---

### 2. `player.py`
**Purpose:**  
Defines the AI player model and decision-making logic.

**Key Components:**
- **Player Class:**  
  - `__init__(...)`: Sets up player attributes (name, role, persona, API, context).
  - `tag()`: Returns a readable tag for the player (e.g., `ALICE (MAFIA)`).
  - `receive_message(message)`: Adds a message to the player’s context history.
  - `make_decision(system_prompt)`:  
    - Crafts a prompt with player persona, role, and message context.
    - Queries the Ollama LLM for a decision or fallback to random/empty on failure.
    - Civilians only see day messages; mafia sees all.
  - `choose_night_target(possible_targets)`: Mafia picks a night victim.
  - `choose_vote(suspects)`: Player votes for a suspect in the day phase.

---

### 3. `state.py`
**Purpose:**  
Tracks and mutates the overall game state.

**Key Components:**
- **GameState Class:**  
  - `__init__(players)`: Initializes player statuses, phase, logs for votes/kills.
  - `living_players()`: Returns names of all alive players.
  - `living_civilians(mafia)`: Returns alive civilians.
  - `is_alive(name)`: Checks if a player is alive.
  - **Mutations:**
    - `kill(name, night)`: Marks player as dead and logs the event.
    - `add_vote_record(day, votes)`: Logs votes for each day.
  - **Win Conditions:**
    - `check_win(mafia_names)`: Returns 'mafia', 'civilians', or None based on the game state.

---

### 4. `context.py`
**Purpose:**  
Manages the conversational context/history for players.

**Key Components:**
- **ContextAggregator Class:**  
  Maintains a bounded history of recent messages (using a deque) for efficient prompt generation and memory management.

---

### 5. `ollama_api.py`
**Purpose:**  
Handles communication with the Ollama LLM server.

**Key Components:**
- **OllamaAPI Class:**  
  - `__init__(host, model, temperature, top_p)`: Configures API parameters.
  - `send_request(prompt)`: Sends a prompt to the Ollama server and gets a response.
  - Minimal HTTP client for `/api/generate` endpoint, assumes local Ollama setup.

---

## Game Flow Summary

1. **Setup:**  
   Loads configuration and initializes AI players.
2. **Night Phase:**  
   Mafia chooses a victim.
3. **Day Phase:**  
   All players discuss, then vote on a suspect to eliminate.
4. **State Updates:**  
   Eliminations are logged, and game state is mutated.
5. **Win Check:**  
   After each phase, checks if mafia or civilians have won.
6. **End:**  
   Game ends and the result is logged.

---

## Customization & Extensibility

- **Personas & Roles:** Easily extendable via `config.json` for more players or custom LLM personalities.
- **LLM Model:** Changeable through Ollama configuration.
- **Translation:** Stub exists for localization.

---

## Usage

Run the game with:
```bash
python game.py
```

Ensure your Ollama server is running and configured as required.

---
