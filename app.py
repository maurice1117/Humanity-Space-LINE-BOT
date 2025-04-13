from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('Z+llILjkg9Vnn4ARo3PFU8rDgsW5QeW61znOSXIvG1NrJ2icoNad867GhgmUzKeLRqybUhnXabEUAzBs11ZgvXldXBe3VvuRITL792wC1ZgcVuvPSiQqBkes5bGPL+Sczrs/WVGx2zcMt6Rf3AkUEwdB04t89/1O/w1cDnyilFU='))
handler = WebhookHandler(os.getenv('99df85c3a61d7082c15bb4928b531399'))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# echo robot
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )