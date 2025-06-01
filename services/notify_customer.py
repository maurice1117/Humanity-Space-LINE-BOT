from linebot import LineBotApi
from linebot.models import TextSendMessage
from dotenv import load_dotenv
import os
load_dotenv()
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

def notify_user_reservation_confirmed(user_id, reservation):
    name = reservation.get("name", "顧客")
    date = reservation.get("date", "未提供")
    memo = reservation.get("memo", "無")
    start_time = reservation.get("start_time", "無")

    text = f"您好{name}，您的預約已確認：\n日期：{date}\n時間：{start_time}\n備註：{memo}"
    message = TextSendMessage(text=text)
    line_bot_api.push_message(user_id, message)