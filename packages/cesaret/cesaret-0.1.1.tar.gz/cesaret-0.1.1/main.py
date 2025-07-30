#!/usr/bin/env python3
"""Project entry point for CeSaReT utilities."""
import argparse
import importlib
import json
import sys
from pathlib import Path

# Ensure `src` is on the path so the package can be imported when running
# directly from the repository without installation.
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echonexus.utils.terminal_ledger import TerminalLedgerRenderer
import requests



def run_echo_api(interactive: bool) -> None:
    if interactive:
        print("Launches the EchoNexus API server. Use the client in another shell to explore.")
        host = input("Host [127.0.0.1]: ") or "127.0.0.1"
        port = input("Port [8000]: ") or "8000"
    else:
        host = "127.0.0.1"
        port = "8000"
    try:
        from echonexus.api.main import app
        import uvicorn
    except Exception as exc:
        print("Could not start API:", exc)
        return
    uvicorn.run(app, host=host, port=int(port))


def run_fractal_demo(interactive: bool) -> None:
    if interactive:
        print("Running FractalLibrary demonstration. This showcases pattern evolution and narrative generation.\n")
    module = importlib.import_module("FractalLibrary.core.demonstrate_library")
    if hasattr(module, "main"):
        module.main()
    else:
        module.pause = lambda s=1: None
        module.create_tushell_journey(module.FractalLibrary())


def run_echo_api_client(interactive: bool) -> None:
    if interactive:
        print("Interact with the EchoNexus API to query state or post feedback.")
        host = input("Host [127.0.0.1]: ") or "127.0.0.1"
        port = input("Port [8000]: ") or "8000"
    else:
        host = "127.0.0.1"
        port = "8000"
    base = f"http://{host}:{port}"
    while True:
        if interactive:
            print("\n1) Get state\n2) Post feedback\nq) Quit")
            choice = input("Select option: ").strip()
        else:
            choice = "q"
        if choice == "1":
            ids = requests.get(f"{base}/entries").json()
            default_id = ids[0] if ids else ""
            available = ", ".join(ids) if ids else "none"
            prompt = f"Entry ID [{default_id}] (available: {available}): "
            entry_id = input(prompt) or default_id
            r = requests.get(f"{base}/state/{entry_id}")
            if r.status_code == 404:
                print("Entry not found. Available IDs:", available)
            else:
                print(r.status_code, r.json())
        elif choice == "2":
            ids = requests.get(f"{base}/entries").json()
            default_id = ids[0] if ids else ""
            available = ", ".join(ids) if ids else "none"
            prompt = f"Entry ID [{default_id}] (available: {available}): "
            entry_id = input(prompt) or default_id
            feedback = input("Feedback: ")
            r = requests.post(f"{base}/feedback/{entry_id}", json={"feedback": feedback})
            print(r.status_code, r.json())
        else:
            break


def show_ledger(interactive: bool) -> None:
    ledger_files = sorted(Path("codex/ledgers").glob("ledger-*.json"))
    if not ledger_files:
        print("No ledger files found")
        return
    if interactive:
        print("Select a ledger to review recorded agent contributions.")
        for i, lf in enumerate(ledger_files, 1):
            print(f"{i}: {lf.name}")
        choice = int(input("Select ledger to view [1]: ") or "1")
        file_path = ledger_files[choice - 1]
    else:
        file_path = ledger_files[-1]
    with open(file_path) as f:
        data = json.load(f)
    renderer = TerminalLedgerRenderer(data)
    renderer.display(interactive)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CeSaReT exploration CLI. Use one of the commands below to explore components.")
    sub = parser.add_subparsers(dest="command")

    api_p = sub.add_parser(
        "echo-api",
        help="Run the EchoNexus server",
        description="Start the FastAPI service that exposes narrative state endpoints.")
    api_p.add_argument("--interactive", action="store_true", help="Prompt for host/port interactively")

    demo_p = sub.add_parser(
        "fractal-demo",
        help="Demonstrate the FractalLibrary",
        description="Run a scripted tour showing pattern evolution and story generation.")
    demo_p.add_argument("--interactive", action="store_true", help="Interactive mode")

    ledger_p = sub.add_parser(
        "ledger",
        help="View ledger history",
        description="Display JSON-ledger entries tracking development steps.")
    ledger_p.add_argument("--interactive", action="store_true", help="Interactive selection")

    client_p = sub.add_parser(
        "echo-api-client",
        help="Client for the EchoNexus API",
        description="Query state or submit feedback to the running server.")
    client_p.add_argument("--interactive", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    if args.command == "echo-api":
        run_echo_api(args.interactive)
    elif args.command == "fractal-demo":
        run_fractal_demo(args.interactive)
    elif args.command == "ledger":
        show_ledger(args.interactive)
    elif args.command == "echo-api-client":
        run_echo_api_client(args.interactive)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
