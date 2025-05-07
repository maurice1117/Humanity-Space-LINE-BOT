# text_handler.py
from services.llm_service import is_reservation_request, extract_reservation_info
from services.reservation_draft import save_draft
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
        try:
            # 嘗試提取完整的預約資訊
            reservation = extract_reservation_info(text)
            reservation['user_id'] = user_id

            # 儲存預約資訊
            save_draft(user_id, reservation)
            from services.reservation_draft import save_text_draft
            save_text_draft(user_id, text)

            # 通知店主
            notify_host_reservation(reservation)

            # 回覆使用者
            line_bot_api.reply_message(
                event.reply_token,
                text_reply("✅ 您的預約資訊已收到，請稍候老闆娘確認")
            )
        except Exception:
            # 如果提取失敗，請求使用者重新提供資訊
            line_bot_api.reply_message(
                event.reply_token,
                text_reply("🌟 看起來您有預約需求，但目前無法辨識完整資訊，請回傳以下格式\n姓名:\n電話:\n預約日期與時間:\n其他:")
            )
        return text

    # 如果不是預約需求，回覆預設訊息
    line_bot_api.reply_message(
        event.reply_token,
        text_reply("我們已收到您的文字訊息")
    )
    return text