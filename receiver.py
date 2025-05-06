from flask import Flask, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

@app.route("/api/reservation", methods=["POST"])
def create_reservation():
    data = request.json

    print("Received data:", data)

    # 驗證資料
    if not data.get("name") or not data.get("tel") or not data.get("date"):
        return jsonify({"message": "Missing required fields"}), 400

    # 驗證日期格式
    try:
        datetime.strptime(data["date"], "%Y/%m/%d")
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY/MM/DD"}), 400

    # 儲存資料（這裡可以儲存到檔案或資料庫）
    with open("data/data.json", "a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")

    return jsonify({"message": "Reservation created successfully"}), 201

if __name__ == "__main__":
    app.run(debug=True)