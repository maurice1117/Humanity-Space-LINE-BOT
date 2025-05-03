from services.llm_service import is_reservation_request, extract_reservation_info
from services.notify_host import notify_host_reservation
from services.reservation_draft import save_draft
from services.response_builder import text_reply
from linebot import LineBotApi
import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

def handle_text(event):
    text = event.message.text.strip()
    user_id = event.source.user_id

    if is_reservation_request(text):
        reservation = extract_reservation_info(text)
        reservation['user_id'] = user_id
        save_draft(user_id, reservation) # 到這步的邏輯都一樣
        notify_host_reservation(reservation) # 通知老闆後的處理看一下
        line_bot_api.reply_message(event.reply_token, text_reply("🌟 看起來您有預約需求，稍後老闆會進行確認"))
    else:
        line_bot_api.reply_message(event.reply_token, text_reply("我們已收到您的文字訊息"))
