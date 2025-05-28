from linebot import LineBotApi
from services.response_builder import build_reservation_flex
import os
from dotenv import load_dotenv
from linebot.exceptions import LineBotApiError
import json
load_dotenv()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

def notify_host_reservation(reservation: dict):
    host_id = os.getenv("HOST_LINE_ID")
    message = build_reservation_flex(reservation)
    line_bot_api.push_message(host_id, message)