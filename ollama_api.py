"""Minimal HTTP client for an Ollama server.
Assumes Ollama is running locally and exposes a /api/generate endpoint.
Adjust as required for your Ollama setup.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional
import requests


class OllamaAPI:
    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "mistral:latest",
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> None:
        self.host = host.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.top_p = top_p

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------
    def send_request(self, prompt: str, **extra_params: Any) -> str:
        """Send a prompt to Ollama and return the generated response text."""
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "stream": False,  # request single JSON response to simplify parsing
            **extra_params,
        }
        url = f"{self.host}/api/generate"
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()

        # Ollama may return either a single JSON object or multiple JSON lines.
        text = resp.text.strip()
        if "\n" in text:
            # streaming-style response concatenated; take last complete JSON line
            last_line = text.splitlines()[-1]
            data = json.loads(last_line)
        else:
            data = json.loads(text)
        return data.get("response", "")
