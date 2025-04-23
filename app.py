from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from reservation_service import notify_admin
from message_extraction import extract_reservation_data
from dotenv import load_dotenv
import os
import re


load_dotenv()

app = Flask(__name__)

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
