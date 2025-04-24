from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from dotenv import load_dotenv
from handlers.unified_router import register_handlers
import os

load_dotenv()

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

register_handlers(handler)
#-------------------------------------
# 定時ping的功能，避免render進入休眠狀態
@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200