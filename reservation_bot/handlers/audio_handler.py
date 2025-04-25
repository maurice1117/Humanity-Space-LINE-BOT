from services.whisper_service import download_audio, transcribe_audio
from services.llm_service import is_reservation_request, extract_reservation_info
from services.notify_host import notify_host_reservation
from services.reservation_draft import save_draft
from services.response_builder import text_reply
from linebot import LineBotApi
import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

def handle_audio(event):
    user_id = event.source.user_id
    file_path = download_audio(event.message.id, os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
    text = transcribe_audio(file_path)
    # 如果LLM判斷為預約相關的訊息，則提取相關資訊並儲存草稿
    if is_reservation_request(text):
        reservation = extract_reservation_info(text)
        reservation["user_id"] = user_id
        save_draft(user_id, reservation)
        notify_host_reservation(reservation)
        line_bot_api.reply_message(event.reply_token, text_reply("語音已收到，我們將進行審核處理"))
    else:
        line_bot_api.reply_message(event.reply_token, text_reply("我們已收到您的語音訊息"))
