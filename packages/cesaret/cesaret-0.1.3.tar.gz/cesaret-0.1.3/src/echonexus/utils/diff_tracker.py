class DiffTracker:
    def __init__(self):
        self.history = []

    def track_change(self, entry_id, old_state, new_state):
        diff = self.generate_diff(old_state, new_state)
        self.history.append({
            'entry_id': entry_id,
            'old_state': old_state,
            'new_state': new_state,
            'diff': diff
        })

    def generate_diff(self, old_state, new_state):
        # Simple line-by-line diff generation
        old_lines = old_state.splitlines()
        new_lines = new_state.splitlines()
        diff = []

        for line in new_lines:
            if line not in old_lines:
                diff.append(f'+ {line}')
        
        for line in old_lines:
            if line not in new_lines:
                diff.append(f'- {line}')

        return '\n'.join(diff)

    def get_history(self):
        return self.history

    def clear_history(self):
        self.history = []
