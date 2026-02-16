from flask import Flask, request, jsonify
from config import Config
from data_fetcher import fetch_stock_data
from preprocess import preprocess_data
from quant_agent import quant_agent_decision

app = Flask(__name__)
app.config.from_object(Config)


@app.route("/")
def home():
    return jsonify({"message": "Chronos Quant Stock API Running"})


@app.route("/predict", methods=["GET"])
def predict():
    symbol = request.args.get("symbol")

    if not symbol:
        return jsonify({"error": "Please provide a stock symbol"}), 400

    df = fetch_stock_data(symbol)
    df = preprocess_data(df)

    if df is None:
        return jsonify({"error": "Invalid symbol or insufficient data"}), 400

    result = quant_agent_decision(df)

    return jsonify({
        "symbol": symbol,
        "action": result["action"],
        "predicted_price": result["predicted_price"]
    })


if __name__ == "__main__":
    app.run(debug=True)
