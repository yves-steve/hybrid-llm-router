from __future__ import annotations


class BedrockProvider:
    name = "bedrock"

    def __init__(self, region: str, access_key_id: str, secret_access_key: str, model_id: str) -> None:
        self.region = region
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.model_id = model_id

    def validate(self) -> None:
        missing = []
        if not self.region:
            missing.append("AWS_REGION")
        if not self.access_key_id:
            missing.append("AWS_ACCESS_KEY_ID")
        if not self.secret_access_key:
            missing.append("AWS_SECRET_ACCESS_KEY")
        if missing:
            raise RuntimeError(
                f"Bedrock provider not configured. Missing: {', '.join(missing)}"
            )

    def generate(self, prompt: str) -> str:
        self.validate()
        # TODO: Implement boto3 Bedrock Runtime invoke call.
        return (
            "[bedrock placeholder] AWS credentials are present. "
            "Implement API call in providers/bedrock.py"
        )
