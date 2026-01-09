from flask import Flask, request, jsonify
from flask_cors import CORS
from data_fetcher import fetch_stock_data
from preprocess import preprocess_data
from quant_agent import quant_agent_decision

app = Flask(__name__)
CORS(app)

@app.route("/predict", methods=["GET"])
def predict():
    symbol = request.args.get("symbol")

    if not symbol:
        return jsonify({"error": "Stock symbol required"}), 400

    df = fetch_stock_data(symbol)
    if df is None:
        return jsonify({"error": "Data fetch failed"}), 500

    df = preprocess_data(df)
    result = quant_agent_decision(df)

    return jsonify({
        "symbol": symbol,
        "action": result["action"],
        "predicted_price": result["predicted_price"]
    })

if __name__ == "__main__":
    app.run(debug=True)
