# text_handler.py
from services.llm_service import is_reservation_request, extract_reservation_info
from services.reservation_draft import save_draft, save_text_draft
from services.notify_host import notify_host_reservation
from services.response_builder import text_reply
from linebot import LineBotApi
import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

# 暫存使用者進入預約流程的狀態
user_stage = {}

def handle_text(event):
    text = event.message.text.strip()
    user_id = event.source.user_id

    # 檢查是否為預約需求
    if is_reservation_request(text):
        print(f"🔍 偵測到預約需求: {text}")
        handle_reservation_request(event, text, user_id)
    elif text.startswith("索取預約格式"):
        print(f"🔍 偵測到索取預約格式: {text}")
        reply_to_user(event, "🌟 請回傳以下格式:\n我要預約\n姓名:\n電話:\n預約日期與時間:\n備註:")
    else:
        handle_default_response(event)

def handle_reservation_request(event, text, user_id):
    try:
        # 提取預約資訊
        reservation = extract_reservation_info(text)
        reservation['user_id'] = user_id

        # 儲存預約資訊
        save_reservation_draft(user_id, reservation, text)

        # 通知店主
        notify_host_reservation(reservation)

        # 回覆使用者
        reply_to_user(event, "✅ 您的預約資訊已收到，請稍候老闆娘確認")
    except Exception as e:
        print(f"❌ 提取預約資訊失敗：{e}")
        reply_to_user(event, "🌟 看起來您有預約需求，但目前無法辨識完整資訊，請回傳以下格式\n姓名:\n電話:\n預約日期與時間:\n其他:")        

def save_reservation_draft(user_id, reservation, text):
    save_draft(user_id, reservation)
    save_text_draft(user_id, text)

def reply_to_user(event, message):
    try:
        line_bot_api.reply_message(
            event.reply_token,
            text_reply(message)
        )
    except Exception as e:
        print(f"❌ 回覆使用者失敗：{e}")

def handle_default_response(event):
    reply_to_user(event, "我們已收到您的文字訊息")