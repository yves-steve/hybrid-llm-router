import os
from pathlib import Path
from dataclasses import dataclass, field

from .hardware import load_profile


def env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class AppConfig:
    ollama_base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    local_model: str = field(default_factory=lambda: os.getenv("LOCAL_MODEL", "llama3.1:8b"))
    cloud_default_provider: str = field(default_factory=lambda: os.getenv("CLOUD_DEFAULT_PROVIDER", "openai"))
    sensitive_local_only: bool = field(default_factory=lambda: env_bool("SENSITIVE_LOCAL_ONLY", True))

    azure_openai_endpoint: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT", ""))
    azure_openai_api_key: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", ""))
    azure_openai_deployment: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_DEPLOYMENT", ""))
    azure_openai_api_version: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"))

    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

    aws_region: str = field(default_factory=lambda: os.getenv("AWS_REGION", ""))
    aws_access_key_id: str = field(default_factory=lambda: os.getenv("AWS_ACCESS_KEY_ID", ""))
    aws_secret_access_key: str = field(default_factory=lambda: os.getenv("AWS_SECRET_ACCESS_KEY", ""))
    bedrock_model_id: str = field(default_factory=lambda: os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-haiku-20241022-v1:0"))

    gcp_project_id: str = field(default_factory=lambda: os.getenv("GCP_PROJECT_ID", ""))
    gcp_location: str = field(default_factory=lambda: os.getenv("GCP_LOCATION", "us-central1"))
    vertex_model: str = field(default_factory=lambda: os.getenv("VERTEX_MODEL", "gemini-1.5-flash"))


def load_config() -> AppConfig:
    config = AppConfig()

    project_root = Path(__file__).resolve().parents[2]
    profile = load_profile(project_root)
    if not profile:
        return config

    # Environment variables always win. Profile acts as fallback defaults.
    if not os.getenv("LOCAL_MODEL") and profile.recommended_local_model:
        config.local_model = profile.recommended_local_model

    if not os.getenv("OPENAI_MODEL") and profile.recommended_cloud_default == "openai":
        config.openai_model = "gpt-4o-mini"

    if not os.getenv("CLOUD_DEFAULT_PROVIDER") and profile.recommended_cloud_default:
        config.cloud_default_provider = profile.recommended_cloud_default

    return config
