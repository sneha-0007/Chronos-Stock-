from flask import Flask, request, jsonify
from data_fetcher import fetch_stock_data
from quant_agent import quant_agent_decision
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


@app.route("/")
def home():
    return jsonify({"message": "Chronos Stock Quant API Running"})


@app.route("/predict", methods=["GET"])
def predict():
    symbol = request.args.get("symbol")

    if not symbol:
        return jsonify({"error": "Please provide a stock symbol"}), 400

    df = fetch_stock_data(symbol)

    if df is None:
        return jsonify({"error": "Invalid symbol or no data available"}), 400

    result = quant_agent_decision(df)

    return jsonify({
        "symbol": symbol,
        "action": result["action"],
        "predicted_price": result["predicted_price"]
    })


if __name__ == "__main__":
    app.run(debug=True)
