from __future__ import annotations

import argparse
import sys

from .config import load_config
from .router import HybridRouter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Hybrid LLM Router: local + cloud providers"
    )
    parser.add_argument("prompt", help="Prompt text to send")
    parser.add_argument(
        "--provider",
        default="auto",
        choices=["auto", "local", "azure", "openai", "bedrock", "vertex"],
        help="Provider override. Default is auto routing.",
    )
    parser.add_argument(
        "--show-routing",
        action="store_true",
        help="Print provider selection details",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config()
    router = HybridRouter(config)

    try:
        text, decision = router.generate(args.prompt, preferred=args.provider)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.show_routing:
        print(f"Provider: {decision.provider}")
        print(f"Reason: {decision.reason}")
        print("---")

    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
