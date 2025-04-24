from linebot import LineBotApi
from services.response_builder import build_reservation_flex
import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

def notify_admin_reservation(reservation: dict):
    admin_id = os.getenv("ADMIN_USER_ID")
    message = build_reservation_flex(reservation)
    line_bot_api.push_message(admin_id, message)
