import os
from dotenv import load_dotenv

# Try to load .env file, but don't fail if it doesn't exist or has issues
try:
    load_dotenv()
except Exception as e:
    print(f"Note: Could not load .env file: {e}")
    print("Bot will use mock data instead of real API")

# Coinbase API Configuration
COINBASE_API_KEY = os.getenv('COINBASE_API_KEY', '7acb0699-9158-4913-a26e-33b873badb3e')
# Note: Newer Coinbase API only requires API key, not secret/passphrase

# Paper Trading Configuration
PAPER_TRADING_MODE = True  # Set to False for real trading (later)
INITIAL_BALANCE = 10000.0  # Starting balance in USD
TRADING_PAIRS = ['BTC-USD', 'ETH-USD', 'ADA-USD']  # Cryptocurrencies to trade

# Trading Bot Settings
MAX_TRADE_AMOUNT = 1000.0  # Maximum amount per trade
MIN_TRADE_AMOUNT = 50.0    # Minimum amount per trade
TRADE_INTERVAL = 30        # Seconds between trade decisions
MAX_POSITION_SIZE = 0.2    # Maximum 20% of portfolio in one asset

# Office Theme Settings
OFFICE_QUOTES = [
    "You miss 100% of the trades you don't take. – Michael Scott",
    "That's what she said! – Michael Scott",
    "Bears. Beets. Battlestar Galactica. ...And Trades. – Jim Halpert",
    "I'm not superstitious, but I am a little stitious. – Michael Scott",
    "Sometimes I'll start a sentence and I don't even know where it's going. – Michael Scott"
] 