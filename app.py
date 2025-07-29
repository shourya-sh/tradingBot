import threading
import time
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from trading_bot import PaperTradingBot

app = Flask(__name__)
CORS(app)

# Initialize the trading bot
trading_bot = PaperTradingBot()

def trading_bot_worker():
    """Background worker for the trading bot"""
    while True:
        try:
            # Make trading decisions
            decision = trading_bot.make_trading_decision()
            if decision:
                print(f"Trade executed: {decision['decision']['signal']} {decision['decision']['asset']}")
            
            # Update portfolio value
            trading_bot.portfolio_value = trading_bot.get_portfolio_value()
            
        except Exception as e:
            print(f"Error in trading bot: {e}")
        
        time.sleep(5)  # Check every 5 seconds

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/portfolio')
def get_portfolio():
    """Get comprehensive portfolio information"""
    return jsonify(trading_bot.get_portfolio_summary())

@app.route('/api/trades')
def get_trades():
    """Get recent trade history"""
    return jsonify(trading_bot.trade_history)

@app.route('/api/market-data')
def get_market_data():
    """Get current market data for all trading pairs"""
    market_data = {}
    for asset in trading_bot.api.get_products():
        if asset['id'] in ['BTC-USD', 'ETH-USD', 'ADA-USD']:
            current_price = trading_bot.api.get_current_price(asset['id'])
            stats = trading_bot.api.get_24hr_stats(asset['id'])
            analysis = trading_bot.analyze_market(asset['id'])
            
            market_data[asset['id']] = {
                'current_price': current_price,
                'stats': stats,
                'analysis': analysis
            }
    
    return jsonify(market_data)

@app.route('/api/balance')
def get_balance():
    """Get current cash balance (legacy endpoint)"""
    return jsonify({"balance": trading_bot.cash_balance})

if __name__ == '__main__':
    # Start trading bot in background
    t = threading.Thread(target=trading_bot_worker, daemon=True)
    t.start()
    
    # Use a fixed port
    port = 5000
    print(f"Running on http://localhost:{port}")
    print("Paper Trading Bot is active!")
    print("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=port, debug=True) 