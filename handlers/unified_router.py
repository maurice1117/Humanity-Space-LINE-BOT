# 這個檔案處理所有使用者與管理者的 LINE 訊息
from linebot.models import MessageEvent, TextMessage, AudioMessage, PostbackEvent
from handlers.text_handler import handle_text
# from handlers.audio_handler import handle_audio
from handlers.host_reply_handler import handle_host_reply
from handlers.postback_handler import handle_postback 

def register_handlers(handler):
    handler.add(MessageEvent, message=TextMessage)(handle_text)
    # handler.add(MessageEvent, message=AudioMessage)(handle_audio)
    handler.add(MessageEvent, message=TextMessage)(handle_host_reply)
    handler.add(PostbackEvent)(handle_postback)
