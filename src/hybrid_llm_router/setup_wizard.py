from __future__ import annotations

from pathlib import Path

from .hardware import (
    HardwareProfile,
    detect_os,
    detect_ram_gb,
    recommend_cloud_default,
    recommend_local_model,
    write_profile,
)


def ask(prompt: str, default: str) -> str:
    raw = input(f"{prompt} [{default}]: ").strip()
    return raw if raw else default


def run_wizard() -> int:
    os_name = detect_os()
    ram_gb = detect_ram_gb()

    print("Hybrid LLM Router setup wizard")
    print("This configures local model and cloud defaults from your hardware.")
    print("---")

    cpu_notes = ask("CPU notes (apple-silicon/intel/amd/other)", "apple-silicon" if os_name == "darwin" else "intel")
    gpu_type = ask("GPU type (none/integrated/apple/nvidia/amd)", "apple" if os_name == "darwin" else "none")

    if ram_gb <= 0:
        ram_gb = int(ask("Detected RAM failed. Enter RAM in GB", "16"))
    else:
        print(f"Detected RAM: {ram_gb} GB")
        ram_override = ask("Use detected RAM? (yes/no)", "yes")
        if ram_override.lower() in {"n", "no"}:
            ram_gb = int(ask("Enter RAM in GB", str(ram_gb)))

    local_model = recommend_local_model(ram_gb, gpu_type)
    cloud_default = recommend_cloud_default(os_name)

    print("---")
    print(f"Recommended local model: {local_model}")
    print(f"Recommended cloud default: {cloud_default}")

    profile = HardwareProfile(
        os_name=os_name,
        ram_gb=ram_gb,
        cpu_notes=cpu_notes,
        gpu_type=gpu_type,
        recommended_local_model=local_model,
        recommended_cloud_default=cloud_default,
    )

    project_root = Path(__file__).resolve().parents[2]
    target = write_profile(profile, project_root)

    print(f"Saved hardware profile: {target}")
    print("Next: copy .env.example to .env and set LOCAL_MODEL to the recommended value.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_wizard())
