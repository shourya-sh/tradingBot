import requests
import time
import json
from typing import Dict, List, Optional
from config import COINBASE_API_KEY

class CoinbaseAPI:
    def __init__(self):
        self.api_key = COINBASE_API_KEY
        # Use the public API endpoints that don't require authentication
        self.base_url = "https://api.coinbase.com/v2"
        
    def get_current_price(self, product_id: str) -> Optional[float]:
        """Get current price for a trading pair using Coinbase public API"""
        try:
            # Convert product_id format (BTC-USD -> BTC-USD)
            currency_pair = product_id.replace('-', '-')
            
            url = f"{self.base_url}/prices/{currency_pair}/spot"
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return float(data['data']['amount'])
            else:
                print(f"Error fetching price for {product_id}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception fetching price for {product_id}: {e}")
            return None
    
    def get_24hr_stats(self, product_id: str) -> Optional[Dict]:
        """Get 24-hour statistics for a trading pair"""
        try:
            # For now, return mock stats since Coinbase public API doesn't provide this
            current_price = self.get_current_price(product_id)
            if current_price:
                return {
                    'open': current_price * 0.98,
                    'high': current_price * 1.05,
                    'low': current_price * 0.95,
                    'volume': 1000000.0
                }
            return None
        except Exception as e:
            print(f"Exception fetching stats for {product_id}: {e}")
            return None
    
    def get_products(self) -> List[Dict]:
        """Get list of available trading products"""
        try:
            url = f"{self.base_url}/currencies"
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                currencies = response.json()['data']
                # Filter for the currencies we want to trade
                trading_currencies = ['BTC', 'ETH', 'ADA']
                return [
                    {'id': f'{currency}-USD', 'base_currency': currency, 'quote_currency': 'USD'}
                    for currency in trading_currencies
                ]
            else:
                print(f"Error fetching products: {response.status_code}")
                return []
        except Exception as e:
            print(f"Exception fetching products: {e}")
            return []
    
    def get_historical_prices(self, product_id: str, granularity: int = 3600) -> List[Dict]:
        """Get historical price data"""
        try:
            # For now, return mock historical data
            current_price = self.get_current_price(product_id)
            if current_price:
                return [[int(time.time()), current_price, current_price, current_price, current_price, 1000.0]]
            return []
        except Exception as e:
            print(f"Exception fetching historical data for {product_id}: {e}")
            return []

# Fallback price data for when API is not configured
class MockCoinbaseAPI:
    """Mock API for testing without real API credentials"""
    
    def __init__(self):
        self.mock_prices = {
            'BTC-USD': 45000.0,
            'ETH-USD': 3200.0,
            'ADA-USD': 0.45
        }
        self.price_variation = 0.02  # 2% variation
    
    def get_current_price(self, product_id: str) -> Optional[float]:
        """Return mock price with some variation"""
        if product_id in self.mock_prices:
            import random
            variation = random.uniform(-self.price_variation, self.price_variation)
            self.mock_prices[product_id] *= (1 + variation)
            return round(self.mock_prices[product_id], 2)
        return None
    
    def get_24hr_stats(self, product_id: str) -> Optional[Dict]:
        """Return mock 24hr stats"""
        price = self.get_current_price(product_id)
        if price:
            return {
                'open': price * 0.98,
                'high': price * 1.05,
                'low': price * 0.95,
                'volume': 1000000.0
            }
        return None
    
    def get_products(self) -> List[Dict]:
        """Return mock product list"""
        return [
            {'id': 'BTC-USD', 'base_currency': 'BTC', 'quote_currency': 'USD'},
            {'id': 'ETH-USD', 'base_currency': 'ETH', 'quote_currency': 'USD'},
            {'id': 'ADA-USD', 'base_currency': 'ADA', 'quote_currency': 'USD'}
        ]
    
    def get_historical_prices(self, product_id: str, granularity: int = 3600) -> List[Dict]:
        """Return mock historical data"""
        price = self.get_current_price(product_id)
        if price:
            return [[int(time.time()), price, price, price, price, 1000.0]]
        return [] 