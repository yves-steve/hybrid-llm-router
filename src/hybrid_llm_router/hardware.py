from __future__ import annotations

import json
import os
import platform
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class HardwareProfile:
    os_name: str
    ram_gb: int
    cpu_notes: str
    gpu_type: str
    recommended_local_model: str
    recommended_cloud_default: str


def detect_os() -> str:
    return platform.system().lower()


def detect_ram_gb() -> int:
    os_name = detect_os()

    if os_name in {"linux", "darwin"}:
        try:
            pages = os.sysconf("SC_PHYS_PAGES")
            page_size = os.sysconf("SC_PAGE_SIZE")
            total_bytes = pages * page_size
            return max(1, round(total_bytes / (1024**3)))
        except (ValueError, OSError, AttributeError):
            return 0

    if os_name == "windows":
        try:
            output = subprocess.check_output(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)",
                ],
                text=True,
            )
            return int(output.strip())
        except Exception:
            return 0

    return 0


def recommend_local_model(ram_gb: int, gpu_type: str) -> str:
    if ram_gb and ram_gb < 16:
        return "llama3.2:3b"
    if ram_gb and ram_gb < 32:
        return "llama3.1:8b"
    if gpu_type in {"nvidia", "apple", "amd"}:
        return "qwen2.5:14b"
    return "llama3.1:8b"


def recommend_cloud_default(os_name: str) -> str:
    # Default to OpenAI for cross-platform quick start; users can switch later.
    if os_name == "darwin":
        return "openai"
    return "openai"


def write_profile(profile: HardwareProfile, project_root: Path) -> Path:
    config_dir = project_root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    target = config_dir / "hardware_profile.json"
    target.write_text(json.dumps(asdict(profile), indent=2), encoding="utf-8")
    return target


def load_profile(project_root: Path) -> HardwareProfile | None:
    target = project_root / "config" / "hardware_profile.json"
    if not target.exists():
        return None

    data = json.loads(target.read_text(encoding="utf-8"))
    return HardwareProfile(**data)
