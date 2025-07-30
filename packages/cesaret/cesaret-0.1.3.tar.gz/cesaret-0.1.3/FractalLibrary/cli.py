import argparse
import importlib
import json
from pathlib import Path

from .core.FractalLibrary import FractalLibrary


def run_demo(interactive: bool) -> None:
    """Run the FractalLibrary demonstration."""
    module = importlib.import_module("FractalLibrary.core.demonstrate_library")
    if interactive:
        print("Running FractalLibrary demo.\n")
        auto = input("Run automatically without pauses? [y/N]: ").lower().startswith("y")
        if not auto:
            module.pause = lambda s=1: input("Press Enter to continue...")
        else:
            module.pause = lambda s=1: None
    else:
        module.pause = lambda s=1: None
    module.main()


def show_state(path: str) -> None:
    """Display a summary of a saved library state."""
    data = json.loads(Path(path).read_text())
    print(f"Nodes: {len(data.get('nodes', {}))}")
    print(f"Dream spaces: {len(data.get('dream_spaces', {}))}")
    print(f"Character spaces: {len(data.get('character_spaces', {}))}")
    if 'timestamp' in data:
        print(f"Timestamp: {data['timestamp']}")
    sample = list(data.get('nodes', {}).keys())[:5]
    if sample:
        print("Sample nodes:")
        for node in sample:
            print(f"  - {node}")


def main() -> None:
    parser = argparse.ArgumentParser(description="FractalLibrary command line tools")
    sub = parser.add_subparsers(dest="command")

    demo_p = sub.add_parser("demo", help="Run the narrative demonstration")
    demo_p.add_argument("--interactive", action="store_true", help="Prompt between stages")

    show_p = sub.add_parser("show", help="Show summary of a saved state file")
    show_p.add_argument("path", help="Path to state JSON")

    args = parser.parse_args()

    if args.command == "demo":
        run_demo(args.interactive)
    elif args.command == "show":
        show_state(args.path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
