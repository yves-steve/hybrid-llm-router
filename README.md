# Hybrid LLM Router (Local + Cloud)

This project lets you run prompts against a local LLM on your MacBook Pro and selectively route cloud-heavy prompts to public cloud LLM providers.

Tiny humor promise: this router is a traffic cop for prompts, not your home Wi-Fi (though it is opinionated about directions).

## What Ollama Is

Ollama is a local model runtime that lets you download and run LLMs directly on your laptop.

- It exposes a local HTTP API (default: `http://localhost:11434`)
- It keeps prompts and outputs on-device unless you explicitly send data elsewhere
- It is ideal for private drafts, fast iterations, and lower-cost experimentation

In this project, Ollama is the default local provider used when routing chooses `local`.

## High-Level System Flow

Once setup is complete, the moving parts look like this:

1. You submit a prompt in the CLI.
2. The router evaluates the prompt and routing mode (`auto` or explicit provider).
3. In `auto`, prompt patterns decide local vs cloud provider.
4. Provider adapter sends the request to Ollama or a cloud endpoint.
5. Response is returned with optional routing metadata (`--show-routing`).

Practical split:

- Local path: privacy-sensitive notes, quick drafts, lightweight scripting
- Cloud path: complex infra planning, large-context synthesis, advanced reasoning

## Why this project

- Keep common/private prompts local with Ollama
- Route infra/deployment prompts to cloud LLMs when needed
- Build cloud-focused projects (Entra, AWS, GCP) with one routing interface

## Primary Use Case (Simple)

This repo is mainly for one workflow:

- Terraform work for infrastructure changes
- PowerShell Graph SDK scripting for M365 and Entra tenant automation
- Writing implementation guides and runbooks from the same prompts

Simple routing rule for this use case:

- Use local for tenant-specific scripting drafts and anything with sensitive identifiers
- Use cloud for large Terraform refactors, architecture tradeoff analysis, and long-form documentation polish

## Example Scenario: Terraform + Graph In One Project

Example project goal:

1. Use Terraform to deploy baseline Azure resources for identity operations (resource group, storage account, key vault).
2. Use Microsoft Graph PowerShell SDK to configure tenant objects (app registration, service principal, security group membership).
3. Generate an operations guide that explains provisioning order, rollback, and least-privilege checks.

How hybrid helps:

- Local model: draft PowerShell scripts that include tenant-specific names and object IDs.
- Cloud model: review Terraform module structure and produce a cleaner deployment guide for your team.

Example prompts:

- Local: "Create a Microsoft Graph PowerShell script to create an app registration, then assign required Graph application permissions with admin consent steps documented."
- Cloud: "Review this Terraform layout and propose a safer module structure with remote state, naming convention, and environment separation."

## Current status

- Local provider (Ollama): working
- Azure/OpenAI/AWS Bedrock/GCP Vertex: scaffolded with validation and TODOs for API calls
- Auto-router: implemented with keyword and prompt-length rules
- Hardware wizard: implemented for macOS/Linux/Windows onboarding

## Project layout

- src/hybrid_llm_router/config.py: environment-driven config
- src/hybrid_llm_router/router.py: routing logic and provider selection
- src/hybrid_llm_router/providers/: local + cloud provider adapters
- src/hybrid_llm_router/main.py: CLI entrypoint
- src/hybrid_llm_router/setup_wizard.py: interactive hardware onboarding
- docs/SETUP.md: install and run steps
- docs/REQUIREMENTS.md: prerequisites
- agents/agent.yaml: agent metadata and routing defaults

## Quick start

```bash
cd hybrid-llm-router
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Optional but recommended: detect hardware and apply local model defaults
PYTHONPATH=src python -m hybrid_llm_router.setup_wizard

# Start Ollama in another terminal: ollama serve
# Pull model once: ollama pull llama3.1:8b

PYTHONPATH=src python -m hybrid_llm_router.main "Draft a secure Entra + AWS identity pattern" --show-routing
```

## Does hybrid routing work?

Yes. You can route per query using:

- `--provider local` for local only
- `--provider azure|openai|bedrock|vertex` for explicit cloud
- `--provider auto` to let the router decide

By default, `auto` uses local for short/general prompts and cloud for infra/deployment terms such as `deploy`, `terraform`, `bicep`, `entra`, `aws`, `gcp`, `azure`, `production`.

If you run the wizard, cloud default provider and local model can be adapted from detected hardware profile.

## Quick Definitions

- Router: decision logic that chooses where a prompt goes (local model or cloud model).
- Provider: a model backend such as Ollama, Azure OpenAI, OpenAI, Bedrock, or Vertex.
- Local model: model running on your machine (for privacy, speed, or cost control).
- Cloud model: managed model in a public cloud provider (for larger context, advanced capability, or team-standard usage).
- Auto routing: default mode where the router decides provider based on prompt patterns and rules.
- Hardware profile: saved machine info (OS, RAM, CPU/GPU notes) used to suggest sane defaults.

## Threat Model And Routing Policy

Yes, you should decide this early. A simple policy is:

1. Data sensitivity classification
	- `Confidential`: secrets, internal architecture, tenant identifiers
	- `Internal`: runbooks, non-sensitive scripts
	- `Public`: blog-style docs, generic code examples
2. Routing policy by classification
	- `Confidential`: local only (`--provider local`)
	- `Internal`: local by default, cloud only after redaction
	- `Public`: local or cloud depending on quality/cost needs
3. Guardrails
	- Never send raw secrets, tokens, private keys, or customer data to cloud models
	- Prefer templates and placeholders in prompts (`<TENANT_ID>`, `<SUBSCRIPTION_ID>`)
	- Keep cloud provider credentials in env vars only

## Secret Handling Rules (Required)

Use these rules for this project:

1. Never hardcode secrets or tenant identifiers in code, docs, prompts, or examples.
2. Keep local secrets only in `.env` (never commit it).
3. For CI/CD (GitHub Actions), store all sensitive values in repository or environment secrets.
4. Use placeholders in docs and scripts, for example: `TENANT_ID_PLACEHOLDER`.
5. If a prompt contains tenant IDs, object IDs, app IDs, client secrets, or certificates, force local routing.

Suggested GitHub Secrets names:

- `AZURE_TENANT_ID`
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_SUBSCRIPTION_ID`
- `OPENAI_API_KEY`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Minimal GitHub Actions pattern:

```yaml
env:
  AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
  AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
  AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
```

## Public GitHub Repo Guidance

Yes, you can publish this project as a public repository, but treat security as part of release criteria.

Before publishing:

1. Verify `.env` is never committed and `.gitignore` is active.
2. Ensure all docs use placeholders, not real tenant IDs or object IDs.
3. Rotate any keys that might have been used in local testing.
4. Turn on GitHub secret scanning and dependency alerts.
5. Keep all CI secrets in GitHub Secrets, never in workflow YAML literals.

Recommended repository settings:

- Enable Dependabot alerts and updates
- Enable secret scanning and push protection
- Protect `main` with PR reviews
- Require status checks before merge
- Use environment-scoped secrets for prod deployments

For this project specifically:

- Keep `SENSITIVE_LOCAL_ONLY=true` for public usage.
- Use local routing for prompts containing tenant IDs, app IDs, object IDs, tokens, or certificates.
- Redact identifiers before requesting cloud model review.

## Model Selection Guide

Use this as a starting matrix. Exact best model depends on your hardware and quality targets.

### Local model sizing

- 8-16 GB RAM: `llama3.2:3b` for fast drafts and short scripts
- 16-32 GB RAM: `llama3.1:8b` for balanced scripting and doc writing
- 32 GB+ RAM (or strong GPU): `qwen2.5:14b` for better code+reasoning quality

### By workload

- Terraform-heavy work (module composition, plan explanations, policy docs)
  - Local: `qwen2.5:14b` (or `llama3.1:8b` if constrained)
  - Cloud: your strongest coding/reasoning model (OpenAI/Azure equivalent)
- Entra + PowerShell SDK scripting
  - Local: `llama3.1:8b` for script skeletons and docs
  - Cloud: stronger model for API edge cases, permission design, and troubleshooting
- Bicep + Bash/PowerShell automation
  - Local: `llama3.1:8b` minimum, `qwen2.5:14b` preferred for multi-file IaC changes
  - Cloud: use when combining architecture decisions + code generation + validation logic
- Guide writing and runbooks
  - Local: `llama3.1:8b` is often enough
  - Cloud: use for polishing, consistency checks, and long-context synthesis

## Suggested Use Cases

1. Private tenant automation draft
	- Prompt includes tenant details and role names
	- Route: local
2. Terraform module strategy comparison
	- Prompt compares options across AWS/Azure/GCP
	- Route: cloud
3. Bicep script hardening checklist
	- Prompt asks for idempotency, naming, linting, and rollback guidance
	- Route: local first, cloud second for final review
4. Entra onboarding guide
	- Draft locally, then cloud-polish style and structure after removing sensitive details

## Next steps

1. Implement each cloud provider API call in `providers/*.py`
2. Add retries/telemetry/tracing
3. Add policy rules (for example: never send secrets to cloud)
