from __future__ import annotations


class VertexProvider:
    name = "vertex"

    def __init__(self, project_id: str, location: str, model: str) -> None:
        self.project_id = project_id
        self.location = location
        self.model = model

    def validate(self) -> None:
        if not self.project_id:
            raise RuntimeError("Vertex provider not configured. Missing: GCP_PROJECT_ID")

    def generate(self, prompt: str) -> str:
        self.validate()
        # TODO: Implement Vertex AI text generation call.
        return (
            "[vertex placeholder] GCP settings are present. "
            "Implement API call in providers/vertex.py"
        )
