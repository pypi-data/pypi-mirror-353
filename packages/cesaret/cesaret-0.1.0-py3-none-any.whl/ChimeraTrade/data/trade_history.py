import json
import os

class TradeHistory:
    def __init__(self, history_file="data/trade_history.json"):
        self.history_file = history_file
        self.trades = self.load_trade_history()

    def load_trade_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []

    def save_trade_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.trades, f, indent=4)

    def add_trade(self, trade):
        self.trades.append(trade)
        self.save_trade_history()

    def get_trade_history(self):
        return self.trades

    def clear_trade_history(self):
        self.trades = []
        self.save_trade_history()
