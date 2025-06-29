from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "ONUS Proxy API Running"

@app.route('/api/onus-candles')
def onus_proxy():
    symbol = request.args.get('symbol', 'BTCVNDC')
    interval = request.args.get('interval', '1h')
    limit = request.args.get('limit', '200')

    url = 'https://api-gateway-app.onuschain.io/market/candlestick'
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
