from linebot.models import FlexSendMessage
from services.reservation_draft import get_draft
from services.response_builder import build_branch_choice_flex
from .host_command_handlers import handle_confirm_add, handle_modify, handle_delete, reply_with_error
from linebot import LineBotApi
import os
from urllib.parse import parse_qs

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

def handle_postback(event):
    data = event.postback.data
    params = parse_qs(data)  # 解析 action=confirm&user_id=xxx 成 dict
    action = params.get("action", [None])[0]
    user_id = params.get("user_id", [None])[0]

    if action == "confirm":
        handle_confirm_add(event, user_id)
    elif action == "edit":
        handle_modify(event, user_id)
    elif action == "delete":
        handle_delete(event, user_id)
    else:
        reply_with_error(event, "⚠️ 無法辨識的操作指令")
