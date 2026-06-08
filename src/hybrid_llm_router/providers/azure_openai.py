from __future__ import annotations


class AzureOpenAIProvider:
    name = "azure"

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment: str,
        api_version: str,
    ) -> None:
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment = deployment
        self.api_version = api_version

    def validate(self) -> None:
        missing = []
        if not self.endpoint:
            missing.append("AZURE_OPENAI_ENDPOINT")
        if not self.api_key:
            missing.append("AZURE_OPENAI_API_KEY")
        if not self.deployment:
            missing.append("AZURE_OPENAI_DEPLOYMENT")

        if missing:
            raise RuntimeError(
                f"Azure provider not configured. Missing: {', '.join(missing)}"
            )

    def generate(self, prompt: str) -> str:
        self.validate()
        # TODO: Implement Azure OpenAI chat completion call.
        # Suggested endpoint format:
        # {endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}
        return (
            "[azure placeholder] Azure provider is configured. "
            "Implement API call in providers/azure_openai.py"
        )
