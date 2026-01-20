import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, request, jsonify
from flask_cors import CORS

from fyers_auth import get_fyers_client
from data_fetcher import get_historical_data
from ml.quant_agent import predict_prices   # ✅ FIXED NAME

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return {"status": "CHRONOS backend running"}


@app.route("/broker/profile", methods=["GET"])
def broker_profile():
    """
    FYERS used ONLY where permissions are allowed
    """
    fyers = get_fyers_client()
    return fyers.get_profile()


@app.route("/predict", methods=["GET"])
def predict():
    """
    Yahoo Finance → QuantAgent
    NO FYERS historical calls here (avoids permission issue)
    """
    try:
        symbol = request.args.get("symbol")
        if not symbol:
            return jsonify({"error": "Symbol required"}), 400

        # Yahoo Finance data
        df = get_historical_data(symbol)

        # ML Prediction
        result = predict_prices(df)

        return jsonify({
            "symbol": symbol,
            "actual": result["actual"],
            "predicted": result["predicted"],
            "timestamps": result["timestamps"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
