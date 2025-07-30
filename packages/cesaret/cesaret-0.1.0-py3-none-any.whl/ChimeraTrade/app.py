import os
import json
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from core.fractal_analyzer import FractalAnalyzer
from core.execution_handler import ExecutionHandler
from core.strategy_optimizer import StrategyOptimizer
from data.state_tracker import StateTracker
from data.trade_history import TradeHistory
from data.risk_manager import RiskManager
from models.signal_validator import SignalValidator
from models.pattern_detector import PatternDetector
from models.reinforcement_ai import ReinforcementAI
from execution.broker_interface import BrokerInterface
from execution.order_manager import OrderManager

app = Flask(__name__)
CORS(app)

# Initialize components
fractal_analyzer = FractalAnalyzer()
execution_handler = ExecutionHandler(BrokerInterface())
strategy_optimizer = StrategyOptimizer()
state_tracker = StateTracker()
trade_history = TradeHistory()
risk_manager = RiskManager()
signal_validator = SignalValidator()
pattern_detector = PatternDetector()
reinforcement_ai = ReinforcementAI()
order_manager = OrderManager()

@app.route('/fractals', methods=['GET'])
def get_fractals():
    """
    Endpoint to get detected fractals.
    Calls the detect_fractals method of the FractalAnalyzer and returns the detected fractals.
    """
    fractal_analyzer.detect_fractals()
    fractals = fractal_analyzer.get_fractals()
    return jsonify(fractals)

@app.route('/execute_trade', methods=['POST'])
def execute_trade():
    """
    Endpoint to execute a trade.
    Receives the symbol and quantity from the request and calls the execute_trade method of the ExecutionHandler.
    """
    data = request.json
    symbol = data.get('symbol')
    quantity = data.get('quantity')
    response = execution_handler.execute_trade(symbol, quantity)
    return jsonify(response)

@app.route('/optimize_strategy', methods=['POST'])
def optimize_strategy():
    """
    Endpoint to optimize the trading strategy.
    Receives new data from the request and calls the optimize_strategy method of the StrategyOptimizer.
    """
    data = request.json
    new_data = data.get('new_data')
    optimized_strategy = strategy_optimizer.optimize_strategy(new_data)
    return jsonify(optimized_strategy)

@app.route('/validate_signal', methods=['POST'])
def validate_signal():
    """
    Endpoint to validate a trading signal.
    Receives the signal from the request and calls the validate method of the SignalValidator.
    """
    data = request.json
    signal = data.get('signal')
    validation_result = signal_validator.validate(signal)
    return jsonify(validation_result)

@app.route('/detect_patterns', methods=['POST'])
def detect_patterns():
    """
    Endpoint to detect patterns in market data.
    Receives market data from the request and calls the detect method of the PatternDetector.
    """
    data = request.json
    market_data = data.get('market_data')
    patterns = pattern_detector.detect(market_data)
    return jsonify(patterns)

@app.route('/train_reinforcement_ai', methods=['POST'])
def train_reinforcement_ai():
    """
    Endpoint to train the reinforcement learning AI.
    Calls the train method of the ReinforcementAI.
    """
    reinforcement_ai.train()
    return jsonify({"message": "Reinforcement AI trained successfully"})

@app.route('/state_transitions', methods=['GET'])
def get_state_transitions():
    """
    Endpoint to get state transitions.
    Calls the get_transitions method of the StateTracker and returns the state transitions.
    """
    state_transitions = state_tracker.get_transitions()
    return jsonify(state_transitions)

@app.route('/trade_history', methods=['GET'])
def get_trade_history():
    """
    Endpoint to get trade history.
    Calls the get_history method of the TradeHistory and returns the trade history.
    """
    history = trade_history.get_history()
    return jsonify(history)

@app.route('/risk_management', methods=['POST'])
def manage_risk():
    """
    Endpoint to manage risk.
    Receives risk parameters from the request and calls the manage method of the RiskManager.
    """
    data = request.json
    risk_params = data.get('risk_params')
    risk_manager.manage(risk_params)
    return jsonify({"message": "Risk management applied"})

@app.route('/')
def home():
    """
    Home endpoint.
    Returns a welcome message for the ChimeraTrade AI-assisted Trading System.
    """
    return "Welcome to the ChimeraTrade AI-assisted Trading System!"

if __name__ == "__main__":
    app.run(debug=True)
