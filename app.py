from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from reservation_service import notify_admin
from message_extraction import extract_reservation_data
from dotenv import load_dotenv
from datetime import datetime
import json
import os
import re


load_dotenv()

app = Flask(__name__)
CORS(app)

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


# === Routes ===

@app.route("/callback", methods=['POST', 'GET'])
def callback():
    if request.method == 'GET':
        return "Callback endpoint is alive"

    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    print("Webhook triggered")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature")
        abort(400)

    return 'OK'

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

@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200


# === Message Handlers ===

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    print(f"使用者 user_id 為：{event.source.user_id}")
    if "我要預約" in text:
        reservation_data = extract_reservation_data(text)
        if reservation_data:
            notify_admin(reservation_data, event.source.user_id)
            reply_text = "預約已收到，我們會盡快處理！"
        else:
            reply_text = "預約格式錯誤，請確認格式是否為：\n時間：...\n人數：...\n目的：...\n備註：..."
    else:
        reply_text = text  # Echo 使用者的訊息

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

# === Entry point ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
