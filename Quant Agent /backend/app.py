"""
app.py – Chronos Stock Backend
Full indicators: SMA, EMA, RSI, MACD, Bollinger Bands
"""

import os, traceback
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

import yfinance as yf
import pandas as pd
import pandas_ta as ta

app = Flask(__name__)
CORS(app)

try:
    from trading_graph import TradingGraph
    QUANTAGENT_AVAILABLE = True
    print("[OK] QuantAgent loaded.")
except Exception as e:
    print(f"[WARNING] QuantAgent not loaded: {e}")
    QUANTAGENT_AVAILABLE = False

INTERVAL_PERIOD_MAP = {
    "1m":"7d","2m":"7d","5m":"60d",
    "15m":"60d","30m":"60d","1h":"730d","1d":"2y",
}

def fetch_ohlcv(symbol: str, interval: str = "5m") -> pd.DataFrame:
    period = INTERVAL_PERIOD_MAP.get(interval, "60d")
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    if df.empty:
        raise ValueError(f"No data for {symbol}")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.dropna(inplace=True)
    df.columns = [c.lower() for c in df.columns]

    # ── Indicators ────────────────────────────────────────────────────────────
    df["SMA"]   = ta.sma(df["close"], length=20)
    df["EMA9"]  = ta.ema(df["close"], length=9)
    df["RSI"]   = ta.rsi(df["close"], length=14)

    # MACD
    macd        = ta.macd(df["close"])
    df["MACD"]  = macd["MACD_12_26_9"]  if macd is not None else None
    df["MACD_S"]= macd["MACDs_12_26_9"] if macd is not None else None
    df["MACD_H"]= macd["MACDh_12_26_9"] if macd is not None else None

    # Bollinger Bands — detect column names dynamically
    bb = ta.bbands(df["close"], length=20, std=2)
    if bb is not None:
        # Column names vary by pandas_ta version — find them safely
        bb_cols = bb.columns.tolist()
        upper = [c for c in bb_cols if c.startswith("BBU")]
        lower = [c for c in bb_cols if c.startswith("BBL")]
        mid   = [c for c in bb_cols if c.startswith("BBM")]
        df["BB_U"] = bb[upper[0]] if upper else None
        df["BB_L"] = bb[lower[0]] if lower else None
        df["BB_M"] = bb[mid[0]]   if mid   else None
    else:
        df["BB_U"] = df["BB_L"] = df["BB_M"] = None

    df.dropna(subset=["SMA","RSI"], inplace=True)
    df.reset_index(inplace=True)
    time_col = "Datetime" if "Datetime" in df.columns else "Date"
    if time_col not in df.columns:
        time_col = df.columns[0]
    df.rename(columns={time_col: "time"}, inplace=True)
    df["time"] = df["time"].astype(str)
    return df

def predict_next_price(df):
    closes     = df["close"].values
    n          = len(closes)
    if n < 20:
        return {"predicted": float(closes[-1]), "confidence": 60}
    last_close = float(closes[-1])
    ema9       = float(df["EMA9"].iloc[-1])
    sma20      = float(df["SMA"].iloc[-1])
    rsi        = float(df["RSI"].iloc[-1])
    momentum   = float((closes[-1] - closes[-6]) / 5) if n >= 6 else 0.0
    predicted  = (0.40*ema9 + 0.20*sma20 + 0.30*last_close + 0.10*(last_close+momentum))
    rsi_score  = 1 - abs(rsi - 50) / 50
    align      = 1 - min(abs(ema9 - sm20) / sma20 * 10, 1)
    confidence = max(55, min(95, int(55 + rsi_score*20 + align*20)))
    return {"predicted": round(predicted, 2), "confidence": confidence}

def df_to_records(df):
    cols = ["time","open","high","low","close","volume",
            "SMA","EMA9","RSI","MACD","MACD_S","MACD_H","BB_U","BB_L","BB_M"]
    # Only include columns that exist
    cols = [c for c in cols if c in df.columns]
    return df[cols].fillna("null").to_dict(orient="records")

@app.route("/chart", methods=["GET"])
def chart():
    symbol   = request.args.get("symbol",   "HDFCBANK.NS")
    interval = request.args.get("interval", "5m")
    try:
        df      = fetch_ohlcv(symbol, interval)
        records = df_to_records(df)
        pred    = predict_next_price(df)
        return jsonify({
            "data":            records,
            "latest_price":    float(df["close"].iloc[-1]),
            "predicted_price": pred["predicted"],
            "confidence":      pred["confidence"],
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e), "data": None}), 500

@app.route("/analyze", methods=["POST"])
def analyze():
    body       = request.get_json(force=True)
    symbol     = body.get("symbol",   "HDFCBANK.NS")
    interval   = body.get("interval", "5m")
    gemini_key = body.get("llm_api_key","") or os.environ.get("GOOGLE_API_KEY","")

    if not gemini_key:
        return jsonify({"error": "No API key. Set GOOGLE_API_KEY in .env"}), 400
    os.environ["GOOGLE_API_KEY"] = gemini_key

    if QUANTAGENT_AVAILABLE:
        try:
            df      = fetch_ohlcv(symbol, interval)
            kline   = df.tail(30).set_index("time")[
                ["open","high","low","close","volume"]
            ].to_dict(orient="index")
            tg          = TradingGraph()
            final_state = tg.graph.invoke({
                "kline_data": kline, "analysis_results": None,
                "messages": [], "time_frame": interval, "stock_name": symbol,
            })
            return jsonify({
                "decision":         final_state.get("final_trade_decision","N/A"),
                "indicator_report": final_state.get("indicator_report","N/A"),
                "pattern_report":   final_state.get("pattern_report","N/A"),
                "trend_report":     final_state.get("trend_report","N/A"),
            })
        except Exception as e:
            traceback.print_exc()
            print(f"[WARNING] QuantAgent failed: {e}")

    # Gemini fallback
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        df   = fetch_ohlcv(symbol, interval)
        pred = predict_next_price(df)
        tail = df.tail(5)[["time","open","high","low","close","SMA","RSI"]].to_string(index=False)
        prompt = f"""Expert stock trader analyzing {symbol} (NSE India).
Last 5 candles:
{tail}
EMA9: ₹{df['EMA9'].iloc[-1]:.2f} | SMA20: ₹{df['SMA'].iloc[-1]:.2f} | RSI: {df['RSI'].iloc[-1]:.1f}
MACD: {df['MACD'].iloc[-1]:.4f} | BB_Upper: ₹{df['BB_U'].iloc[-1]:.2f} | BB_Lower: ₹{df['BB_L'].iloc[-1]:.2f}
Model Prediction: ₹{pred['predicted']} (Confidence: {pred['confidence']}%)

Give SHORT trade decision:
1. Action: LONG/SHORT/HOLD
2. Entry: ₹X  3. Stop Loss: ₹X  4. Target: ₹X
5. Reason: 2 sentences"""
        model    = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return jsonify({
            "decision":         response.text,
            "indicator_report": f"EMA9: ₹{df['EMA9'].iloc[-1]:.2f} | SMA20: ₹{df['SMA'].iloc[-1]:.2f} | RSI: {df['RSI'].iloc[-1]:.1f} | MACD: {df['MACD'].iloc[-1]:.4f}",
            "pattern_report":   f"BB Upper: ₹{df['BB_U'].iloc[-1]:.2f} | BB Lower: ₹{df['BB_L'].iloc[-1]:.2f}",
            "trend_report":     f"Predicted: ₹{pred['predicted']} | Confidence: {pred['confidence']}%",
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status":"ok","quantagent":QUANTAGENT_AVAILABLE})

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)