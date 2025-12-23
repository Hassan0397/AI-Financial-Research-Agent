import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from typing import Optional, Dict, Any, List
import threading
from requests.exceptions import RequestException

# Enhanced cache with TTL and cleanup
cache = {}
CACHE_DURATION = {
    'crypto': 15,  # Crypto prices update faster
    'stock': 30,   # Stock prices
    'search': 300  # Search results
}

class CacheManager:
    """Enhanced cache management with automatic cleanup"""
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get cached data if valid"""
        current_time = time.time()
        if key in cache:
            data, timestamp, ttl = cache[key]
            if current_time - timestamp < ttl:
                return data
            else:
                # Auto-clean expired cache
                del cache[key]
        return None
    
    @staticmethod
    def set(key: str, data: Any, cache_type: str = 'default'):
        """Store data in cache with appropriate TTL"""
        ttl = CACHE_DURATION.get(cache_type, 60)
        cache[key] = (data, time.time(), ttl)
    
    @staticmethod
    def clean_old_entries():
        """Clean old cache entries"""
        current_time = time.time()
        keys_to_delete = []
        for key, (_, timestamp, ttl) in cache.items():
            if current_time - timestamp > ttl:
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del cache[key]

# -----------------------------------------------------------
#  ENHANCED CRYPTO DATA FETCHER WITH MULTI-SOURCE VERIFICATION
# -----------------------------------------------------------

def get_crypto_data(coin_id: str, verify_with_multiple: bool = True) -> Dict[str, Any]:
    """
    Enhanced crypto data fetcher with multi-source verification
    Returns accurate real-time prices
    """
    cache_key = f"crypto_{coin_id.lower()}"
    cached = CacheManager.get(cache_key)
    if cached:
        return cached
    
    try:
        # Normalize coin ID
        coin_id = coin_id.lower()
        
        # Try primary source (CoinGecko)
        primary_data = _fetch_from_coingecko(coin_id)
        
        if primary_data and primary_data.get("status") == "success":
            if verify_with_multiple:
                # Verify with secondary source
                secondary_data = _fetch_from_coincap(coin_id)
                if secondary_data and secondary_data.get("status") == "success":
                    # Compare prices - if difference is significant, flag it
                    price1 = primary_data.get('current_price', 0)
                    price2 = secondary_data.get('current_price', 0)
                    
                    if price1 > 0 and price2 > 0:
                        price_diff = abs(price1 - price2) / min(price1, price2) * 100
                        if price_diff > 2:  # More than 2% difference
                            primary_data['price_discrepancy'] = f"{price_diff:.2f}%"
                            primary_data['verified_with'] = 'multiple_sources_discrepancy'
                        else:
                            primary_data['verified_with'] = 'multiple_sources_consistent'
                    else:
                        primary_data['verified_with'] = 'coingecko_only'
            
            CacheManager.set(cache_key, primary_data, 'crypto')
            return primary_data
        
        # If primary failed, try secondary
        secondary_data = _fetch_from_coincap(coin_id)
        if secondary_data and secondary_data.get("status") == "success":
            CacheManager.set(cache_key, secondary_data, 'crypto')
            return secondary_data
        
        # If both failed, try third source
        third_data = _fetch_from_alternative(coin_id)
        if third_data:
            CacheManager.set(cache_key, third_data, 'crypto')
            return third_data
        
        return {"error": "Unable to fetch data from any source", "status": "error"}
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

def _fetch_from_coingecko(coin_id: str) -> Optional[Dict[str, Any]]:
    """Fetch data from CoinGecko API"""
    try:
        # Simple price API first (faster)
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'precision': 8
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if coin_id in data:
                coin_data = data[coin_id]
                
                # Get detailed data
                detail_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
                detail_response = requests.get(detail_url, timeout=5, params={
                    'localization': 'false',
                    'tickers': 'false',
                    'market_data': 'true',
                    'community_data': 'false',
                    'developer_data': 'false',
                    'sparkline': 'false'
                })
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    market_data = detail_data.get('market_data', {})
                    
                    result = {
                        "id": coin_id,
                        "name": detail_data.get('name', coin_id.upper()),
                        "symbol": detail_data.get('symbol', '').upper(),
                        "current_price": float(coin_data.get('usd', 0)),
                        "price_change_24h": float(market_data.get('price_change_24h', 0)),
                        "price_change_percentage_24h": float(market_data.get('price_change_percentage_24h', 0)),
                        "market_cap": float(market_data.get('market_cap', {}).get('usd', 0)),
                        "total_volume": float(market_data.get('total_volume', {}).get('usd', 0)),
                        "high_24h": float(market_data.get('high_24h', {}).get('usd', 0)),
                        "low_24h": float(market_data.get('low_24h', {}).get('usd', 0)),
                        "ath": float(market_data.get('ath', {}).get('usd', 0)),
                        "ath_change_percentage": float(market_data.get('ath_change_percentage', {}).get('usd', 0)),
                        "circulating_supply": float(market_data.get('circulating_supply', 0)),
                        "total_supply": float(market_data.get('total_supply', 0)),
                        "max_supply": float(market_data.get('max_supply', 0)),
                        "last_updated": market_data.get('last_updated', datetime.now().isoformat()),
                        "source": "coingecko",
                        "status": "success"
                    }
                    return result
                else:
                    # Fallback to simple data
                    return {
                        "id": coin_id,
                        "name": coin_id.upper(),
                        "symbol": coin_id.upper()[:3],
                        "current_price": float(coin_data.get('usd', 0)),
                        "price_change_24h": float(coin_data.get('usd_24h_change', 0)),
                        "price_change_percentage_24h": float(coin_data.get('usd_24h_change', 0)),
                        "market_cap": float(coin_data.get('usd_market_cap', 0)),
                        "total_volume": float(coin_data.get('usd_24h_vol', 0)),
                        "last_updated": datetime.now().isoformat(),
                        "source": "coingecko_simple",
                        "status": "success"
                    }
    except Exception:
        return None

def _fetch_from_coincap(coin_id: str) -> Optional[Dict[str, Any]]:
    """Fetch data from CoinCap API (alternative)"""
    try:
        # Try different ID formats
        url = f"https://api.coincap.io/v2/assets/{coin_id}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            
            result = {
                "id": coin_id,
                "name": data.get('name', coin_id.upper()),
                "symbol": data.get('symbol', coin_id.upper()[:3]),
                "current_price": float(data.get('priceUsd', 0)),
                "price_change_24h": float(data.get('changePercent24Hr', 0)),
                "price_change_percentage_24h": float(data.get('changePercent24Hr', 0)),
                "market_cap": float(data.get('marketCapUsd', 0)),
                "total_volume": float(data.get('volumeUsd24Hr', 0)),
                "supply": float(data.get('supply', 0)),
                "max_supply": float(data.get('maxSupply', 0)),
                "last_updated": datetime.now().isoformat(),
                "source": "coincap",
                "status": "success"
            }
            return result
        
        # Try search if direct fetch fails
        search_url = f"https://api.coincap.io/v2/assets?search={coin_id}"
        search_response = requests.get(search_url, timeout=5)
        if search_response.status_code == 200:
            assets = search_response.json().get('data', [])
            if assets:
                asset = assets[0]
                return {
                    "id": asset.get('id', coin_id),
                    "name": asset.get('name', coin_id.upper()),
                    "symbol": asset.get('symbol', coin_id.upper()[:3]),
                    "current_price": float(asset.get('priceUsd', 0)),
                    "price_change_24h": float(asset.get('changePercent24Hr', 0)),
                    "price_change_percentage_24h": float(asset.get('changePercent24Hr', 0)),
                    "market_cap": float(asset.get('marketCapUsd', 0)),
                    "total_volume": float(asset.get('volumeUsd24Hr', 0)),
                    "last_updated": datetime.now().isoformat(),
                    "source": "coincap_search",
                    "status": "success"
                }
    except Exception:
        return None

def _fetch_from_alternative(coin_id: str) -> Optional[Dict[str, Any]]:
    """Try alternative crypto APIs"""
    try:
        # Try Binance API for major coins
        symbol_map = {
            'bitcoin': 'BTCUSDT',
            'btc': 'BTCUSDT',
            'ethereum': 'ETHUSDT',
            'eth': 'ETHUSDT',
            'binancecoin': 'BNBUSDT',
            'bnb': 'BNBUSDT',
            'solana': 'SOLUSDT',
            'sol': 'SOLUSDT',
            'cardano': 'ADAUSDT',
            'ada': 'ADAUSDT',
            'dogecoin': 'DOGEUSDT',
            'doge': 'DOGEUSDT',
            'polkadot': 'DOTUSDT',
            'dot': 'DOTUSDT',
            'ripple': 'XRPUSDT',
            'xrp': 'XRPUSDT',
            'chainlink': 'LINKUSDT',
            'link': 'LINKUSDT',
            'litecoin': 'LTCUSDT',
            'ltc': 'LTCUSDT',
            'matic-network': 'MATICUSDT',
            'matic': 'MATICUSDT',
            'avalanche-2': 'AVAXUSDT',
            'avax': 'AVAXUSDT',
        }
        
        symbol = symbol_map.get(coin_id)
        if symbol:
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "id": coin_id,
                    "name": coin_id.upper(),
                    "symbol": symbol.replace('USDT', ''),
                    "current_price": float(data.get('lastPrice', 0)),
                    "price_change_24h": float(data.get('priceChange', 0)),
                    "price_change_percentage_24h": float(data.get('priceChangePercent', 0)),
                    "high_24h": float(data.get('highPrice', 0)),
                    "low_24h": float(data.get('lowPrice', 0)),
                    "total_volume": float(data.get('volume', 0)),
                    "last_updated": datetime.now().isoformat(),
                    "source": "binance",
                    "status": "success"
                }
    except Exception:
        pass
    
    return None

# -----------------------------------------------------------
#  ENHANCED STOCK DATA FETCHER WITH REAL-TIME VERIFICATION
# -----------------------------------------------------------

def get_stock_data(ticker: str, verify: bool = True) -> Dict[str, Any]:
    """
    Enhanced stock data fetcher with real-time verification
    Uses multiple methods to get the most accurate real-time price
    """
    cache_key = f"stock_{ticker.upper()}"
    cached = CacheManager.get(cache_key)
    if cached:
        return cached
    
    try:
        ticker = ticker.upper()
        
        # Check if it's a known crypto symbol (not a stock)
        known_crypto_symbols = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'DOGE', 'SHIB', 'LINK', 
                               'LTC', 'XRP', 'MATIC', 'AVAX', 'ATOM', 'UNI', 'AAVE', 'COMP',
                               'MKR', 'SNX', 'YFI', 'CRV', 'SUSHI', '1INCH', 'GRT', 'BAT',
                               'ENJ', 'MANA', 'SAND', 'AXS', 'LUNA', 'XTZ', 'EOS', 'TRX',
                               'NEO', 'WAVES', 'QTUM', 'ICX', 'ZIL', 'ONT', 'VET', 'FIL',
                               'XLM', 'XMR', 'ZEC', 'DASH', 'ETC', 'ALGO', 'HBAR', 'NEAR',
                               'FTM', 'ONE', 'RUNE', 'CAKE']
        
        if ticker in known_crypto_symbols:
            # This is a cryptocurrency, not a stock
            return {"error": f"{ticker} is a cryptocurrency symbol, not a stock", "status": "error"}
        
        stock = yf.Ticker(ticker)
        
        # Get stock info first
        info = stock.info
        if not info:
            return {"error": "No data available for this ticker", "status": "error"}
        
        # METHOD 1: Try to get real-time quote from Yahoo Finance
        real_time_price = None
        price_source = 'yfinance_info'
        
        # Check for real-time data in info
        if info.get('regularMarketPrice') is not None:
            real_time_price = info.get('regularMarketPrice')
            price_source = 'regularMarketPrice'
        elif info.get('currentPrice') is not None:
            real_time_price = info.get('currentPrice')
            price_source = 'currentPrice'
        elif info.get('ask') is not None and info.get('bid') is not None:
            # Calculate mid-price from bid/ask
            real_time_price = (info.get('ask') + info.get('bid')) / 2
            price_source = 'bid_ask_mid'
        
        # METHOD 2: Try to get 1m interval data for real-time
        if real_time_price is None:
            try:
                # Get very recent data with 1m interval
                hist_1m = stock.history(period='1d', interval='1m')
                if not hist_1m.empty:
                    latest = hist_1m.iloc[-1]
                    real_time_price = float(latest['Close'])
                    price_source = 'history_1m'
            except Exception as e:
                print(f"1m interval failed: {e}")
        
        # METHOD 3: Try to get 5m interval data
        if real_time_price is None:
            try:
                hist_5m = stock.history(period='1d', interval='5m')
                if not hist_5m.empty:
                    latest = hist_5m.iloc[-1]
                    real_time_price = float(latest['Close'])
                    price_source = 'history_5m'
            except Exception:
                pass
        
        # METHOD 4: Fallback to daily data
        if real_time_price is None:
            try:
                hist_1d = stock.history(period='2d', interval='1d')
                if not hist_1d.empty:
                    latest = hist_1d.iloc[-1]
                    real_time_price = float(latest['Close'])
                    price_source = 'history_1d'
            except Exception:
                pass
        
        # If still no price, return error
        if real_time_price is None:
            return {"error": "Unable to fetch price data", "status": "error"}
        
        # Calculate day change
        previous_close = info.get('regularMarketPreviousClose')
        if previous_close is None:
            # Try to get from history
            try:
                hist_2d = stock.history(period='2d')
                if len(hist_2d) >= 2:
                    previous_close = float(hist_2d['Close'].iloc[-2])
            except:
                previous_close = real_time_price
        
        day_change = real_time_price - previous_close if previous_close else 0
        day_change_pct = (day_change / previous_close * 100) if previous_close and previous_close != 0 else 0
        
        # Get today's OHLC from real-time data if available
        try:
            # Try to get today's data
            today = datetime.now().date()
            hist_today = stock.history(start=today, interval='1m')
            if not hist_today.empty:
                today_open = float(hist_today['Open'].iloc[0])
                today_high = float(hist_today['High'].max())
                today_low = float(hist_today['Low'].min())
                today_volume = int(hist_today['Volume'].sum())
            else:
                # Use info data
                today_open = info.get('regularMarketOpen', real_time_price)
                today_high = info.get('regularMarketDayHigh', real_time_price)
                today_low = info.get('regularMarketDayLow', real_time_price)
                today_volume = info.get('regularMarketVolume', 0)
        except:
            today_open = info.get('regularMarketOpen', real_time_price)
            today_high = info.get('regularMarketDayHigh', real_time_price)
            today_low = info.get('regularMarketDayLow', real_time_price)
            today_volume = info.get('regularMarketVolume', 0)
        
        # Prepare result
        result = {
            "ticker": ticker,
            "name": info.get('longName', info.get('shortName', ticker)),
            "current_price": round(real_time_price, 2),
            "previous_close": round(previous_close, 2) if previous_close else None,
            "day_change": round(day_change, 2),
            "day_change_pct": round(day_change_pct, 2),
            "open": round(today_open, 2) if today_open else None,
            "high": round(today_high, 2) if today_high else None,
            "low": round(today_low, 2) if today_low else None,
            "volume": today_volume,
            "market_cap": info.get('marketCap'),
            "pe_ratio": info.get('trailingPE'),
            "dividend_yield": info.get('dividendYield'),
            "price_source": price_source,
            "last_updated": datetime.now().isoformat(),
            "status": "success"
        }
        
        # Add verification if requested
        if verify and price_source != 'bid_ask_mid':
            # Try to get bid/ask for verification
            bid = info.get('bid')
            ask = info.get('ask')
            if bid and ask:
                mid_price = (bid + ask) / 2
                price_diff = abs(real_time_price - mid_price) / real_time_price * 100
                if price_diff < 0.5:  # Less than 0.5% difference
                    result['price_verified'] = True
                    result['verification_diff'] = f"{price_diff:.2f}%"
                    result['bid'] = bid
                    result['ask'] = ask
        
        # Cache the result
        CacheManager.set(cache_key, result, 'stock')
        return result
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

# -----------------------------------------------------------
#  ENHANCED SEARCH FUNCTION WITH SMART DETECTION
# -----------------------------------------------------------

def search_asset(query: str) -> Dict[str, Any]:
    """
    Enhanced search with smart detection and confidence scoring
    """
    query = query.strip().lower()
    cache_key = f"search_{query}"
    cached = CacheManager.get(cache_key)
    if cached:
        return cached
    
    # Known cryptocurrency symbols (uppercase)
    known_crypto_symbols = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'SOL': 'solana',
        'ADA': 'cardano',
        'DOT': 'polkadot',
        'DOGE': 'dogecoin',
        'SHIB': 'shiba-inu',
        'LINK': 'chainlink',
        'LTC': 'litecoin',
        'XRP': 'ripple',
        'MATIC': 'matic-network',
        'AVAX': 'avalanche-2',
        'ATOM': 'cosmos',
        'UNI': 'uniswap',
        'AAVE': 'aave',
        'COMP': 'compound',
        'MKR': 'maker',
        'SNX': 'synthetix',
        'YFI': 'yearn-finance',
        'CRV': 'curve-dao-token',
        'SUSHI': 'sushi',
        '1INCH': '1inch',
        'GRT': 'the-graph',
        'BAT': 'basic-attention-token',
        'ENJ': 'enjincoin',
        'MANA': 'decentraland',
        'SAND': 'the-sandbox',
        'AXS': 'axie-infinity',
        'LUNA': 'terra-luna',
        'XTZ': 'tezos',
        'EOS': 'eos',
        'TRX': 'tron',
        'NEO': 'neo',
        'WAVES': 'waves',
        'QTUM': 'qtum',
        'ICX': 'icon',
        'ZIL': 'zilliqa',
        'ONT': 'ontology',
        'VET': 'vechain',
        'FIL': 'filecoin',
        'XLM': 'stellar',
        'XMR': 'monero',
        'ZEC': 'zcash',
        'DASH': 'dash',
        'ETC': 'ethereum-classic',
        'ALGO': 'algorand',
        'HBAR': 'hedera-hashgraph',
        'NEAR': 'near',
        'FTM': 'fantom',
        'ONE': 'harmony',
        'RUNE': 'thorchain',
        'CAKE': 'pancakeswap-token',
        'BNB': 'binancecoin',
        'BCH': 'bitcoin-cash',
        'XEM': 'nem',
        'MIOTA': 'iota',
        'XTZ': 'tezos',
        'EGLD': 'elrond-erd-2',
        'ICP': 'internet-computer',
        'VET': 'vechain',
        'THETA': 'theta-token',
        'EOS': 'eos',
        'MKR': 'maker',
        'CRO': 'crypto-com-chain',
        'BSV': 'bitcoin-cash-sv',
        'KLAY': 'klay-token',
        'LEO': 'leo-token',
        'NEXO': 'nexo',
        'CHZ': 'chiliz',
        'HOT': 'holotoken',
        'BTT': 'bittorrent',
        'ZEC': 'zcash',
        'DCR': 'decred',
        'DGB': 'digibyte',
        'SC': 'siacoin',
        'BTG': 'bitcoin-gold',
        'RVN': 'ravencoin',
        'NANO': 'nano',
        'ZEN': 'zencash',
        'WAVES': 'waves',
        'ONT': 'ontology',
        'ICX': 'icon',
        'IOST': 'iostoken',
        'STEEM': 'steem',
        'AR': 'arweave',
        'CELO': 'celo',
        'QTUM': 'qtum',
        'BTS': 'bitshares',
        'LSK': 'lisk',
        'NXT': 'nxt',
        'STRAT': 'stratis',
        'WAN': 'wanchain',
        'AION': 'aion',
        'KMD': 'komodo',
        'REP': 'augur',
        'GNO': 'gnosis',
        'POWR': 'power-ledger',
        'FUN': 'funfair',
        'SNT': 'status',
        'KNC': 'kyber-network',
        'BAND': 'band-protocol',
        'UMA': 'uma',
        'REN': 'republic-protocol',
        'LOOM': 'loom-network',
        'POLY': 'polymath',
        'REQ': 'request-network',
        'CVC': 'civic',
        'STORJ': 'storj',
        'DATA': 'streamr-datacoin',
        'MAN': 'matrix-ai-network',
        'WTC': 'waltonchain',
        'ITC': 'iot-chain',
        'RUFF': 'ruff',
        'AE': 'aeternity',
        'AGI': 'singularitynet',
        'WINGS': 'wings',
        'MTL': 'metal',
        'SAN': 'santiment',
        'EVX': 'everex',
        'PPT': 'populous',
        'RLC': 'iexec-rlc',
        'GXS': 'gxchain',
        'NAS': 'nebulas-token',
        'MCO': 'crypto-com',
        'ENG': 'enigma',
        'SNGLS': 'singulardtv',
        'ANT': 'aragon',
        'BAT': 'basic-attention-token',
        'BNT': 'bancor',
        'CVC': 'civic',
        'DNT': 'district0x',
        'FUN': 'funfair',
        'GNO': 'gnosis',
        'GNT': 'golem',
        'ICN': 'iconomi',
        'MLN': 'melon',
        'NMR': 'numeraire',
        'OAX': 'openanx',
        'OMG': 'omisego',
        'PAY': 'tenx',
        'RCN': 'ripio-credit-network',
        'REP': 'augur',
        'RLC': 'iexec-rlc',
        'SNT': 'status',
        'STORJ': 'storj',
        'TKN': 'tokencard',
        'TRST': 'wetrust',
        'WINGS': 'wings',
        'ZRX': '0x'
    }
    
    # Common crypto names (lowercase)
    common_crypto_names = {
        'bitcoin': 'bitcoin',
        'ethereum': 'ethereum',
        'solana': 'solana',
        'cardano': 'cardano',
        'polkadot': 'polkadot',
        'dogecoin': 'dogecoin',
        'shiba inu': 'shiba-inu',
        'shibainu': 'shiba-inu',
        'shiba': 'shiba-inu',
        'chainlink': 'chainlink',
        'litecoin': 'litecoin',
        'ripple': 'ripple',
        'polygon': 'matic-network',
        'avalanche': 'avalanche-2',
        'cosmos': 'cosmos',
        'uniswap': 'uniswap',
        'aave': 'aave',
        'compound': 'compound',
        'maker': 'maker',
        'synthetix': 'synthetix',
        'yearn finance': 'yearn-finance',
        'curve': 'curve-dao-token',
        'sushiswap': 'sushi',
        '1inch': '1inch',
        'the graph': 'the-graph',
        'basic attention token': 'basic-attention-token',
        'enjin coin': 'enjincoin',
        'decentraland': 'decentraland',
        'the sandbox': 'the-sandbox',
        'axie infinity': 'axie-infinity',
        'terra': 'terra-luna',
        'tezos': 'tezos',
        'eos': 'eos',
        'tron': 'tron',
        'neo': 'neo',
        'waves': 'waves',
        'qtum': 'qtum',
        'icon': 'icon',
        'zilliqa': 'zilliqa',
        'ontology': 'ontology',
        'vechain': 'vechain',
        'filecoin': 'filecoin',
        'stellar': 'stellar',
        'monero': 'monero',
        'zcash': 'zcash',
        'dash': 'dash',
        'ethereum classic': 'ethereum-classic',
        'algorand': 'algorand',
        'hedera': 'hedera-hashgraph',
        'near': 'near',
        'fantom': 'fantom',
        'harmony': 'harmony',
        'thorchain': 'thorchain',
        'pancakeswap': 'pancakeswap-token',
        'binance coin': 'binancecoin',
        'bitcoin cash': 'bitcoin-cash',
        'nem': 'nem',
        'iota': 'iota',
        'elrond': 'elrond-erd-2',
        'internet computer': 'internet-computer',
        'theta': 'theta-token',
        'crypto.com coin': 'crypto-com-chain',
        'bitcoin sv': 'bitcoin-cash-sv',
        'klaytn': 'klay-token',
        'leo token': 'leo-token',
        'nexo': 'nexo',
        'chiliz': 'chiliz',
        'holo': 'holotoken',
        'bittorrent': 'bittorrent',
        'decred': 'decred',
        'digibyte': 'digibyte',
        'siacoin': 'siacoin',
        'bitcoin gold': 'bitcoin-gold',
        'ravencoin': 'ravencoin',
        'nano': 'nano',
        'zencash': 'zencash',
        'arweave': 'arweave',
        'celo': 'celo',
        'bitshares': 'bitshares',
        'lisk': 'lisk',
        'nxt': 'nxt',
        'stratis': 'stratis',
        'wanchain': 'wanchain',
        'aion': 'aion',
        'komodo': 'komodo',
        'augur': 'augur',
        'gnosis': 'gnosis',
        'power ledger': 'power-ledger',
        'funfair': 'funfair',
        'status': 'status',
        'kyber network': 'kyber-network',
        'band protocol': 'band-protocol',
        'uma': 'uma',
        'republic protocol': 'republic-protocol',
        'loom network': 'loom-network',
        'polymath': 'polymath',
        'request network': 'request-network',
        'civic': 'civic',
        'storj': 'storj',
        'streamr': 'streamr-datacoin',
        'matrix ai network': 'matrix-ai-network',
        'waltonchain': 'waltonchain',
        'iot chain': 'iot-chain',
        'ruff': 'ruff',
        'aeternity': 'aeternity',
        'singularitynet': 'singularitynet',
        'wings': 'wings',
        'metal': 'metal',
        'santiment': 'santiment',
        'everex': 'everex',
        'populous': 'populous',
        'iexec rlc': 'iexec-rlc',
        'gxchain': 'gxchain',
        'nebulas': 'nebulas-token',
        'crypto.com': 'crypto-com',
        'enigma': 'enigma',
        'singulardtv': 'singulardtv',
        'aragon': 'aragon',
        'bancor': 'bancor',
        'district0x': 'district0x',
        'golem': 'golem',
        'iconomi': 'iconomi',
        'melon': 'melon',
        'numeraire': 'numeraire',
        'openanx': 'openanx',
        'omisego': 'omisego',
        'tenx': 'tenx',
        'ripio credit network': 'ripio-credit-network',
        'tokencard': 'tokencard',
        'wetrust': 'wetrust',
        '0x': '0x'
    }
    
    # STEP 1: Check if query is a known cryptocurrency symbol (uppercase)
    query_upper = query.upper()
    if query_upper in known_crypto_symbols:
        coin_id = known_crypto_symbols[query_upper]
        crypto_data = get_crypto_data(coin_id)
        
        if "error" not in crypto_data and crypto_data.get("status") in ["success", "success_simple", "success_fallback"]:
            result = {
                "type": "crypto",
                "data": crypto_data,
                "confidence": 0.95,
                "detected_as": "crypto_symbol",
                "query": query
            }
            CacheManager.set(cache_key, result, 'search')
            return result
    
    # STEP 2: Check if query is a common cryptocurrency name
    if query in common_crypto_names:
        coin_id = common_crypto_names[query]
        crypto_data = get_crypto_data(coin_id)
        
        if "error" not in crypto_data and crypto_data.get("status") in ["success", "success_simple", "success_fallback"]:
            result = {
                "type": "crypto",
                "data": crypto_data,
                "confidence": 0.9,
                "detected_as": "crypto_name",
                "query": query
            }
            CacheManager.set(cache_key, result, 'search')
            return result
    
    # STEP 3: Try as cryptocurrency (direct CoinGecko ID)
    crypto_data = get_crypto_data(query)
    if "error" not in crypto_data and crypto_data.get("status") in ["success", "success_simple", "success_fallback"]:
        result = {
            "type": "crypto",
            "data": crypto_data,
            "confidence": 0.8,
            "detected_as": "crypto_id",
            "query": query
        }
        CacheManager.set(cache_key, result, 'search')
        return result
    
    # STEP 4: Only try as stock if it's not a known crypto symbol and looks like a stock
    # Check if it looks like a stock ticker (1-5 letters, uppercase convention)
    looks_like_stock = (
        len(query) <= 5 and 
        query.isalpha() and 
        query_upper not in known_crypto_symbols and
        query not in common_crypto_names
    )
    
    if looks_like_stock:
        stock_data = get_stock_data(query.upper())
        if "error" not in stock_data and stock_data.get("status") == "success":
            result = {
                "type": "stock",
                "data": stock_data,
                "confidence": 0.85,
                "detected_as": "stock_ticker",
                "query": query
            }
            CacheManager.set(cache_key, result, 'search')
            return result
    
    # STEP 5: Try CoinGecko search API for fuzzy matching
    try:
        # Clean query for searching
        clean_query = query.replace(' ', '-').lower()
        
        # Try CoinGecko search
        search_url = f"https://api.coingecko.com/api/v3/search?query={clean_query}"
        search_response = requests.get(search_url, timeout=10)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            coins = search_data.get('coins', [])
            
            if coins:
                # Try the first match
                matched_coin = coins[0]
                coin_id = matched_coin.get('id')
                
                if coin_id:
                    crypto_data = get_crypto_data(coin_id)
                    if "error" not in crypto_data and crypto_data.get("status") in ["success", "success_simple", "success_fallback"]:
                        result = {
                            "type": "crypto",
                            "data": crypto_data,
                            "confidence": 0.7,
                            "detected_as": "search_api_match",
                            "query": query,
                            "matched_name": matched_coin.get('name', '')
                        }
                        CacheManager.set(cache_key, result, 'search')
                        return result
    except Exception:
        pass  # Search API failed
    
    # STEP 6: Not found
    suggestions = []
    
    # Check if it's likely a crypto symbol
    if query_upper in known_crypto_symbols or query in common_crypto_names:
        suggestions.append(f"'{query}' is a cryptocurrency. Try searching for '{known_crypto_symbols.get(query_upper, common_crypto_names.get(query, query))}'")
    elif len(query) <= 5 and query.isalpha():
        suggestions.append(f"'{query.upper()}' could be a stock ticker - make sure it's valid (e.g., AAPL, TSLA)")
        suggestions.append(f"'{query.upper()}' could also be a crypto symbol - try full name (e.g., bitcoin, ethereum)")
    else:
        suggestions.append(f"'{query}' might be misspelled or not available")
    
    suggestions.append("For cryptocurrencies: Use full names like 'bitcoin', 'ethereum', 'solana'")
    suggestions.append("For stocks: Use ticker symbols like 'AAPL', 'TSLA', 'GOOGL'")
    suggestions.append("Common crypto symbols: 'BTC', 'ETH', 'SOL', 'DOGE', 'SHIB'")
    
    result = {
        "error": f"'{query}' not found as cryptocurrency or stock",
        "suggestions": suggestions,
        "confidence": 0.0
    }
    CacheManager.set(cache_key, result, 'search')
    return result

# -----------------------------------------------------------
#  COMPATIBILITY FUNCTIONS (ENHANCED)
# -----------------------------------------------------------

def get_crypto_price(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Enhanced backward compatibility function
    Returns price with more data
    """
    data = get_crypto_data(symbol.lower())
    if "error" in data:
        return None
    
    return {
        'price': data.get('current_price', 0),
        'high_24h': data.get('high_24h', data.get('current_price', 0) * 1.05),
        'low_24h': data.get('low_24h', data.get('current_price', 0) * 0.95),
        'volume_24h': data.get('total_volume', 0),
        'market_cap': data.get('market_cap', 0),
        'price_change_24h': data.get('price_change_24h', 0),
        'price_change_percentage_24h': data.get('price_change_percentage_24h', 0),
        'name': data.get('name', symbol.upper()),
        'symbol': data.get('symbol', symbol.upper()),
        'last_updated': data.get('last_updated', datetime.now().isoformat())
    }

def get_stock_price(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Enhanced backward compatibility function
    Returns price with more data
    """
    data = get_stock_data(symbol.upper())
    if "error" in data:
        return None
    
    return {
        'price': data.get('current_price', 0),
        'high': data.get('high', data.get('current_price', 0) * 1.05),
        'low': data.get('low', data.get('current_price', 0) * 0.95),
        'volume': data.get('volume', 0),
        'market_cap': data.get('market_cap', 0),
        'change': data.get('day_change', 0),
        'change_percent': data.get('day_change_pct', 0),
        'open': data.get('open', data.get('current_price', 0)),
        'previous_close': data.get('previous_close', data.get('current_price', 0)),
        'name': data.get('name', symbol.upper()),
        'ticker': data.get('ticker', symbol.upper()),
        'last_updated': data.get('last_updated', datetime.now().isoformat())
    }

# -----------------------------------------------------------
#  NEW: MULTI-SOURCE PRICE FETCHER
# -----------------------------------------------------------

def get_multi_source_price(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Try multiple sources to get the most accurate price
    """
    # Clean the cache first
    CacheManager.clean_old_entries()
    
    results = []
    
    # Try as crypto
    crypto_data = get_crypto_data(symbol.lower())
    if "error" not in crypto_data and crypto_data.get("status") in ["success", "success_simple", "success_fallback"]:
        results.append({
            'type': 'crypto',
            'price': crypto_data.get('current_price', 0),
            'source': crypto_data.get('source', 'unknown'),
            'confidence': 0.9 if crypto_data.get('verified_with') else 0.7,
            'data': crypto_data
        })
    
    # Try as stock (only if not a known crypto symbol)
    known_crypto_symbols = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'DOGE', 'SHIB', 'LINK', 'LTC', 'XRP']
    if symbol.upper() not in known_crypto_symbols:
        stock_data = get_stock_data(symbol.upper())
        if "error" not in stock_data and stock_data.get("status") in ["success", "success_info_only"]:
            results.append({
                'type': 'stock',
                'price': stock_data.get('current_price', 0),
                'source': stock_data.get('price_source', 'unknown'),
                'confidence': 0.9 if stock_data.get('price_verified') else 0.7,
                'data': stock_data
            })
    
    if not results:
        return None
    
    # Sort by confidence and return the best
    results.sort(key=lambda x: x['confidence'], reverse=True)
    best_result = results[0]
    
    # Prepare result in the expected format
    if best_result['type'] == 'crypto':
        data = best_result['data']
        return {
            'type': 'crypto',
            'price': data.get('current_price', 0),
            'high_24h': data.get('high_24h', 0),
            'low_24h': data.get('low_24h', 0),
            'volume_24h': data.get('total_volume', 0),
            'market_cap': data.get('market_cap', 0),
            'name': data.get('name', symbol.upper()),
            'symbol': data.get('symbol', symbol.upper()),
            'source': data.get('source', 'multiple'),
            'verified': 'verified_with' in data or 'price_verified' in data
        }
    else:
        data = best_result['data']
        return {
            'type': 'stock',
            'price': data.get('current_price', 0),
            'high': data.get('high', 0),
            'low': data.get('low', 0),
            'volume': data.get('volume', 0),
            'market_cap': data.get('market_cap', 0),
            'name': data.get('name', symbol.upper()),
            'ticker': data.get('ticker', symbol.upper()),
            'source': data.get('price_source', 'multiple'),
            'verified': data.get('price_verified', False)
        }

# -----------------------------------------------------------
#  ENHANCED BATCH FUNCTIONS
# -----------------------------------------------------------

def get_multiple_crypto_data(coin_list: List[str]) -> Dict[str, Any]:
    """Fetch multiple cryptos with parallel requests"""
    results = {}
    for coin in coin_list:
        results[coin] = get_crypto_data(coin)
    return results

def get_multiple_stock_data(ticker_list: List[str]) -> Dict[str, Any]:
    """Fetch multiple stocks"""
    results = {}
    for ticker in ticker_list:
        results[ticker] = get_stock_data(ticker)
    return results

# -----------------------------------------------------------
#  NEW: PRICE VERIFICATION UTILITY
# -----------------------------------------------------------

def verify_price(symbol: str, expected_type: str = None) -> Dict[str, Any]:
    """
    Verify price from multiple sources and return consistency report
    """
    sources = []
    
    if expected_type is None or expected_type == 'crypto':
        # Try crypto sources
        crypto_sources = [
            ('coingecko', lambda: _fetch_from_coingecko(symbol.lower())),
            ('coincap', lambda: _fetch_from_coincap(symbol.lower())),
            ('alternative', lambda: _fetch_from_alternative(symbol.lower()))
        ]
        
        for source_name, fetch_func in crypto_sources:
            try:
                data = fetch_func()
                if data and data.get('status') == 'success':
                    sources.append({
                        'type': 'crypto',
                        'source': source_name,
                        'price': data.get('current_price'),
                        'timestamp': data.get('last_updated')
                    })
            except:
                pass
    
    if expected_type is None or expected_type == 'stock':
        # Try stock (only if not a known crypto)
        known_crypto_symbols = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'DOGE', 'SHIB']
        if symbol.upper() not in known_crypto_symbols:
            try:
                stock = yf.Ticker(symbol.upper())
                info = stock.info
                if info.get('regularMarketPrice'):
                    sources.append({
                        'type': 'stock',
                        'source': 'yfinance',
                        'price': info.get('regularMarketPrice'),
                        'timestamp': datetime.now().isoformat()
                    })
            except:
                pass
    
    if not sources:
        return {
            'verified': False,
            'error': 'No sources available',
            'sources': []
        }
    
    # Calculate consistency
    prices = [s['price'] for s in sources if s['price'] is not None]
    if len(prices) >= 2:
        avg_price = sum(prices) / len(prices)
        max_diff = max(abs(p - avg_price) for p in prices)
        diff_percent = (max_diff / avg_price * 100) if avg_price > 0 else 0
        
        if diff_percent < 1:
            consistency = 'high'
        elif diff_percent < 3:
            consistency = 'medium'
        else:
            consistency = 'low'
    else:
        consistency = 'single_source'
        avg_price = prices[0] if prices else 0
        diff_percent = 0
    
    return {
        'verified': len(sources) > 1,
        'consistency': consistency,
        'price_discrepancy_percent': diff_percent,
        'average_price': avg_price,
        'sources_count': len(sources),
        'sources': sources
    }

# -----------------------------------------------------------
#  NEW: REAL-TIME QUOTE FETCHER USING ALPHA VANTAGE FALLBACK
# -----------------------------------------------------------

def get_realtime_stock_quote(ticker: str, api_key: str = None) -> Optional[Dict[str, Any]]:
    """
    Get real-time stock quote using Alpha Vantage as fallback if available
    Requires Alpha Vantage API key (optional)
    """
    ticker = ticker.upper()
    
    # First try yfinance
    try:
        stock_data = get_stock_data(ticker)
        if "error" not in stock_data:
            return stock_data
    except:
        pass
    
    # Fallback to Alpha Vantage if API key is provided
    if api_key:
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': ticker,
                'apikey': api_key
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'Global Quote' in data:
                    quote = data['Global Quote']
                    return {
                        "ticker": ticker,
                        "current_price": float(quote.get('05. price', 0)),
                        "day_change": float(quote.get('09. change', 0)),
                        "day_change_pct": float(quote.get('10. change percent', '0').replace('%', '')),
                        "high": float(quote.get('03. high', 0)),
                        "low": float(quote.get('04. low', 0)),
                        "open": float(quote.get('02. open', 0)),
                        "previous_close": float(quote.get('08. previous close', 0)),
                        "volume": int(quote.get('06. volume', 0)),
                        "source": "alphavantage",
                        "last_updated": datetime.now().isoformat(),
                        "status": "success"
                    }
        except Exception as e:
            print(f"Alpha Vantage error: {e}")
    
    return None

# -----------------------------------------------------------
#  INITIAL CACHE CLEANUP THREAD
# -----------------------------------------------------------

def start_cache_cleanup():
    """Start background thread for cache cleanup"""
    def cleanup_loop():
        while True:
            time.sleep(300)  # Clean every 5 minutes
            CacheManager.clean_old_entries()
    
    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()

# Start cleanup thread on import
start_cache_cleanup()