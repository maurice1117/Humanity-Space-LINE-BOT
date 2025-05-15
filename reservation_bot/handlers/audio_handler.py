
# audio_handler.py
from services.whisper_service import download_audio, transcribe_audio
from services.llm_service import is_reservation_request, extract_reservation_info
from services.reservation_draft import save_draft
from services.notify_host import notify_host_reservation
from services.response_builder import text_reply
from linebot import LineBotApi
import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

def handle_audio(event):
    user_id = event.source.user_id
    # 下載並轉寫語音
    file_path = download_audio(event.message.id, os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
    text = transcribe_audio(file_path).strip()

    # 處理預約需求
    if is_reservation_request(text):
        reservation = extract_reservation_info(text)
        reservation['user_id'] = user_id
        save_draft(user_id, reservation)
        notify_host_reservation(reservation)
        line_bot_api.reply_message(
            event.reply_token,
            text_reply("🌟 聽起來您有預約需求，稍後老闆會進行確認")
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            text_reply("我們已收到您的語音訊息")
        )
    return text
