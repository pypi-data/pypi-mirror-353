class RiskManager:
    def __init__(self, initial_balance: float, stop_loss_pct: float, position_size_pct: float):
        self.balance = initial_balance
        self.stop_loss_pct = stop_loss_pct
        self.position_size_pct = position_size_pct
        self.current_position = None

    def calculate_position_size(self, price: float) -> float:
        position_size = self.balance * self.position_size_pct / 100
        return position_size / price

    def set_stop_loss(self, entry_price: float) -> float:
        stop_loss_price = entry_price * (1 - self.stop_loss_pct / 100)
        return stop_loss_price

    def update_balance(self, profit_loss: float):
        self.balance += profit_loss

    def enter_position(self, price: float):
        position_size = self.calculate_position_size(price)
        stop_loss_price = self.set_stop_loss(price)
        self.current_position = {
            'entry_price': price,
            'position_size': position_size,
            'stop_loss_price': stop_loss_price
        }

    def exit_position(self, exit_price: float):
        if self.current_position:
            entry_price = self.current_position['entry_price']
            position_size = self.current_position['position_size']
            profit_loss = (exit_price - entry_price) * position_size
            self.update_balance(profit_loss)
            self.current_position = None

    def check_stop_loss(self, current_price: float):
        if self.current_position and current_price <= self.current_position['stop_loss_price']:
            self.exit_position(current_price)
