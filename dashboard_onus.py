import streamlit as st
import pandas as pd
import requests
import ta
import matplotlib.pyplot as plt

# --- Hàm lấy dữ liệu từ ONUS ---
@st.cache_data(ttl=60*5)
def fetch_onus_data(symbol='BTCVNDC', interval='1h', limit=200):
    url = "https://api-gateway-app.onuschain.io/market/candlestick"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params)
    raw = response.json()['data']

    df = pd.DataFrame(raw, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.set_index('timestamp').astype(float)
    return df

# --- Hàm tạo tín hiệu ---
def generate_signals(df):
    df['MA20'] = ta.trend.sma_indicator(df['close'], window=20)
    df['RSI'] = ta.momentum.rsi(df['close'], window=14)
    df['MACD'] = ta.trend.macd_diff(df['close'])

    buy, sell = [], []
    for i in range(len(df)):
        if df['close'][i] > df['MA20'][i] and df['RSI'][i] < 30 and df['MACD'][i] > 0:
            buy.append(df['close'][i])
            sell.append(None)
        elif df['close'][i] < df['MA20'][i] and df['RSI'][i] > 70 and df['MACD'][i] < 0:
            buy.append(None)
            sell.append(df['close'][i])
        else:
            buy.append(None)
            sell.append(None)

    df['Buy_Signal'] = buy
    df['Sell_Signal'] = sell
    return df

# --- Giao diện Streamlit ---
st.set_page_config(page_title="Crypto Dashboard ONUS", layout="wide")
st.title("📈 Crypto Buy/Sell Dashboard (ONUS Data)")

# Lựa chọn người dùng
coin = st.selectbox("Chọn cặp coin:", ["BTCVNDC", "ETHVNDC", "BNBVNDC"])
interval = st.selectbox("Chọn khung thời gian:", ["15m", "1h", "4h", "1d"])
limit = st.slider("Số lượng nến (candles):", 50, 500, 200)

# Lấy dữ liệu và phân tích
df = fetch_onus_data(symbol=coin, interval=interval, limit=limit)
df = generate_signals(df)

# Hiển thị biểu đồ giá
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(df['close'], label='Giá đóng cửa', alpha=0.8)
ax.plot(df['MA20'], label='MA20', linestyle='--')
ax.scatter(df.index, df['Buy_Signal'], label='Mua', color='green', marker='^')
ax.scatter(df.index, df['Sell_Signal'], label='Bán', color='red', marker='v')
ax.set_title(f"Tín hiệu giao dịch cho {coin}")
ax.legend()
ax.grid()

st.pyplot(fig)

# Hiển thị bảng dữ liệu mới nhất
st.subheader("📋 Dữ liệu mới nhất")
st.dataframe(df.tail(10).style.format({'close': '{:,.0f}', 'RSI': '{:.2f}'}))
