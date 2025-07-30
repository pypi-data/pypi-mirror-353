class TerminalLedgerRenderer:
    """Render ledger entries in a terminal friendly format."""

    def __init__(self, entries):
        self.entries = entries

    def display(self, interactive: bool = False) -> None:
        total = len(self.entries)
        for idx, entry in enumerate(self.entries, 1):
            agents = entry.get("agent") or ", ".join(entry.get("agents", []))
            print(f"\n=== Entry {idx}/{total} ===")
            if agents:
                print(f"Agents: {agents}")
            if entry.get("timestamp"):
                print(f"Timestamp: {entry['timestamp']}")
            if entry.get("narrative"):
                print(f"Narrative: {entry['narrative']}")
            if entry.get("user_input"):
                print(f"User Input: {entry['user_input']}")
            if entry.get("routing"):
                print(f"Files: {entry['routing']}")
            if entry.get("scene"):
                print(f"Scene: {entry['scene']}")
            if interactive and idx < total:
                inp = input("Press Enter for next (q to quit)...")
                if inp.lower().startswith('q'):
                    break
