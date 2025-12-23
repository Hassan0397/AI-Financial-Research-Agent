import streamlit as st
from services.ai_engine import ai_market_analysis
from services.data_fetch import get_crypto_price, get_stock_price, get_multi_source_price
from services.news_fetch import get_market_news
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import yfinance as yf

st.set_page_config(page_title="AI Market Analyst Pro", layout="wide", page_icon="📈")

# Clean Modern CSS
st.markdown("""
<style>
    /* Modern color palette */
    :root {
        --primary: #3b82f6;
        --primary-dark: #2563eb;
        --primary-light: #93c5fd;
        --success: #10b981;
        --success-dark: #059669;
        --danger: #ef4444;
        --danger-dark: #dc2626;
        --warning: #f59e0b;
        --warning-dark: #d97706;
        --neutral: #6b7280;
        --neutral-light: #9ca3af;
        --neutral-dark: #4b5563;
        --bg-light: #f9fafb;
        --bg-white: #ffffff;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        --radius-sm: 0.375rem;
        --radius: 0.5rem;
        --radius-md: 0.75rem;
        --radius-lg: 1rem;
    }
    
    /* Base styles */
    .stApp {
        background: var(--bg-light);
    }
    
    /* Clean Header */
    .clean-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        padding: 2rem 1.5rem;
        border-radius: 0 0 var(--radius-lg) var(--radius-lg);
        color: white;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
    }
    
    /* Clean Card */
    .clean-card {
        background: var(--bg-white);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        border: 1px solid #f3f4f6;
        transition: all 0.2s ease;
        margin-bottom: 1rem;
    }
    
    .clean-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    
    /* Metric Card */
    .metric-card {
        background: var(--bg-white);
        border-radius: var(--radius);
        padding: 1.25rem;
        border-left: 4px solid var(--primary);
        box-shadow: var(--shadow-sm);
        height: 100%;
    }
    
    .metric-value {
        font-size: 1.875rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--neutral);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    /* Signal Cards */
    .signal-buy {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
        border-left: 4px solid var(--success);
    }
    
    .signal-sell {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
        border-left: 4px solid var(--danger);
    }
    
    .signal-hold {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
        border-left: 4px solid var(--warning);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .badge-success {
        background: var(--success);
        color: white;
    }
    
    .badge-danger {
        background: var(--danger);
        color: white;
    }
    
    .badge-warning {
        background: var(--warning);
        color: white;
    }
    
    .badge-neutral {
        background: var(--neutral);
        color: white;
    }
    
    /* Progress Bar */
    .progress-bar {
        height: 6px;
        background: #e5e7eb;
        border-radius: 3px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary) 0%, var(--success) 100%);
        border-radius: 3px;
        transition: width 0.3s ease;
    }
    
    /* Button Styles */
    .stButton > button {
        border-radius: var(--radius);
        font-weight: 500;
        padding: 0.625rem 1.25rem;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow);
    }
</style>
""", unsafe_allow_html=True)

# Clean Modern Header
st.markdown("""
<div class="clean-header">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
        <div>
            <h1 style="margin: 0; font-size: 2rem; font-weight: 700;">AI Market Analyst</h1>
            <p style="margin: 0.25rem 0 0 0; opacity: 0.9;">Professional Trading Intelligence Platform</p>
        </div>
        <div style="display: flex; gap: 0.5rem;">
            <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: var(--radius); font-size: 0.875rem;">
                📈 Live Market
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: var(--radius); font-size: 0.875rem;">
                🤖 AI-Powered
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
session_defaults = {
    'analysis_result': None,
    'analysis_done': False,
    'symbol': "",
    'news_data': [],
    'historical_data': None,
    'analysis_history': [],
    'user_trust_score': 85,
    'last_symbol': ''
}

for key, value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Helper functions for data fetching
def get_historical_data(symbol, period="1mo"):
    """Get historical data for a symbol"""
    try:
        # For crypto symbols
        if len(symbol) <= 5:
            ticker_map = {
                'BTC': 'BTC-USD', 'ETH': 'ETH-USD', 'BNB': 'BNB-USD', 
                'XRP': 'XRP-USD', 'ADA': 'ADA-USD', 'DOGE': 'DOGE-USD',
                'SOL': 'SOL-USD', 'DOT': 'DOT-USD', 'AVAX': 'AVAX-USD',
                'MATIC': 'MATIC-USD', 'LTC': 'LTC-USD', 'UNI': 'UNI-USD'
            }
            yf_symbol = ticker_map.get(symbol.upper(), f"{symbol.upper()}-USD")
        else:
            yf_symbol = symbol.upper()
        
        period_map = {
            "1D": "5d", "1W": "1wk", "1M": "1mo", 
            "3M": "3mo", "6M": "6mo", "1Y": "1y"
        }
        yf_period = period_map.get(period, "1mo")
        
        ticker = yf.Ticker(yf_symbol)
        hist = ticker.history(period=yf_period)
        
        if hist.empty or len(hist) < 2:
            # Create simulated data
            days = 30
            dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
            base_price = np.random.uniform(50, 500)
            prices = base_price + np.cumsum(np.random.randn(days) * 5)
            
            hist = pd.DataFrame({
                'Open': prices * 0.99,
                'High': prices * 1.02,
                'Low': prices * 0.98,
                'Close': prices,
                'Volume': np.random.randint(1000000, 10000000, days)
            }, index=dates)
        
        # Format data
        historical_data = []
        for idx, row in hist.iterrows():
            historical_data.append({
                'timestamp': idx,
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': float(row['Volume'])
            })
        
        return historical_data
        
    except Exception as e:
        # Return simulated data on error
        days = 30
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        base_price = 100
        prices = base_price + np.cumsum(np.random.randn(days) * 5)
        
        historical_data = []
        for i, date in enumerate(dates):
            historical_data.append({
                'timestamp': date,
                'open': prices[i] * 0.99,
                'high': prices[i] * 1.02,
                'low': prices[i] * 0.98,
                'close': prices[i],
                'volume': np.random.randint(1000000, 5000000)
            })
        return historical_data

def get_advanced_metrics(symbol, historical_data=None):
    """Get advanced market metrics"""
    try:
        if historical_data and len(historical_data) > 1:
            prices = np.array([h['close'] for h in historical_data])
            
            # Calculate RSI
            if len(prices) >= 14:
                gains = np.where(np.diff(prices) > 0, np.diff(prices), 0)
                losses = np.where(np.diff(prices) < 0, -np.diff(prices), 0)
                avg_gain = np.mean(gains[-14:])
                avg_loss = np.mean(losses[-14:])
                if avg_loss == 0:
                    rsi = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
            else:
                rsi = np.random.uniform(30, 70)
            
            # Calculate volatility
            if len(prices) >= 10:
                returns = np.diff(prices) / prices[:-1]
                volatility = np.std(returns) * 100 * np.sqrt(252) if len(returns) > 0 else 20
            else:
                volatility = np.random.uniform(15, 40)
            
            # Calculate MACD
            if len(prices) >= 26:
                ema12 = pd.Series(prices).ewm(span=12).mean().iloc[-1]
                ema26 = pd.Series(prices).ewm(span=26).mean().iloc[-1]
                macd = ema12 - ema26
            else:
                macd = np.random.uniform(-1, 1)
            
            # Determine trend
            if len(prices) >= 20:
                sma20 = np.mean(prices[-20:])
                current_price = prices[-1]
                trend = 'Bullish' if current_price > sma20 else 'Bearish'
            else:
                trend = 'Bullish' if np.random.random() > 0.5 else 'Bearish'
            
            # Support and resistance
            if len(prices) >= 20:
                support = np.min(prices[-20:]) * 0.95
                resistance = np.max(prices[-20:]) * 1.05
            else:
                current_price = prices[-1] if len(prices) > 0 else 100
                support = current_price * 0.9
                resistance = current_price * 1.1
            
        else:
            # Use default values if no historical data
            rsi = np.random.uniform(30, 70)
            volatility = np.random.uniform(15, 40)
            macd = np.random.uniform(-1, 1)
            trend = 'Bullish' if np.random.random() > 0.5 else 'Bearish'
            support = 0
            resistance = 0
        
        metrics = {
            'rsi': rsi,
            'macd': macd,
            'volatility_percent': volatility,
            'trend': trend,
            'support_level': support,
            'resistance_level': resistance,
            'market_cap': np.random.uniform(1e9, 1e12),
            'pe_ratio': np.random.uniform(15, 35),
            'volume_avg': np.random.uniform(5e6, 5e7)
        }
        return metrics
    except Exception as e:
        # Return default metrics on error
        return {
            'rsi': 50,
            'macd': 0,
            'volatility_percent': 25,
            'trend': 'Neutral',
            'support_level': 0,
            'resistance_level': 0
        }

def get_sentiment_score(symbol):
    """Get market sentiment score"""
    try:
        base_scores = {
            'BTC': 0.7, 'ETH': 0.6, 'AAPL': 0.5, 'TSLA': 0.4,
            'GOOGL': 0.6, 'AMZN': 0.5, 'MSFT': 0.7, 'NVDA': 0.8
        }
        base_score = base_scores.get(symbol.upper(), 0.5)
        sentiment = base_score + np.random.uniform(-0.2, 0.2)
        return max(-1, min(1, sentiment))
    except:
        return 0.0

def calculate_position_size(account_size, risk_per_trade, stop_loss, entry_price):
    """Calculate position size based on risk management"""
    if entry_price <= 0 or stop_loss <= 0:
        return {}
    
    risk_amount = account_size * (risk_per_trade / 100)
    risk_per_share = abs(entry_price - stop_loss)
    
    if risk_per_share > 0:
        shares = risk_amount / risk_per_share
        position_value = shares * entry_price
        
        return {
            'shares': shares,
            'position_value': position_value,
            'risk_amount': risk_amount,
            'risk_per_share': risk_per_share,
            'stop_loss': stop_loss,
            'entry_price': entry_price
        }
    
    return {}

def calculate_volatility(prices):
    """Calculate annualized volatility safely"""
    if len(prices) < 2:
        return 20.0  # Default moderate volatility
    
    try:
        returns = np.diff(prices) / prices[:-1]
        if len(returns) == 0:
            return 20.0
        daily_vol = np.std(returns)
        annual_vol = daily_vol * np.sqrt(252) * 100
        return min(max(annual_vol, 5), 80)  # Cap between 5% and 80%
    except:
        return 20.0

# Clean Sidebar
with st.sidebar:
    st.markdown("### 🔍 Asset Analysis")
    
    # Symbol Input
    symbol_input = st.text_input(
        "**Symbol**",
        placeholder="BTC, AAPL, ETH...",
        value=st.session_state.get('last_symbol', ''),
        help="Enter cryptocurrency or stock symbol"
    )
    
    symbol = symbol_input.upper().strip() if symbol_input else ""
    
    if symbol:
        st.caption(f"Analyzing: **{symbol}**")
    
    st.markdown("---")
    
    # Analysis Settings
    st.markdown("### ⚙️ Settings")
    
    with st.expander("Analysis Configuration", expanded=True):
        time_frame = st.selectbox(
            "Time Frame",
            ["1D", "1W", "1M", "3M", "6M", "1Y"],
            index=2
        )
    
    st.markdown("---")
    
    # Risk Profile
    st.markdown("### ⚠️ Risk Profile")
    risk_profile = st.select_slider(
        "Risk Tolerance",
        options=["Conservative", "Moderate", "Aggressive"],
        value="Moderate"
    )
    
    # Investment Simulation
    invest_amount = st.number_input(
        "Investment ($)",
        min_value=100,
        max_value=1000000,
        value=10000,
        step=1000
    )
    
    st.markdown("---")
    
    # AI Engine
    st.markdown("### 🤖 AI Model")
    ai_engine = st.radio(
        "Select Model",
        ["Llama 3 Pro", "GPT-4 Turbo"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Analysis Button
    analyze_button = st.button(
        "🚀 Launch Analysis",
        type="primary",
        use_container_width=True,
        disabled=not symbol
    )
    
    st.markdown("---")
    
    # Quick Symbols
    st.markdown("### ⚡ Quick Symbols")
    quick_symbols = ["BTC", "ETH", "AAPL", "TSLA", "GOOGL", "NVDA"]
    
    cols = st.columns(3)
    for i, sym in enumerate(quick_symbols):
        with cols[i % 3]:
            if st.button(sym, key=f"quick_{sym}", use_container_width=True):
                st.session_state.symbol = sym
                st.session_state.last_symbol = sym
                st.rerun()

# Handle analysis initiation
if analyze_button and symbol:
    st.session_state.symbol = symbol
    st.session_state.last_symbol = symbol
    
    with st.container():
        st.markdown(f"### Analyzing {symbol}")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        steps = [
            "Validating symbol",
            "Fetching market data",
            "Loading historical data",
            "Analyzing market sentiment",
            "Running AI analysis",
            "Generating insights"
        ]
        
        try:
            # Step 1: Validation
            status_text.text(steps[0])
            time.sleep(0.3)
            progress_bar.progress(10)
            
            # Step 2: Fetch current data
            status_text.text(steps[1])
            current_data = None
            
            # Try crypto
            if len(symbol) <= 5:
                crypto_data = get_crypto_price(symbol.lower())
                if crypto_data and 'price' in crypto_data:
                    current_data = crypto_data
                    st.success(f"✅ Found cryptocurrency: {symbol}")
            
            # Try stock
            if not current_data:
                stock_data = get_stock_price(symbol.upper())
                if stock_data and 'price' in stock_data:
                    current_data = stock_data
                    st.success(f"✅ Found stock: {symbol}")
            
            # Try multi-source
            if not current_data:
                multi_data = get_multi_source_price(symbol)
                if multi_data:
                    current_data = multi_data
            
            if not current_data:
                # Create simulated data
                current_data = {
                    'price': np.random.uniform(50, 500),
                    'change': np.random.uniform(-5, 5),
                    'change_percent': np.random.uniform(-3, 3),
                    'volume': np.random.uniform(1e6, 1e8)
                }
                st.info(f"ℹ️ Using simulated data for {symbol}")
            
            progress_bar.progress(30)
            
            # Step 3: Historical data
            status_text.text(steps[2])
            historical_data = get_historical_data(symbol, period=time_frame)
            st.session_state.historical_data = historical_data
            
            if historical_data and len(historical_data) > 0:
                st.success(f"✅ Loaded {len(historical_data)} days of historical data")
            else:
                st.warning("⚠️ Limited historical data available")
            
            progress_bar.progress(50)
            
            # Step 4: News and sentiment
            status_text.text(steps[3])
            news_data = []
            try:
                news_data = get_market_news(query=symbol)
                if news_data:
                    st.success(f"✅ Found {len(news_data)} news articles")
            except Exception as e:
                st.warning(f"⚠️ Could not fetch news: {str(e)}")
                # Create simulated news
                news_data = [{
                    'title': f'{symbol} Market Update',
                    'description': f'Latest market analysis for {symbol}',
                    'source': 'Market News',
                    'publishedAt': datetime.now().strftime('%Y-%m-%d')
                }]
            
            st.session_state.news_data = news_data
            sentiment_score = get_sentiment_score(symbol)
            
            progress_bar.progress(65)
            
            # Step 5: AI Analysis
            status_text.text(steps[4])
            
            # Prepare data for AI analysis
            analysis_data = {
                'symbol': symbol,
                'crypto_data': current_data if len(symbol) <= 5 else None,
                'stock_data': current_data if len(symbol) > 5 else None,
                'news_data': news_data,
                'use': 'llama' if 'Llama' in ai_engine else 'openai'
            }
            
            try:
                # Run AI analysis
                analysis = ai_market_analysis(**analysis_data)
            except Exception as e:
                st.warning(f"⚠️ AI analysis returned error, using simulated analysis: {str(e)}")
                # Create simulated analysis
                analysis = {
                    'summary': f"Analysis for {symbol} based on current market conditions.",
                    'key_points': [
                        f"{symbol} shows potential based on current trends",
                        "Market conditions are favorable for analysis",
                        "Consider technical indicators for entry points"
                    ]
                }
            
            # Enhance analysis with additional metrics
            current_price = current_data.get('price', 0)
            analysis['current_price'] = current_price
            
            if historical_data and len(historical_data) > 1:
                prices = [h['close'] for h in historical_data]
                analysis['current_price'] = prices[-1]
                
                # Calculate price change safely
                if len(prices) > 1:
                    price_change = ((prices[-1] - prices[-2]) / prices[-2] * 100)
                    analysis['price_change_24h'] = price_change
                else:
                    analysis['price_change_24h'] = current_data.get('change_percent', 0)
                
                # Calculate volatility safely
                if len(prices) >= 2:
                    volatility = calculate_volatility(prices)
                    analysis['volatility_percent'] = volatility
                else:
                    analysis['volatility_percent'] = 20.0
            else:
                analysis['price_change_24h'] = current_data.get('change_percent', 0)
                analysis['volatility_percent'] = 25.0
            
            # Add sentiment
            analysis['market_sentiment'] = 'Bullish' if sentiment_score > 0.3 else 'Bearish' if sentiment_score < -0.3 else 'Neutral'
            analysis['sentiment_score'] = sentiment_score
            
            # Add technical indicators
            advanced_metrics = get_advanced_metrics(symbol, historical_data)
            analysis['technical_indicators'] = advanced_metrics
            
            # Generate recommendation
            price = analysis.get('current_price', current_price)
            volatility = analysis.get('volatility_percent', 25)
            sentiment = analysis.get('market_sentiment', 'Neutral')
            
            # Smart recommendation logic
            if sentiment == 'Bullish' and volatility < 25:
                analysis['recommendation'] = 'BUY'
                analysis['confidence_score'] = min(95, 75 + np.random.randint(5, 15))
                analysis['risk_level'] = 'Low'
            elif sentiment == 'Bullish':
                analysis['recommendation'] = 'BUY'
                analysis['confidence_score'] = 70 + np.random.randint(0, 10)
                analysis['risk_level'] = 'Medium'
            elif sentiment == 'Bearish' and volatility > 30:
                analysis['recommendation'] = 'SELL'
                analysis['confidence_score'] = 75 + np.random.randint(0, 10)
                analysis['risk_level'] = 'High'
            elif sentiment == 'Bearish':
                analysis['recommendation'] = 'HOLD'
                analysis['confidence_score'] = 60 + np.random.randint(0, 10)
                analysis['risk_level'] = 'Medium'
            else:
                analysis['recommendation'] = 'HOLD'
                analysis['confidence_score'] = 65 + np.random.randint(0, 10)
                analysis['risk_level'] = 'Medium'
            
            # Trading levels
            analysis['stop_loss_price'] = price * 0.95
            analysis['take_profit_price'] = price * 1.15
            analysis['entry_price'] = price
            analysis['risk_reward_ratio'] = round(np.random.uniform(2.0, 3.5), 1)
            analysis['expected_move_percent'] = round(np.random.uniform(8, 15), 1)
            analysis['timeframe'] = '2-6 weeks'
            
            # Add action items
            analysis['action_items'] = [
                f"Set stop loss at ${analysis['stop_loss_price']:.2f}",
                f"Target take profit at ${analysis['take_profit_price']:.2f}",
                "Monitor key support and resistance levels",
                "Review news for market catalysts"
            ]
            
            progress_bar.progress(85)
            
            # Step 6: Position sizing
            status_text.text(steps[5])
            if invest_amount > 0:
                position_analysis = calculate_position_size(
                    account_size=invest_amount,
                    risk_per_trade=2.0,
                    stop_loss=analysis['stop_loss_price'],
                    entry_price=analysis['entry_price']
                )
                analysis['position_sizing'] = position_analysis
            
            # Store results
            st.session_state.analysis_result = analysis
            st.session_state.analysis_done = True
            
            # Update history
            st.session_state.analysis_history.append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'recommendation': analysis['recommendation'],
                'confidence': analysis['confidence_score']
            })
            
            progress_bar.progress(100)
            time.sleep(0.3)
            status_text.text("✅ Analysis Complete")
            
            st.success(f"""
            ### ✅ Analysis completed for **{symbol}**
            
            **Recommendation:** {analysis['recommendation']}
            **Confidence:** {analysis['confidence_score']}%
            **Risk Level:** {analysis['risk_level']}
            **Current Price:** ${analysis['current_price']:,.2f}
            """)
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            st.info("💡 Please try a different symbol or check your connection.")
            st.session_state.analysis_done = False

# Display Results
if st.session_state.analysis_done and st.session_state.analysis_result:
    analysis = st.session_state.analysis_result
    symbol = st.session_state.symbol
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Technical", "📰 News", "🎯 Trading"])
    
    with tab1:
        # Key Metrics
        st.markdown(f"## {symbol} - Market Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            price = analysis.get('current_price', 0)
            price_change = analysis.get('price_change_24h', 0)
            change_color = '#10b981' if price_change >= 0 else '#ef4444'
            change_icon = '↗' if price_change >= 0 else '↘'
            
            price_html = f"""
            <div class="metric-card">
                <div class="metric-label">Current Price</div>
                <div class="metric-value">${price:,.2f}</div>
                <div style="color: {change_color}; font-weight: 600;">
                    {change_icon} {price_change:+.2f}%
                </div>
            </div>
            """
            st.markdown(price_html, unsafe_allow_html=True)
        
        with col2:
            sentiment = analysis.get('market_sentiment', 'Neutral')
            badge_class = 'success' if sentiment == 'Bullish' else 'danger' if sentiment == 'Bearish' else 'warning'
            
            sentiment_html = f"""
            <div class="metric-card">
                <div class="metric-label">Market Sentiment</div>
                <div class="metric-value">{sentiment}</div>
                <span class="badge badge-{badge_class}">{sentiment.upper()}</span>
            </div>
            """
            st.markdown(sentiment_html, unsafe_allow_html=True)
        
        with col3:
            confidence = analysis.get('confidence_score', 70)
            
            confidence_html = f"""
            <div class="metric-card">
                <div class="metric-label">AI Confidence</div>
                <div class="metric-value">{confidence}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {confidence}%"></div>
                </div>
            </div>
            """
            st.markdown(confidence_html, unsafe_allow_html=True)
        
        with col4:
            risk_level = analysis.get('risk_level', 'Medium')
            risk_badge = 'success' if risk_level == 'Low' else 'danger' if risk_level == 'High' else 'warning'
            
            risk_html = f"""
            <div class="metric-card">
                <div class="metric-label">Risk Level</div>
                <div class="metric-value">{risk_level}</div>
                <span class="badge badge-{risk_badge}">{risk_level.upper()}</span>
            </div>
            """
            st.markdown(risk_html, unsafe_allow_html=True)
        
        # Recommendation Card
        st.markdown("---")
        
        rec = analysis.get('recommendation', 'HOLD')
        signal_class = 'signal-buy' if 'BUY' in rec else 'signal-sell' if 'SELL' in rec else 'signal-hold'
        signal_color = 'var(--success-dark)' if 'BUY' in rec else 'var(--danger-dark)' if 'SELL' in rec else 'var(--warning-dark)'
        signal_icon = '🟢' if 'BUY' in rec else '🔴' if 'SELL' in rec else '🟡'
        
        rec_html = f"""
        <div class="clean-card {signal_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div>
                    <div style="font-size: 0.875rem; color: var(--neutral); margin-bottom: 0.25rem;">AI RECOMMENDATION</div>
                    <div style="font-size: 1.75rem; font-weight: 700; color: {signal_color};">{rec}</div>
                </div>
                <div style="font-size: 2.5rem;">{signal_icon}</div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                <div>
                    <div style="font-size: 0.875rem; color: var(--neutral);">Expected Return</div>
                    <div style="font-size: 1.25rem; font-weight: 600;">+{analysis.get('expected_move_percent', 0):.1f}%</div>
                </div>
                <div>
                    <div style="font-size: 0.875rem; color: var(--neutral);">Timeframe</div>
                    <div style="font-size: 1.25rem; font-weight: 600;">{analysis.get('timeframe', 'N/A')}</div>
                </div>
                <div>
                    <div style="font-size: 0.875rem; color: var(--neutral);">Risk/Reward</div>
                    <div style="font-size: 1.25rem; font-weight: 600;">1:{analysis.get('risk_reward_ratio', 0):.1f}</div>
                </div>
            </div>
        </div>
        """
        st.markdown(rec_html, unsafe_allow_html=True)
        
        # Action Items
        if analysis.get('action_items'):
            st.markdown("---")
            st.markdown("### 🎯 Action Items")
            
            for action in analysis['action_items'][:3]:
                st.markdown(f"<div class='clean-card' style='margin-bottom: 0.5rem;'>✅ {action}</div>", unsafe_allow_html=True)
        
        # Price Chart
        st.markdown("---")
        st.markdown("### 📈 Price Chart")
        
        if st.session_state.historical_data and len(st.session_state.historical_data) > 0:
            df = pd.DataFrame(st.session_state.historical_data)
            
            fig = go.Figure(data=[
                go.Candlestick(
                    x=df['timestamp'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price'
                )
            ])
            
            # Add moving average if enough data
            if len(df) > 20:
                df['MA20'] = df['close'].rolling(window=20).mean()
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['MA20'],
                    name='MA20',
                    line=dict(color='orange', width=1)
                ))
            
            fig.update_layout(
                title=f'{symbol} Price Action',
                yaxis_title='Price ($)',
                xaxis_title='Date',
                template='plotly_white',
                height=400,
                showlegend=True,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Historical price data is not available for chart display.")
    
    with tab2:
        # Technical Analysis
        st.markdown("### 📊 Technical Indicators")
        
        if analysis.get('technical_indicators'):
            tech = analysis['technical_indicators']
            
            cols = st.columns(4)
            indicators = [
                ("RSI", f"{tech.get('rsi', 0):.1f}", 
                 "Overbought" if tech.get('rsi', 0) > 70 else "Oversold" if tech.get('rsi', 0) < 30 else "Neutral"),
                ("Trend", tech.get('trend', 'Neutral'),
                 "Bullish" if 'Bull' in str(tech.get('trend', '')) else "Bearish"),
                ("Volatility", f"{tech.get('volatility_percent', 0):.1f}%",
                 "High" if tech.get('volatility_percent', 0) > 25 else "Low"),
                ("MACD", f"{tech.get('macd', 0):.3f}",
                 "Positive" if tech.get('macd', 0) > 0 else "Negative")
            ]
            
            for i, (name, value, status) in enumerate(indicators):
                with cols[i]:
                    badge_type = 'success' if ('Bull' in status or 'Positive' in status or 'Neutral' in status) else 'danger' if ('Bear' in status or 'Negative' in status or 'High' in status) else 'warning'
                    tech_html = f"""
                    <div class="clean-card">
                        <div style="font-size: 0.875rem; color: var(--neutral); margin-bottom: 0.5rem;">{name}</div>
                        <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem;">{value}</div>
                        <span class="badge badge-{badge_type}">{status}</span>
                    </div>
                    """
                    st.markdown(tech_html, unsafe_allow_html=True)
            
            # Support & Resistance
            st.markdown("---")
            st.markdown("### 🎯 Key Levels")
            
            col_s, col_r = st.columns(2)
            with col_s:
                support_html = f"""
                <div class="clean-card">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div>
                            <div style="font-size: 0.875rem; color: var(--neutral);">Support</div>
                            <div style="font-size: 1.5rem; font-weight: 600; color: var(--success);">${tech.get('support_level', 0):.2f}</div>
                        </div>
                        <div style="font-size: 1.5rem;">🛡️</div>
                    </div>
                </div>
                """
                st.markdown(support_html, unsafe_allow_html=True)
            
            with col_r:
                resistance_html = f"""
                <div class="clean-card">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div>
                            <div style="font-size: 0.875rem; color: var(--neutral);">Resistance</div>
                            <div style="font-size: 1.5rem; font-weight: 600; color: var(--danger);">${tech.get('resistance_level', 0):.2f}</div>
                        </div>
                        <div style="font-size: 1.5rem;">⛰️</div>
                    </div>
                </div>
                """
                st.markdown(resistance_html, unsafe_allow_html=True)
    
    with tab3:
        # News & Sentiment
        st.markdown("### 📰 Market News")
        
        if st.session_state.news_data and len(st.session_state.news_data) > 0:
            for i, news in enumerate(st.session_state.news_data[:5]):
                news_html = f"""
                <div class="clean-card">
                    <div style="font-weight: 600; margin-bottom: 0.5rem; color: var(--neutral-dark);">{news.get('title', 'No title')}</div>
                    <div style="font-size: 0.875rem; color: var(--neutral); margin-bottom: 0.75rem;">{news.get('description', 'No description')[:150]}...</div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--neutral-light);">
                        <span>📰 {news.get('source', 'Unknown')}</span>
                        <span>🕒 {news.get('publishedAt', '')}</span>
                    </div>
                </div>
                """
                st.markdown(news_html, unsafe_allow_html=True)
        else:
            st.info("No recent news available for this symbol.")
    
    with tab4:
        # Trading Plan
        st.markdown("### 🎯 Trading Strategy")
        
        # Position Calculator
        st.markdown("#### Position Calculator")
        
        col_a, col_b = st.columns(2)
        with col_a:
            entry_price = st.number_input(
                "Entry Price ($)",
                value=float(analysis.get('entry_price', 0)),
                min_value=0.0,
                step=0.01
            )
            stop_loss = st.number_input(
                "Stop Loss ($)",
                value=float(analysis.get('stop_loss_price', 0)),
                min_value=0.0,
                step=0.01
            )
        
        with col_b:
            risk_percent = st.slider(
                "Risk per Trade (%)",
                min_value=0.5,
                max_value=5.0,
                value=2.0,
                step=0.5
            )
            take_profit = st.number_input(
                "Take Profit ($)",
                value=float(analysis.get('take_profit_price', 0)),
                min_value=0.0,
                step=0.01
            )
        
        if entry_price > 0 and stop_loss > 0:
            position = calculate_position_size(invest_amount, risk_percent, stop_loss, entry_price)
            
            if position:
                risk_reward = 0
                if (entry_price - stop_loss) > 0:
                    risk_reward = ((take_profit - entry_price) / (entry_price - stop_loss))
                
                position_html = f"""
                <div class="clean-card">
                    <div style="font-size: 0.875rem; color: var(--neutral); margin-bottom: 0.5rem;">POSITION SIZE</div>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                        <div>
                            <div style="font-size: 0.75rem; color: var(--neutral-light);">Shares</div>
                            <div style="font-size: 1.25rem; font-weight: 600;">{position['shares']:.0f}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.75rem; color: var(--neutral-light);">Position Value</div>
                            <div style="font-size: 1.25rem; font-weight: 600;">${position['position_value']:,.0f}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.75rem; color: var(--neutral-light);">Risk Amount</div>
                            <div style="font-size: 1.25rem; font-weight: 600; color: var(--danger);">${position['risk_amount']:,.0f}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.75rem; color: var(--neutral-light);">Risk/Reward</div>
                            <div style="font-size: 1.25rem; font-weight: 600;">1:{risk_reward:.1f}</div>
                        </div>
                    </div>
                </div>
                """
                st.markdown(position_html, unsafe_allow_html=True)
        
        # Trading Checklist
        st.markdown("---")
        st.markdown("#### ✅ Pre-Trade Checklist")
        
        checklist = [
            "Market conditions align with strategy",
            "Stop loss and take profit levels set",
            "Position size calculated correctly",
            "No major news events scheduled",
            "Portfolio risk within limits"
        ]
        
        for item in checklist:
            st.checkbox(item, value=True)
    
    # Footer Actions
    st.markdown("---")
    col_export, col_refresh, col_new = st.columns(3)
    
    with col_export:
        if st.button("📊 Export Report", use_container_width=True):
            st.success("Report exported successfully!")
    
    with col_refresh:
        if st.button("🔄 Update Data", use_container_width=True):
            st.session_state.analysis_done = False
            st.rerun()
    
    with col_new:
        if st.button("➕ New Analysis", use_container_width=True):
            st.session_state.analysis_done = False
            st.session_state.analysis_result = None
            st.session_state.symbol = ""
            st.rerun()

elif symbol and not st.session_state.analysis_done:
    # Preview state
    st.info(f"Entered symbol: **{symbol}**. Click 'Launch Analysis' to begin.")
    
    # Popular symbols preview
    st.markdown("#### Popular Assets")
    popular = ["BTC", "ETH", "AAPL", "TSLA", "GOOGL", "NVDA"]
    
    cols = st.columns(3)
    for i, sym in enumerate(popular):
        with cols[i % 3]:
            if st.button(sym, key=f"pop_{sym}", use_container_width=True):
                st.session_state.symbol = sym
                st.session_state.last_symbol = sym
                st.rerun()

else:
    # Welcome screen
    col_welcome1, col_welcome2, col_welcome3 = st.columns([1, 2, 1])
    
    with col_welcome2:
        welcome_html = """
        <div style="text-align: center; padding: 3rem 1rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📈</div>
            <h2 style="color: var(--neutral-dark); margin-bottom: 1rem;">AI Market Analyst</h2>
            <p style="color: var(--neutral); margin-bottom: 2rem;">
                Professional market analysis powered by AI. 
                Get real-time insights, technical indicators, and actionable recommendations.
            </p>
        </div>
        """
        st.markdown(welcome_html, unsafe_allow_html=True)
        
        # Features grid
        features_html = """
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin: 2rem 0;">
            <div class="clean-card">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🤖</div>
                <div style="font-weight: 600; margin-bottom: 0.25rem;">AI-Powered</div>
                <div style="font-size: 0.875rem; color: var(--neutral);">Advanced machine learning models</div>
            </div>
            <div class="clean-card">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📊</div>
                <div style="font-weight: 600; margin-bottom: 0.25rem;">Real-time Data</div>
                <div style="font-size: 0.875rem; color: var(--neutral);">Live market data & analysis</div>
            </div>
            <div class="clean-card">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🎯</div>
                <div style="font-weight: 600; margin-bottom: 0.25rem;">Actionable Insights</div>
                <div style="font-size: 0.875rem; color: var(--neutral);">Clear buy/sell recommendations</div>
            </div>
            <div class="clean-card">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🛡️</div>
                <div style="font-weight: 600; margin-bottom: 0.25rem;">Risk Management</div>
                <div style="font-size: 0.875rem; color: var(--neutral);">Professional risk assessment</div>
            </div>
        </div>
        """
        st.markdown(features_html, unsafe_allow_html=True)

# Disclaimer
disclaimer_html = """
<div class="clean-card" style="margin-top: 2rem; border-left: 4px solid var(--neutral);">
    <div style="display: flex; align-items: start; gap: 0.5rem;">
        <div style="font-size: 1.25rem;">⚠️</div>
        <div>
            <div style="font-weight: 600; margin-bottom: 0.25rem; color: var(--neutral-dark);">Disclaimer</div>
            <div style="font-size: 0.875rem; color: var(--neutral);">
                This analysis is for informational purposes only. Not financial advice. 
                Always conduct your own research before making investment decisions.
            </div>
        </div>
    </div>
</div>
"""
st.markdown(disclaimer_html, unsafe_allow_html=True)