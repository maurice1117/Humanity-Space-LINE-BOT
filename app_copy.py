from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
# audio message processing
from linebot.models import AudioMessage
from whisper_handler import download_audio, transcribe_audio


import os

from text_handler import handle_text

load_dotenv()

app = Flask(__name__)

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 處理 text 訊息: echo robot
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )

handler.add(MessageEvent, message=TextMessage)(handle_text)

# 定時ping的功能，避免render進入休眠狀態
@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

# ---------------------------------------------------
# 處理 audio 訊息
@handler.add(MessageEvent, message=AudioMessage)
def handle_audio(event):
    try:
        # 1. 下載語音
        message_id = event.message.id
        audio_path = download_audio(message_id, channel_access_token)
        
        # 2. Whisper 轉文字
        transcribe_text = transcribe_audio(audio_path)

        # 3. 回覆語音內容文字（先簡單測試回傳文字）
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"🎙️根據語音辨識結果，您的訊息為：{transcribe_text}")
        )

    except Exception as e:
        print(f"[ERROR] {e}")
