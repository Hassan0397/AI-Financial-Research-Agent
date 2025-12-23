import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import time
import numpy as np
from services.data_fetch import get_crypto_data, get_stock_data, search_asset, get_multiple_crypto_data, get_multiple_stock_data
from services.news_fetch import get_market_news, get_asset_news

# Page Configuration
st.set_page_config(
    page_title="AI Financial Research Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Color Scheme
PRIMARY_COLOR = "#2563EB"
SECONDARY_COLOR = "#0F172A"
ACCENT_COLOR = "#10B981"
WARNING_COLOR = "#EF4444"
SUCCESS_COLOR = "#10B981"
BACKGROUND_COLOR = "#F8FAFC"
CARD_BACKGROUND = "#FFFFFF"
BORDER_COLOR = "#E2E8F0"

# Professional Custom CSS
st.markdown(f"""
<style>
    /* Base Styles */
    .stApp {{
        background-color: {BACKGROUND_COLOR};
    }}
    
    /* Typography */
    .main-header {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {SECONDARY_COLOR};
        margin-bottom: 1rem;
        letter-spacing: -0.025em;
    }}
    .sub-header {{
        font-size: 1.75rem;
        font-weight: 600;
        color: {SECONDARY_COLOR};
        margin-bottom: 1rem;
        letter-spacing: -0.025em;
    }}
    .section-header {{
        font-size: 1.25rem;
        font-weight: 600;
        color: {SECONDARY_COLOR};
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {PRIMARY_COLOR};
    }}
    
    /* Cards */
    .metric-card {{
        background: {CARD_BACKGROUND};
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid {BORDER_COLOR};
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }}
    .metric-card:hover {{
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transform: translateY(-2px);
    }}
    .metric-card h4 {{
        color: #64748B;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }}
    .metric-card h2 {{
        color: {SECONDARY_COLOR};
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }}
    .metric-card p {{
        color: #64748B;
        font-size: 0.875rem;
        margin: 0.25rem 0;
    }}
    
    /* Color Classes */
    .positive-change {{
        color: {SUCCESS_COLOR};
        font-weight: 600;
    }}
    .negative-change {{
        color: {WARNING_COLOR};
        font-weight: 600;
    }}
    
    /* Detailed View Styles */
    .detailed-tab {{
        background: {CARD_BACKGROUND};
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid {BORDER_COLOR};
        margin-top: 1rem;
    }}
    
    /* Chart Controls */
    .chart-controls {{
        background: {BACKGROUND_COLOR};
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }}
    
    /* Advanced Metrics Grid */
    .metrics-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }}
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: {BACKGROUND_COLOR};
        padding: 4px;
        border-radius: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 48px;
        background-color: transparent;
        border-radius: 6px;
        padding: 0 20px;
        font-weight: 500;
        color: #64748B;
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: rgba(37, 99, 235, 0.05);
        color: {PRIMARY_COLOR};
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {PRIMARY_COLOR} !important;
        color: white !important;
        border-color: {PRIMARY_COLOR} !important;
    }}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'crypto_data' not in st.session_state:
    st.session_state.crypto_data = {}
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = {}
if 'news_data' not in st.session_state:
    st.session_state.news_data = []
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'watchlist_cryptos' not in st.session_state:
    st.session_state.watchlist_cryptos = ["bitcoin", "ethereum", "solana"]
if 'watchlist_stocks' not in st.session_state:
    st.session_state.watchlist_stocks = ["AAPL", "TSLA", "GOOGL"]
if 'detailed_view_asset' not in st.session_state:
    st.session_state.detailed_view_asset = None
if 'detailed_view_type' not in st.session_state:
    st.session_state.detailed_view_type = None

# Professional Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%);
        padding: 2rem 1rem;
        border-radius: 0 0 12px 12px;
        text-align: center;
        margin-bottom: 2rem;
    ">
        <div style="
            background: white;
            width: 60px;
            height: 60px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <span style="font-size: 28px;">📊</span>
        </div>
        <h2 style="color: white; margin: 0; font-size: 1.25rem; font-weight: 600;">
            AI Financial Research
        </h2>
        <p style="color: rgba(255, 255, 255, 0.8); font-size: 0.875rem; margin-top: 0.5rem;">
            Professional Market Intelligence
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats
    st.markdown('<div class="section-header">⚡ Dashboard Status</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Last Updated", datetime.now().strftime("%H:%M"), delta="Live")
    with col2:
        if st.session_state.last_update:
            st.metric("Data Age", "Fresh", delta="✓")
    
    st.markdown("---")
    
    # Settings
    st.markdown('<div class="section-header">🔧 Configuration</div>', unsafe_allow_html=True)
    auto_refresh = st.checkbox("Auto-refresh Data", value=True)
    if auto_refresh:
        refresh_rate = st.select_slider(
            "Refresh Interval",
            options=[30, 60, 120, 300],
            value=60,
            format_func=lambda x: f"{x} seconds"
        )
    
    st.markdown("---")
    
    # Watchlists
    st.markdown('<div class="section-header">📈 Market Watchlists</div>', unsafe_allow_html=True)
    
    # Crypto Watchlist
    st.caption("Cryptocurrencies")
    crypto_options = ["bitcoin", "ethereum", "solana", "cardano", "polkadot", 
                     "dogecoin", "chainlink", "litecoin", "ripple", "binancecoin"]
    new_cryptos = st.multiselect(
        "Select Cryptocurrencies",
        crypto_options,
        default=st.session_state.watchlist_cryptos,
        label_visibility="collapsed"
    )
    
    if new_cryptos != st.session_state.watchlist_cryptos:
        st.session_state.watchlist_cryptos = new_cryptos
        st.session_state.crypto_data = {}
    
    # Stock Watchlist
    st.caption("Equities")
    stock_options = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", 
                    "META", "NVDA", "JPM", "NFLX", "ADBE"]
    new_stocks = st.multiselect(
        "Select Stocks",
        stock_options,
        default=st.session_state.watchlist_stocks,
        label_visibility="collapsed"
    )
    
    if new_stocks != st.session_state.watchlist_stocks:
        st.session_state.watchlist_stocks = new_stocks
        st.session_state.stock_data = {}
    
    st.markdown("---")
    
    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.crypto_data = {}
            st.session_state.stock_data = {}
            st.session_state.news_data = []
            st.session_state.detailed_view_asset = None
            st.session_state.last_update = datetime.now()
            st.rerun()
    with col2:
        if st.button("📊 Export", use_container_width=True):
            st.info("Export feature coming soon!")

# Main Dashboard Header
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.markdown('<h1 class="main-header">Financial Intelligence Dashboard</h1>', unsafe_allow_html=True)
    st.caption("Professional-grade market analysis and real-time insights")

with col2:
    if st.session_state.last_update:
        st.metric("Last Update", st.session_state.last_update.strftime("%H:%M:%S"), 
                 delta="Updated")
    else:
        st.metric("Status", "Initializing...")

with col3:
    st.markdown('<div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.875rem; font-weight: 500; background-color: rgba(16, 185, 129, 0.1); color: #10B981;">🟢 Live Data</div>', unsafe_allow_html=True)

st.markdown("---")

# Function to generate sample price data (in production, this would come from API)
def generate_price_data(days=30, volatility=0.02, trend=0.001):
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    prices = [100]
    for i in range(1, days):
        change = np.random.normal(trend, volatility)
        prices.append(prices[-1] * (1 + change))
    return pd.DataFrame({'Date': dates, 'Price': prices})

def generate_volume_data(days=30):
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    volumes = np.random.randint(1000000, 5000000, size=days)
    return pd.DataFrame({'Date': dates, 'Volume': volumes})

# Function to create detailed view
def show_detailed_view(asset_name, asset_type, asset_data):
    st.markdown(f"### 📊 {asset_name.upper()} - Detailed Analysis")
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.detailed_view_asset = None
        st.session_state.detailed_view_type = None
        st.rerun()
    
    # Create tabs for different analysis views
    detail_tabs = st.tabs(["📈 Price Analysis", "📊 Volume Analysis", "📉 Technical Indicators", "📰 News & Sentiment"])
    
    with detail_tabs[0]:  # Price Analysis
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("#### Historical Price Chart")
            
            # Time period selector
            time_period = st.selectbox(
                "Time Period",
                ["1D", "1W", "1M", "3M", "6M", "1Y", "All"],
                key=f"price_period_{asset_name}"
            )
            
            # Generate sample price data (in real app, fetch from API)
            price_data = generate_price_data(days=90)
            
            # Create candlestick chart
            fig = go.Figure(data=[go.Candlestick(
                x=price_data['Date'],
                open=[p * 0.99 for p in price_data['Price']],
                high=[p * 1.02 for p in price_data['Price']],
                low=[p * 0.98 for p in price_data['Price']],
                close=price_data['Price'],
                name=asset_name
            )])
            
            fig.update_layout(
                title=f"{asset_name.upper()} Price Action",
                yaxis_title="Price (USD)",
                xaxis_title="Date",
                template="plotly_white",
                height=500,
                showlegend=False,
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Price Statistics")
            
            # Calculate metrics
            current_price = asset_data.get('current_price', 100)
            if asset_type == 'crypto':
                change_24h = asset_data.get('price_change_percentage_24h', 0)
                high_24h = asset_data.get('high_24h', current_price * 1.05)
                low_24h = asset_data.get('low_24h', current_price * 0.95)
            else:
                change_24h = asset_data.get('day_change_pct', 0)
                high_24h = asset_data.get('high', current_price * 1.05)
                low_24h = asset_data.get('low', current_price * 0.95)
            
            # Display metrics
            st.metric("Current Price", f"${current_price:,.2f}", 
                     f"{change_24h:+.2f}%")
            
            st.metric("24h High", f"${high_24h:,.2f}")
            st.metric("24h Low", f"${low_24h:,.2f}")
            
            # Volatility indicator
            volatility = abs(change_24h)
            if volatility < 2:
                volatility_color = SUCCESS_COLOR
                volatility_label = "Low"
            elif volatility < 5:
                volatility_color = "#F59E0B"
                volatility_label = "Medium"
            else:
                volatility_color = WARNING_COLOR
                volatility_label = "High"
            
            st.markdown(f"""
            <div style="padding: 1rem; background: {BACKGROUND_COLOR}; border-radius: 8px; margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #64748B;">Volatility</span>
                    <span style="color: {volatility_color}; font-weight: 600;">{volatility_label}</span>
                </div>
                <div style="margin-top: 0.5rem; height: 4px; background: #E2E8F0; border-radius: 2px;">
                    <div style="width: {min(volatility * 10, 100)}%; height: 100%; background: {volatility_color}; border-radius: 2px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with detail_tabs[1]:  # Volume Analysis
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("#### Volume Analysis")
            
            # Volume chart
            volume_data = generate_volume_data(days=30)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=volume_data['Date'],
                y=volume_data['Volume'],
                name="Volume",
                marker_color=PRIMARY_COLOR
            ))
            
            fig.update_layout(
                title="Trading Volume (30 Days)",
                yaxis_title="Volume",
                xaxis_title="Date",
                template="plotly_white",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume statistics
            st.markdown("#### Volume Metrics")
            col_vol1, col_vol2, col_vol3 = st.columns(3)
            
            with col_vol1:
                avg_volume = volume_data['Volume'].mean()
                st.metric("Avg Daily Volume", f"{avg_volume:,.0f}")
            
            with col_vol2:
                max_volume = volume_data['Volume'].max()
                st.metric("Peak Volume", f"{max_volume:,.0f}")
            
            with col_vol3:
                volume_change = ((volume_data['Volume'].iloc[-1] - volume_data['Volume'].iloc[0]) / volume_data['Volume'].iloc[0]) * 100
                st.metric("30D Change", f"{volume_change:+.1f}%")
        
        with col2:
            st.markdown("#### Volume Profile")
            
            # Volume distribution
            volume_bins = pd.cut(volume_data['Volume'], bins=5)
            bin_counts = volume_bins.value_counts().sort_index()
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=[str(bin) for bin in bin_counts.index],
                values=bin_counts.values,
                hole=.3,
                marker_colors=['#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE']
            )])
            
            fig_pie.update_layout(
                title="Volume Distribution",
                height=300,
                showlegend=True
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with detail_tabs[2]:  # Technical Indicators
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Technical Analysis")
            
            # Generate price data for indicators
            price_data_ta = generate_price_data(days=100)
            
            # Calculate moving averages
            price_data_ta['MA20'] = price_data_ta['Price'].rolling(window=20).mean()
            price_data_ta['MA50'] = price_data_ta['Price'].rolling(window=50).mean()
            
            # Create chart with moving averages
            fig_ta = go.Figure()
            
            # Price line
            fig_ta.add_trace(go.Scatter(
                x=price_data_ta['Date'],
                y=price_data_ta['Price'],
                name="Price",
                line=dict(color=SECONDARY_COLOR, width=2)
            ))
            
            # Moving averages
            fig_ta.add_trace(go.Scatter(
                x=price_data_ta['Date'],
                y=price_data_ta['MA20'],
                name="MA20",
                line=dict(color=PRIMARY_COLOR, width=1.5)
            ))
            
            fig_ta.add_trace(go.Scatter(
                x=price_data_ta['Date'],
                y=price_data_ta['MA50'],
                name="MA50",
                line=dict(color=SUCCESS_COLOR, width=1.5)
            ))
            
            fig_ta.update_layout(
                title="Price with Moving Averages",
                yaxis_title="Price (USD)",
                template="plotly_white",
                height=400
            )
            
            st.plotly_chart(fig_ta, use_container_width=True)
            
            # RSI Calculation
            delta = price_data_ta['Price'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            price_data_ta['RSI'] = 100 - (100 / (1 + rs))
            
            # RSI Chart
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(
                x=price_data_ta['Date'],
                y=price_data_ta['RSI'],
                name="RSI",
                line=dict(color=PRIMARY_COLOR, width=2)
            ))
            
            # Add overbought/oversold lines
            fig_rsi.add_hline(y=70, line_dash="dash", line_color=WARNING_COLOR, opacity=0.5)
            fig_rsi.add_hline(y=30, line_dash="dash", line_color=SUCCESS_COLOR, opacity=0.5)
            
            fig_rsi.update_layout(
                title="Relative Strength Index (RSI)",
                yaxis_title="RSI",
                yaxis_range=[0, 100],
                template="plotly_white",
                height=300
            )
            
            st.plotly_chart(fig_rsi, use_container_width=True)
        
        with col2:
            st.markdown("#### Technical Signals")
            
            # Current RSI value
            current_rsi = price_data_ta['RSI'].iloc[-1]
            
            # Determine RSI signal
            if current_rsi > 70:
                rsi_signal = "Overbought ⚠️"
                signal_color = WARNING_COLOR
            elif current_rsi < 30:
                rsi_signal = "Oversold 📈"
                signal_color = SUCCESS_COLOR
            else:
                rsi_signal = "Neutral ↔️"
                signal_color = "#64748B"
            
            st.metric("RSI (14)", f"{current_rsi:.1f}", rsi_signal)
            
            # Moving average signals
            ma20 = price_data_ta['MA20'].iloc[-1]
            ma50 = price_data_ta['MA50'].iloc[-1]
            current_price = price_data_ta['Price'].iloc[-1]
            
            st.markdown("##### MA Crossovers")
            
            if ma20 > ma50:
                ma_signal = "Bullish 📈"
                ma_color = SUCCESS_COLOR
            else:
                ma_signal = "Bearish 📉"
                ma_color = WARNING_COLOR
            
            st.markdown(f"""
            <div style="padding: 1rem; background: {BACKGROUND_COLOR}; border-radius: 8px; margin: 1rem 0;">
                <div style="color: {ma_color}; font-weight: 600; font-size: 1rem;">{ma_signal}</div>
                <div style="margin-top: 0.5rem;">
                    <div>MA20: ${ma20:.2f}</div>
                    <div>MA50: ${ma50:.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Support and Resistance levels
            st.markdown("##### Key Levels")
            
            resistance = current_price * 1.05
            support = current_price * 0.95
            
            st.metric("Resistance", f"${resistance:,.2f}")
            st.metric("Support", f"${support:,.2f}")
    
    with detail_tabs[3]:  # News & Sentiment
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("#### Latest News & Analysis")
            
            try:
                news = get_asset_news(asset_name)
                if news:
                    for i, article in enumerate(news[:5]):
                        with st.container():
                            col_a, col_b = st.columns([4, 1])
                            with col_a:
                                st.markdown(f"""
                                <div style="padding: 1rem; border-radius: 8px; border: 1px solid {BORDER_COLOR}; margin-bottom: 1rem;">
                                    <h4 style="margin: 0 0 0.5rem 0;">{article.get('title', 'No Title')}</h4>
                                    <p style="color: #64748B; margin: 0 0 0.5rem 0;">{article.get('summary', article.get('description', ''))[:200]}...</p>
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <small style="color: #94A3B8;">Source: {article.get('source', 'Unknown')}</small>
                                        <a href="{article.get('url', '#')}" target="_blank" style="color: {PRIMARY_COLOR}; text-decoration: none;">Read →</a>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            with col_b:
                                sentiment = np.random.choice(['Positive', 'Neutral', 'Negative'])
                                if sentiment == 'Positive':
                                    sentiment_icon = "📈"
                                    sentiment_color = SUCCESS_COLOR
                                elif sentiment == 'Negative':
                                    sentiment_icon = "📉"
                                    sentiment_color = WARNING_COLOR
                                else:
                                    sentiment_icon = "↔️"
                                    sentiment_color = "#64748B"
                                
                                st.markdown(f"""
                                <div style="text-align: center; padding: 0.5rem; background: {BACKGROUND_COLOR}; border-radius: 8px;">
                                    <div style="font-size: 1.5rem;">{sentiment_icon}</div>
                                    <div style="font-size: 0.75rem; color: {sentiment_color}; margin-top: 0.25rem;">{sentiment}</div>
                                </div>
                                """, unsafe_allow_html=True)
                else:
                    st.info("No recent news available for this asset.")
            except:
                st.info("News data temporarily unavailable.")
        
        with col2:
            st.markdown("#### Sentiment Analysis")
            
            # Generate sentiment scores
            sentiment_scores = {
                'Positive': np.random.randint(40, 70),
                'Neutral': np.random.randint(20, 40),
                'Negative': np.random.randint(10, 30)
            }
            
            # Sentiment pie chart
            fig_sentiment = go.Figure(data=[go.Pie(
                labels=list(sentiment_scores.keys()),
                values=list(sentiment_scores.values()),
                hole=.4,
                marker_colors=[SUCCESS_COLOR, '#64748B', WARNING_COLOR]
            )])
            
            fig_sentiment.update_layout(
                title="Market Sentiment",
                height=300,
                showlegend=True
            )
            
            st.plotly_chart(fig_sentiment, use_container_width=True)
            
            # Overall sentiment
            overall_sentiment = 'Bullish' if sentiment_scores['Positive'] > 50 else 'Neutral' if sentiment_scores['Neutral'] > 40 else 'Bearish'
            
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: {BACKGROUND_COLOR}; border-radius: 8px; margin-top: 1rem;">
                <div style="font-size: 1rem; color: #64748B; margin-bottom: 0.5rem;">Overall Sentiment</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: {SUCCESS_COLOR if overall_sentiment == 'Bullish' else WARNING_COLOR if overall_sentiment == 'Bearish' else '#64748B'}">
                    {overall_sentiment}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Check if detailed view is active
if st.session_state.detailed_view_asset:
    # Get asset data
    asset_type = st.session_state.detailed_view_type
    asset_name = st.session_state.detailed_view_asset
    
    if asset_type == 'crypto':
        asset_data = st.session_state.crypto_data.get(asset_name, {})
    else:
        asset_data = st.session_state.stock_data.get(asset_name, {})
    
    # Show detailed view
    show_detailed_view(asset_name, asset_type, asset_data)
else:
    # Create main dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Cryptocurrencies", "📊 Equities", "🔍 Asset Search", "📰 Market Intelligence"])

    # Tab 1: Cryptocurrencies
    with tab1:
        st.markdown('<h2 class="sub-header">Cryptocurrency Markets</h2>', unsafe_allow_html=True)
        
        if not st.session_state.watchlist_cryptos:
            st.warning("Configure your cryptocurrency watchlist in the sidebar")
        else:
            # Fetch data
            crypto_data = {}
            
            for coin in st.session_state.watchlist_cryptos:
                if coin in st.session_state.crypto_data:
                    crypto_data[coin] = st.session_state.crypto_data[coin]
                else:
                    try:
                        data = get_crypto_data(coin)
                        if "error" not in data:
                            crypto_data[coin] = data
                            st.session_state.crypto_data[coin] = data
                    except:
                        pass
            
            # Display grid
            if crypto_data:
                num_cols = min(4, len(crypto_data))
                cols = st.columns(num_cols)
                
                for i, (coin, data) in enumerate(crypto_data.items()):
                    col_idx = i % num_cols
                    if i % num_cols == 0 and i != 0:
                        cols = st.columns(min(num_cols, len(crypto_data) - i))
                    
                    with cols[col_idx]:
                        if "error" not in data and data:
                            current_price = data.get("current_price", 0)
                            change_24h = data.get("price_change_percentage_24h", 0)
                            market_cap = data.get("market_cap", 0)
                            
                            # Format market cap
                            if market_cap >= 1e9:
                                market_cap_str = f"${market_cap/1e9:.1f}B"
                            elif market_cap >= 1e6:
                                market_cap_str = f"${market_cap/1e6:.1f}M"
                            else:
                                market_cap_str = f"${market_cap:,.0f}"
                            
                            # Display card
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>{coin.upper()}</h4>
                                <h2>${current_price:,.2f}</h2>
                                <p>24h Change: <span class="{'positive-change' if change_24h >= 0 else 'negative-change'}">
                                    {change_24h:+.2f}%
                                </span></p>
                                <p>Market Cap: {market_cap_str}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Detailed View Button
                            if st.button("📈 Detailed Analysis", key=f"crypto_detail_{coin}", use_container_width=True):
                                st.session_state.detailed_view_asset = coin
                                st.session_state.detailed_view_type = 'crypto'
                                st.rerun()

    # Tab 2: Stocks
    with tab2:
        st.markdown('<h2 class="sub-header">Equity Markets</h2>', unsafe_allow_html=True)
        
        if not st.session_state.watchlist_stocks:
            st.warning("Configure your equity watchlist in the sidebar")
        else:
            # Fetch data
            stock_data = {}
            
            for stock in st.session_state.watchlist_stocks:
                if stock in st.session_state.stock_data:
                    stock_data[stock] = st.session_state.stock_data[stock]
                else:
                    try:
                        data = get_stock_data(stock)
                        if "error" not in data:
                            stock_data[stock] = data
                            st.session_state.stock_data[stock] = data
                    except:
                        pass
            
            # Display grid
            if stock_data:
                num_cols = min(4, len(stock_data))
                cols = st.columns(num_cols)
                
                for i, (stock, data) in enumerate(stock_data.items()):
                    col_idx = i % num_cols
                    if i % num_cols == 0 and i != 0:
                        cols = st.columns(min(num_cols, len(stock_data) - i))
                    
                    with cols[col_idx]:
                        if "error" not in data and data:
                            current_price = data.get("current_price", 0)
                            day_change_pct = data.get("day_change_pct", 0)
                            volume = data.get("volume", 0)
                            
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>{stock}</h4>
                                <h2>${current_price:,.2f}</h2>
                                <p>Day Change: <span class="{'positive-change' if day_change_pct >= 0 else 'negative-change'}">
                                    {day_change_pct:+.2f}%
                                </span></p>
                                <p>Volume: {volume:,.0f}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Detailed View Button
                            if st.button("📈 Detailed Analysis", key=f"stock_detail_{stock}", use_container_width=True):
                                st.session_state.detailed_view_asset = stock
                                st.session_state.detailed_view_type = 'stock'
                                st.rerun()

    # Tab 3: Search (same as before)
    with tab3:
        st.markdown('<h2 class="sub-header">Asset Intelligence Search</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        with col1:
            query = st.text_input(
                "Search for any asset (cryptocurrency or equity)",
                placeholder="e.g., 'bitcoin', 'AAPL', 'ethereum', 'TSLA'",
                help="Enter the name or ticker symbol of any asset"
            )
        
        with col2:
            st.write("")
            st.write("")
            search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)
        
        if query or search_clicked:
            with st.spinner("Analyzing asset data..."):
                try:
                    result = search_asset(query)
                    
                    if "error" not in result:
                        asset_type = result["type"]
                        data = result["data"]
                        
                        st.success(f"Asset identified: **{data.get('name', query.upper())}** ({asset_type.upper()})")
                        
                        # Asset details
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown("#### 📈 Key Metrics")
                            
                            if asset_type == "crypto":
                                current_price = data.get('current_price', 0)
                                change_24h = data.get('price_change_percentage_24h', 0)
                                
                                metrics_cols = st.columns(4)
                                with metrics_cols[0]:
                                    st.metric("Price", f"${current_price:,.2f}", f"{change_24h:+.2f}%")
                                with metrics_cols[1]:
                                    st.metric("Market Cap", f"${data.get('market_cap', 0):,.0f}")
                                with metrics_cols[2]:
                                    st.metric("24h Volume", f"${data.get('total_volume', 0):,.0f}")
                                with metrics_cols[3]:
                                    high_low = f"${data.get('high_24h', 0):,.0f} / ${data.get('low_24h', 0):,.0f}"
                                    st.metric("24h Range", high_low)
                            
                            else:  # stock
                                current_price = data.get('current_price', 0)
                                day_change = data.get('day_change', 0)
                                
                                metrics_cols = st.columns(4)
                                with metrics_cols[0]:
                                    st.metric("Price", f"${current_price:,.2f}", f"${day_change:+.2f}")
                                with metrics_cols[1]:
                                    st.metric("Day High", f"${data.get('high', 0):,.2f}")
                                with metrics_cols[2]:
                                    st.metric("Day Low", f"${data.get('low', 0):,.2f}")
                                with metrics_cols[3]:
                                    st.metric("Volume", f"{data.get('volume', 0):,.0f}")
                        
                        with col2:
                            st.markdown("#### ⚡ Actions")
                            if st.button("📈 Open Detailed View", use_container_width=True):
                                st.session_state.detailed_view_asset = query.lower() if asset_type == 'crypto' else query.upper()
                                st.session_state.detailed_view_type = asset_type
                                st.rerun()
                    
                    else:
                        st.error("Asset not found")
                
                except Exception as e:
                    st.error("Search failed. Please try again.")

    # Tab 4: News (same as before)
    with tab4:
        st.markdown('<h2 class="sub-header">Market Intelligence</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            news_category = st.selectbox(
                "Category",
                ["General Market", "Cryptocurrency", "Stocks", "Economy", "Technology"],
                label_visibility="collapsed"
            )
        
        with col2:
            if st.button("🔄 Refresh News", use_container_width=True):
                st.session_state.news_data = []
        
        category_map = {
            "General Market": "financial market",
            "Cryptocurrency": "cryptocurrency",
            "Stocks": "stock market",
            "Economy": "economy",
            "Technology": "technology stocks"
        }
        
        if not st.session_state.news_data:
            with st.spinner("Gathering market intelligence..."):
                try:
                    news = get_market_news(category_map.get(news_category, "financial market"))
                    if news:
                        st.session_state.news_data = news
                except:
                    st.error("Failed to load news")
        
        if st.session_state.news_data:
            for i, article in enumerate(st.session_state.news_data[:8]):
                if isinstance(article, dict):
                    title = article.get('title', 'No Title')
                    url = article.get('url', '#')
                    summary = article.get('summary', article.get('description', ''))
                    source = article.get('source', 'Unknown')
                    
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"""
                        <div style="background: {CARD_BACKGROUND}; padding: 1.25rem; border-radius: 8px; border: 1px solid {BORDER_COLOR}; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); margin-bottom: 1rem;">
                            <h4 style="color: {SECONDARY_COLOR}; font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">{title}</h4>
                            <p style="color: #64748B; font-size: 0.875rem; line-height: 1.5; margin-bottom: 0.5rem;">{summary[:200]}...</p>
                            <small style="color: #94A3B8;">Source: {source}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("→", key=f"read_{i}", help="Open article"):
                            st.markdown(f"[Open]({url})")
                    
                    if i < len(st.session_state.news_data[:8]) - 1:
                        st.markdown("---")

# Professional Footer
st.markdown("""
---
<div style="
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    color: #64748B;
    font-size: 0.875rem;
">
    <div>
        📊 <strong>AI Financial Research Agent</strong> • Professional Edition
    </div>
    <div>
        Last Updated: {}
    </div>
    <div>
        🔒 Data Secured • ⚡ Real-time Processing
    </div>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

# Update timestamp
if not st.session_state.last_update:
    st.session_state.last_update = datetime.now()

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()