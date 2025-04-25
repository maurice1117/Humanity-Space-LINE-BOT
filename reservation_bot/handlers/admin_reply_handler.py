# 這個檔案專門用來處理老闆在收到預約相關訊息後加memo的部分。
# 老闆可以修改預約資訊或是刪除預約草稿，然後可以加上memo。原則上老闆用語音或文字都可以。
from services.host_control import is_host
from services.reservation_draft import confirm_draft, update_draft, delete_draft
from services.reservation_flow import finalize_and_save
from services.whisper_service import download_audio, transcribe_audio
from services.response_builder import text_reply
from linebot import LineBotApi
from linebot.models import AudioMessage, TextMessage
import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
host_id = os.getenv("HOST_LINE_ID")

def handle_admin_reply(event):
    user_id = event.source.user_id
    print(f"🔐 收到來自 {user_id} 的訊息，內容: {event.message.text}")
    if is_host(user_id):
        print(f"（💅由管理者傳送）")        

    if isinstance(event.message, AudioMessage):
        file_path = download_audio(event.message.id, os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
        memo = transcribe_audio(file_path)
        update_draft(user_id, memo=memo)
        line_bot_api.reply_message(event.reply_token, text_reply("已收到語音備註並更新"))
        # notify the host (there is only 1 host)
        line_bot_api.push_message(host_id, text_reply(f"🔔 使用者 {user_id} 傳送語音訊息：「{memo}」"))

    elif isinstance(event.message, TextMessage):
        text = event.message.text.strip()
        print(f"🔐 收到來自 {user_id} 的文字訊息，內容: {text}")
        line_bot_api.push_message(host_id, text_reply(f"🔔 使用者 {user_id} 傳送文字訊息：「{text}」"))
        if text.startswith("確認新增"):
            reservation = confirm_draft(user_id)
            finalize_and_save(user_id, reservation)
            line_bot_api.reply_message(event.reply_token, text_reply("✅ 已新增預約並通知使用者"))
            
        elif text.startswith("修改"):
            _, key, value = text.split(" ", 2)
            update_draft(user_id, **{key: value})
            line_bot_api.reply_message(event.reply_token, text_reply(f"✏️ 已更新 {key} 為 {value}"))
            line_bot_api.push_message(host_id, text_reply(f"🔔 使用者 {user_id} 修改 {key} 為 {value}"))

        elif text.startswith("刪除"):
            delete_draft(user_id)
            line_bot_api.reply_message(event.reply_token, text_reply("🗑 草稿已刪除"))
            line_bot_api.push_message(host_id, text_reply(f"🔔 使用者 {user_id} 刪除預約草稿"))
            
        else:
            line_bot_api.reply_message(event.reply_token, text_reply("無法辨識操作"))
        