import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as ob
import ta

# Page configuration
st.set_page_config(page_title="Mama Trading Analytics", layout="wide")
st.title("📈 Mama's Pro Trading Chart Analyzer")
st.subheader("Crypto & Forex Live Signals with Support/Resistance")

# 1. Sidebar Inputs
st.sidebar.header("⚙️ Market Settings")

# Asset Selection Mapping
asset_type = st.sidebar.selectbox("Market Type", ["Forex / Gold", "Crypto"])
if asset_type == "Crypto":
    ticker_options = {"BTC-USD": "Bitcoin (BTC)", "ETH-USD": "Ethereum (ETH)", "SOL-USD": "Solana (SOL)"}
else:
    ticker_options = {"GC=F": "Gold (XAUUSD)", "EURUSD=X": "EURUSD", "GBPUSD=X": "GBPUSD", "JPY=X": "USDJPY"}

selected_ticker = st.sidebar.selectbox("Select Asset", list(ticker_options.keys()), format_func=lambda x: ticker_options[x])

# Timeframe Mapping (Streamlit to yfinance)
timeframe_map = {"1m": "1m", "5m": "5m", "15m": "15m"}
tf = st.sidebar.selectbox("Timeframe", list(timeframe_map.keys()), index=1)

# Period strategy based on timeframe
period = "1d" if tf == "1m" else "5d"

# 2. Fetch Data
@st.cache_data(ttl=60)  # Cache data for 1 minute
def load_data(symbol, tf_str, period_str):
    df = yf.download(tickers=symbol, period=period_str, interval=tf_str)
    # Flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

try:
    df = load_data(selected_ticker, timeframe_map[tf], period)
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

if df.empty:
    st.warning("No data found. The market might be closed or API limit reached.")
    st.stop()

# 3. Technical Indicators Calculation
df['EMA_20'] = ta.trend.ema_indicator(df['Close'], window=20)
df['RSI'] = ta.momentum.rsi(df['Close'], window=14)

# Support & Resistance (Local Min/Max over 20 periods)
window = 20
df['Support'] = df['Low'].rolling(window=window).min()
df['Resistance'] = df['High'].rolling(window=window).max()

# 4. Buy/Sell Signal Logic with TP/SL
df['Signal'] = "Hold"
df['TP'] = 0.0
df['SL'] = 0.0

for i in range(window, len(df)):
    current_close = df['Close'].iloc[i]
    prev_close = df['Close'].iloc[i-1]
    current_rsi = df['RSI'].iloc[i]
    current_ema = df['EMA_20'].iloc[i]
    current_support = df['Support'].iloc[i-1]
    current_resistance = df['Resistance'].iloc[i-1]
    
    # ATR or basic percentage for TP/SL baseline (using 0.5% for crypto, 0.1% for forex as approximation)
    pct = 0.005 if asset_type == "Crypto" else 0.001
    
    # BUY Signal: Price breaks above EMA, RSI turns bullish (>50), or bounces from support
    if (current_close > current_ema) and (prev_close <= current_ema) and (current_rsi > 50):
        df.at[df.index[i], 'Signal'] = 'BUY'
        df.at[df.index[i], 'SL'] = current_support
        df.at[df.index[i], 'TP'] = current_close + (current_close - current_support) * 1.5
        
    # SELL Signal: Price breaks below EMA, RSI turns bearish (<50), or rejects from resistance
    elif (current_close < current_ema) and (prev_close >= current_ema) and (current_rsi < 50):
        df.at[df.index[i], 'Signal'] = 'SELL'
        df.at[df.index[i], 'SL'] = current_resistance
        df.at[df.index[i], 'TP'] = current_close - (current_resistance - current_close) * 1.5

# Filter latest signals to show on dashboard
latest_signals = df[df['Signal'] != 'Hold'].tail(3)

# 5. Dashboard UI Layout
col1, col2 = st.columns([3, 1])

with col2:
    st.markdown("### 🔔 Latest Signals")
    if not latest_signals.empty:
        for idx, row in latest_signals.iterrows():
            color = "green" if row['Signal'] == 'BUY' else "red"
            st.markdown(f"""
            <div style="border:1px solid {color}; padding:10px; border-radius:5px; margin-bottom:10px;">
                <b style="color:{color};">{row['Signal']} SIGNAL</b><br>
                Time: {idx.strftime('%Y-%m-%d %H:%M')}<br>
                Entry: <b>{row['Close']:.4f}</b><br>
                <span style="color:green;">TP: {row['TP']:.4f}</span> | <span style="color:red;">SL: {row['SL']:.4f}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent setup found. Waiting for confirmation...")

with col1:
    # 6. Interactive Plotly Chart Construction
    fig = ob.Figure()
    
    # Candlestick
    fig.add_trace(ob.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name="Price"
    ))
    
    # Dynamic Support & Resistance Lines (Latest Values)
    current_sup = df['Support'].iloc[-1]
    current_res = df['Resistance'].iloc[-1]
    
    fig.add_hline(y=current_res, line_dash="dash", line_color="red", annotation_text="Resistance")
    fig.add_hline(y=current_sup, line_dash="dash", line_color="green", annotation_text="Support")
    
    # EMA Line
    fig.add_trace(ob.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='orange', width=1.5), name='EMA 20'))
    
    # Buy/Sell Shapes/Markers on Chart
    buys = df[df['Signal'] == 'BUY']
    sells = df[df['Signal'] == 'SELL']
    
    fig.add_trace(ob.Scatter(
        x=buys.index, y=buys['Low'] * 0.999, mode='markers',
        marker=dict(symbol='triangle-up', size=12, color='green'), name='BUY Trigger'
    ))
    fig.add_trace(ob.Scatter(
        x=sells.index, y=sells['High'] * 1.001, mode='markers',
        marker=dict(symbol='triangle-down', size=12, color='red'), name='SELL Trigger'
    ))
    
    # Layout Adjustments
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=600,
        margin=dict(l=10, r=10, t=10, b=10),
        template="plotly_dark"
    )
    
    st.plotly_chart(fig, use_container_width=True)

# 7. RSI Sub-plot
st.markdown("### 📊 Momentum (RSI 14)")
fig_rsi = ob.Figure()
fig_rsi.add_trace(ob.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=1.5), name='RSI'))
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
fig_rsi.update_layout(height=200, template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_rsi, use_container_width=True)
