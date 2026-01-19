from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import traceback

# ==========================================================
# FIX PYTHON IMPORT PATH (CRITICAL)
# ==========================================================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ==========================================================
# IMPORT PROJECT MODULES
# ==========================================================
from backend.data_fetcher import fetch_stock_data
from ml.preprocess import preprocess_data
from ml.quant_agent import quant_agent_decision

# ==========================================================
# FLASK APP SETUP
# ==========================================================
app = Flask(__name__)
CORS(app)

# ==========================================================
# HEALTH CHECK
# ==========================================================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "CHRONOS Backend",
        "model": "QuantAgent",
        "data_source": "FYERS"
    })

# ==========================================================
# MAIN PREDICTION ENDPOINT
# ==========================================================
@app.route("/predict", methods=["GET"])
def predict():
    try:
        symbol = request.args.get("symbol", "").strip().upper()

        if not symbol:
            return jsonify({
                "error": "Query parameter 'symbol' is required"
            }), 400

        # --------------------------------------------------
        # FETCH DATA FROM FYERS
        # --------------------------------------------------
        df = fetch_stock_data(symbol)

        if df is None or df.empty:
            return jsonify({
                "error": "Failed to fetch data from FYERS",
                "symbol": symbol
            }), 500

        # --------------------------------------------------
        # PREPROCESS DATA
        # --------------------------------------------------
        df = preprocess_data(df)

        if df is None or df.empty:
            return jsonify({
                "error": "Preprocessing failed",
                "symbol": symbol
            }), 500

        # --------------------------------------------------
        # QUANT AGENT DECISION
        # --------------------------------------------------
        decision = quant_agent_decision(df)

        return jsonify({
            "symbol": symbol,
            "action": decision.get("action", "HOLD"),
            "predicted_price": decision.get("predicted_price"),
            "confidence": decision.get("confidence"),
            "model": "QuantAgent",
            "data_source": "FYERS"
        })

    except Exception as e:
        print("❌ ERROR IN /predict")
        traceback.print_exc()

        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


# ==========================================================
# RUN SERVER
# ==========================================================
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
