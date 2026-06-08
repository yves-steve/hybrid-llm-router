from __future__ import annotations


class OpenAIPublicProvider:
    name = "openai"

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def validate(self) -> None:
        if not self.api_key:
            raise RuntimeError("OpenAI provider not configured. Missing: OPENAI_API_KEY")

    def generate(self, prompt: str) -> str:
        self.validate()
        # TODO: Implement OpenAI Responses API call.
        return (
            "[openai placeholder] OpenAI provider is configured. "
            "Implement API call in providers/openai_public.py"
        )
