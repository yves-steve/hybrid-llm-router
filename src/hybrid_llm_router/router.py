from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from .config import AppConfig
from .providers.azure_openai import AzureOpenAIProvider
from .providers.bedrock import BedrockProvider
from .providers.local_ollama import LocalOllamaProvider
from .providers.openai_public import OpenAIPublicProvider
from .providers.vertex import VertexProvider


class Provider(Protocol):
    name: str

    def generate(self, prompt: str) -> str:
        ...


@dataclass
class RoutingDecision:
    provider: str
    reason: str


class HybridRouter:
    def __init__(self, config: AppConfig) -> None:
        self.sensitive_local_only = config.sensitive_local_only
        self.cloud_default_provider = config.cloud_default_provider
        if self.cloud_default_provider not in {"azure", "openai", "bedrock", "vertex"}:
            self.cloud_default_provider = "openai"
        self.providers: dict[str, Provider] = {
            "local": LocalOllamaProvider(config.ollama_base_url, config.local_model),
            "azure": AzureOpenAIProvider(
                config.azure_openai_endpoint,
                config.azure_openai_api_key,
                config.azure_openai_deployment,
                config.azure_openai_api_version,
            ),
            "openai": OpenAIPublicProvider(config.openai_api_key, config.openai_model),
            "bedrock": BedrockProvider(
                config.aws_region,
                config.aws_access_key_id,
                config.aws_secret_access_key,
                config.bedrock_model_id,
            ),
            "vertex": VertexProvider(
                config.gcp_project_id,
                config.gcp_location,
                config.vertex_model,
            ),
        }

        self.sensitive_markers = {
            "client_secret",
            "client secret",
            "tenant_id",
            "tenant id",
            "object id",
            "api_key",
            "api key",
            "access token",
            "refresh token",
            "private key",
            "begin private key",
            "certificate",
            "thumbprint",
            "password",
        }
        self.guid_pattern = re.compile(
            r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
        )

    def _contains_sensitive_data(self, prompt: str) -> bool:
        lower_prompt = prompt.lower()
        if any(marker in lower_prompt for marker in self.sensitive_markers):
            return True
        if self.guid_pattern.search(prompt):
            return True
        return False

    def route(self, prompt: str, preferred: str = "auto") -> RoutingDecision:
        contains_sensitive_data = self._contains_sensitive_data(prompt)
        preferred = preferred.lower().strip()
        if preferred != "auto":
            if preferred not in self.providers:
                raise RuntimeError(
                    f"Unknown provider '{preferred}'. Use auto|local|azure|openai|bedrock|vertex"
                )
            if self.sensitive_local_only and preferred != "local" and contains_sensitive_data:
                return RoutingDecision(
                    provider="local",
                    reason="Sensitive content detected; provider overridden to local",
                )
            return RoutingDecision(provider=preferred, reason="User-selected provider")

        lower_prompt = prompt.lower()
        infra_keywords = {
            "deploy",
            "terraform",
            "bicep",
            "entra",
            "aws",
            "gcp",
            "azure",
            "production",
            "kubernetes",
            "iac",
            "pipeline",
        }

        if self.sensitive_local_only and contains_sensitive_data:
            return RoutingDecision(
                provider="local",
                reason="Sensitive content detected; routed to local provider",
            )

        is_infra = any(word in lower_prompt for word in infra_keywords)
        is_short = len(prompt.split()) <= 80

        if is_infra and not is_short:
            return RoutingDecision(
                provider=self.cloud_default_provider,
                reason="Infra/deployment-heavy prompt routed to cloud provider",
            )

        if is_infra:
            return RoutingDecision(
                provider=self.cloud_default_provider,
                reason="Infra prompt routed to cloud provider",
            )

        return RoutingDecision(
            provider="local",
            reason="Short/general prompt routed to local model",
        )

    def generate(self, prompt: str, preferred: str = "auto") -> tuple[str, RoutingDecision]:
        decision = self.route(prompt, preferred=preferred)
        provider = self.providers[decision.provider]
        result = provider.generate(prompt)
        return result, decision
