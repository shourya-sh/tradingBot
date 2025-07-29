import time
import random
import json
from typing import Dict, List, Optional
from datetime import datetime
from config import (
    PAPER_TRADING_MODE, INITIAL_BALANCE, TRADING_PAIRS, 
    MAX_TRADE_AMOUNT, MIN_TRADE_AMOUNT, TRADE_INTERVAL,
    MAX_POSITION_SIZE, OFFICE_QUOTES
)
from coinbase_api import CoinbaseAPI, MockCoinbaseAPI

class PaperTradingBot:
    def __init__(self):
        # Initialize API (use mock if no credentials)
        try:
            self.api = CoinbaseAPI()
            # Test API connection
            test_price = self.api.get_current_price('BTC-USD')
            if test_price is None:
                print("API connection failed, using mock data")
                self.api = MockCoinbaseAPI()
        except Exception as e:
            print(f"Using mock API: {e}")
            self.api = MockCoinbaseAPI()
        
        # Portfolio state
        self.cash_balance = INITIAL_BALANCE
        self.positions = {}  # {asset: {'quantity': float, 'avg_price': float}}
        self.trade_history = []
        self.portfolio_value = INITIAL_BALANCE
        self.total_pnl = 0.0
        
        # Trading state
        self.last_trade_time = 0
        self.current_quote = random.choice(OFFICE_QUOTES)
        
    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value including positions"""
        total_value = self.cash_balance
        
        for asset, position in self.positions.items():
            current_price = self.api.get_current_price(asset)
            if current_price:
                position_value = position['quantity'] * current_price
                total_value += position_value
        
        return round(total_value, 2)
    
    def get_position_value(self, asset: str) -> float:
        """Get current value of a specific position"""
        if asset in self.positions:
            current_price = self.api.get_current_price(asset)
            if current_price:
                return round(self.positions[asset]['quantity'] * current_price, 2)
        return 0.0
    
    def calculate_pnl(self, asset: str) -> float:
        """Calculate profit/loss for a position"""
        if asset in self.positions:
            current_price = self.api.get_current_price(asset)
            if current_price:
                position = self.positions[asset]
                current_value = position['quantity'] * current_price
                cost_basis = position['quantity'] * position['avg_price']
                return round(current_value - cost_basis, 2)
        return 0.0
    
    def execute_buy(self, asset: str, amount: float) -> bool:
        """Execute a buy order (paper trading)"""
        current_price = self.api.get_current_price(asset)
        if not current_price or amount > self.cash_balance:
            return False
        
        quantity = amount / current_price
        cost = quantity * current_price
        
        # Update cash balance
        self.cash_balance -= cost
        
        # Update or create position
        if asset in self.positions:
            # Average down/up
            old_quantity = self.positions[asset]['quantity']
            old_avg_price = self.positions[asset]['avg_price']
            new_quantity = old_quantity + quantity
            new_avg_price = ((old_quantity * old_avg_price) + cost) / new_quantity
            self.positions[asset] = {
                'quantity': new_quantity,
                'avg_price': new_avg_price
            }
        else:
            self.positions[asset] = {
                'quantity': quantity,
                'avg_price': current_price
            }
        
        # Record trade
        self.record_trade('buy', asset, quantity, current_price, cost)
        return True
    
    def execute_sell(self, asset: str, amount: float) -> bool:
        """Execute a sell order (paper trading)"""
        if asset not in self.positions:
            return False
        
        current_price = self.api.get_current_price(asset)
        if not current_price:
            return False
        
        position = self.positions[asset]
        quantity_to_sell = amount / current_price
        
        if quantity_to_sell > position['quantity']:
            quantity_to_sell = position['quantity']  # Sell entire position
        
        proceeds = quantity_to_sell * current_price
        
        # Update cash balance
        self.cash_balance += proceeds
        
        # Update position
        remaining_quantity = position['quantity'] - quantity_to_sell
        if remaining_quantity <= 0:
            del self.positions[asset]  # Close position
        else:
            self.positions[asset]['quantity'] = remaining_quantity
        
        # Record trade
        self.record_trade('sell', asset, quantity_to_sell, current_price, proceeds)
        return True
    
    def record_trade(self, action: str, asset: str, quantity: float, price: float, total: float):
        """Record a trade in history"""
        trade = {
            'action': action,
            'asset': asset,
            'quantity': round(quantity, 6),
            'price': round(price, 2),
            'total': round(total, 2),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'portfolio_value': self.get_portfolio_value()
        }
        self.trade_history.append(trade)
        
        # Keep only last 50 trades
        if len(self.trade_history) > 50:
            self.trade_history.pop(0)
    
    def analyze_market(self, asset: str) -> Dict:
        """Simple market analysis for trading decisions"""
        current_price = self.api.get_current_price(asset)
        stats = self.api.get_24hr_stats(asset)
        
        if not current_price or not stats:
            return {'signal': 'hold', 'confidence': 0.0}
        
        # Simple analysis based on 24hr stats
        open_price = float(stats.get('open', current_price))
        high_price = float(stats.get('high', current_price))
        low_price = float(stats.get('low', current_price))
        
        # Calculate basic indicators
        price_change = current_price - open_price
        price_change_pct = (price_change / open_price) * 100
        volatility = (high_price - low_price) / open_price
        
        # Simple trading signals
        signal = 'hold'
        confidence = 0.5
        
        if price_change_pct > 2 and volatility < 0.1:  # Strong uptrend, low volatility
            signal = 'buy'
            confidence = 0.7
        elif price_change_pct < -2 and volatility < 0.1:  # Strong downtrend, low volatility
            signal = 'sell'
            confidence = 0.7
        elif price_change_pct > 5:  # Overbought
            signal = 'sell'
            confidence = 0.6
        elif price_change_pct < -5:  # Oversold
            signal = 'buy'
            confidence = 0.6
        
        return {
            'signal': signal,
            'confidence': confidence,
            'price_change_pct': round(price_change_pct, 2),
            'volatility': round(volatility * 100, 2),
            'current_price': current_price
        }
    
    def make_trading_decision(self) -> Optional[Dict]:
        """Make a trading decision based on market analysis"""
        current_time = time.time()
        if current_time - self.last_trade_time < TRADE_INTERVAL:
            return None
        
        decisions = []
        
        for asset in TRADING_PAIRS:
            analysis = self.analyze_market(asset)
            if analysis['confidence'] > 0.6:  # Only trade if confident
                decisions.append({
                    'asset': asset,
                    'signal': analysis['signal'],
                    'confidence': analysis['confidence'],
                    'analysis': analysis
                })
        
        if not decisions:
            return None
        
        # Pick the best decision
        best_decision = max(decisions, key=lambda x: x['confidence'])
        
        # Calculate trade amount
        portfolio_value = self.get_portfolio_value()
        max_amount = min(MAX_TRADE_AMOUNT, portfolio_value * MAX_POSITION_SIZE)
        trade_amount = random.uniform(MIN_TRADE_AMOUNT, max_amount)
        
        # Execute trade
        success = False
        if best_decision['signal'] == 'buy' and self.cash_balance >= trade_amount:
            success = self.execute_buy(best_decision['asset'], trade_amount)
        elif best_decision['signal'] == 'sell':
            position_value = self.get_position_value(best_decision['asset'])
            if position_value > 0:
                success = self.execute_sell(best_decision['asset'], min(trade_amount, position_value))
        
        if success:
            self.last_trade_time = current_time
            self.current_quote = random.choice(OFFICE_QUOTES)
            return {
                'decision': best_decision,
                'trade_amount': trade_amount,
                'success': True
            }
        
        return None
    
    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary"""
        portfolio_value = self.get_portfolio_value()
        total_pnl = portfolio_value - INITIAL_BALANCE
        pnl_pct = (total_pnl / INITIAL_BALANCE) * 100
        
        positions_summary = []
        for asset, position in self.positions.items():
            current_value = self.get_position_value(asset)
            pnl = self.calculate_pnl(asset)
            pnl_pct_pos = (pnl / (position['quantity'] * position['avg_price'])) * 100 if position['quantity'] > 0 else 0
            
            positions_summary.append({
                'asset': asset,
                'quantity': round(position['quantity'], 6),
                'avg_price': round(position['avg_price'], 2),
                'current_value': current_value,
                'pnl': pnl,
                'pnl_pct': round(pnl_pct_pos, 2)
            })
        
        return {
            'cash_balance': round(self.cash_balance, 2),
            'portfolio_value': portfolio_value,
            'total_pnl': round(total_pnl, 2),
            'pnl_pct': round(pnl_pct, 2),
            'positions': positions_summary,
            'total_trades': len(self.trade_history),
            'current_quote': self.current_quote
        } 