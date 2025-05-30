from linebot.models import TextSendMessage
from linebot import LineBotApi
import os
from services.reservation_draft import user_temp_data  # 使用你已設的暫存 dict

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

def handle_postback_event(event):
    data = event.data
    user_id = event.source.user_id
    selected_time = event.postback.params.get("datetime")

    if data.startswith("action=select_datetime") and selected_time:
        user_temp_data[user_id] = {"datetime": selected_time}
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"你選擇的時間是：{selected_time}\n請輸入姓名與電話，例如：王小明 0912345678")
        )