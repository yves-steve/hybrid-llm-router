from __future__ import annotations

import requests


class LocalOllamaProvider:
    name = "local"

    def __init__(self, base_url: str, model: str, timeout: int = 120) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(
                "Failed to call local Ollama endpoint. Ensure Ollama is running and model is installed."
            ) from exc

        data = response.json()
        text = data.get("response", "")
        if not text:
            raise RuntimeError("Ollama returned an empty response.")

        return text
