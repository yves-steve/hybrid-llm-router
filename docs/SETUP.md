# Setup (macOS)

## 1. Create virtual environment

```bash
cd hybrid-llm-router
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Install and run Ollama

```bash
brew install ollama
ollama serve
```

Open a new terminal and pull a model:

```bash
ollama pull llama3.1:8b
```

## 3. Configure environment variables

```bash
cp .env.example .env
```

Fill in cloud credentials you want to use. You can leave providers empty if you only want local mode.

## 4. Run hardware setup wizard

This will detect OS and RAM, ask about CPU/GPU, and write `config/hardware_profile.json`.

```bash
PYTHONPATH=src python -m hybrid_llm_router.setup_wizard
```

## 5. Run a prompt

```bash
PYTHONPATH=src python -m hybrid_llm_router.main "Summarize Entra app registration best practices" --show-routing
```

## 6. Force a provider

```bash
PYTHONPATH=src python -m hybrid_llm_router.main "Create a Terraform plan for VNet and private endpoints" --provider openai --show-routing
```
