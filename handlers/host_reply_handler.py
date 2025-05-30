# 服務層
from services.host_control import is_host
from services.reservation_draft import (
    confirm_draft, update_draft, delete_draft, get_text_draft, save_text_draft
)
from services.reservation_flow import finalize_and_save
from services.response_builder import text_reply
from services.date_extraction import extract_date_from_text
from services.llm_service import extract_reservation_info

# handler
# from handlers.audio_handler import handle_audio
from handlers.text_handler import handle_text
from handlers.host_command_handlers import (handle_confirm_add, handle_modify, handle_delete, handle_unknown_command, handle_query_by_date, handle_query_by_name, handle_query_for_today
                                   , handle_query_for_tomorrow, reply_with_error)
# linebot
from linebot import LineBotApi
from linebot.models import AudioMessage, TextMessage
from linebot.exceptions import LineBotApiError

# 內建
from datetime import datetime
import json
import os
import re

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
host_id = os.getenv("HOST_LINE_ID")


def handle_host_reply(event):
    # 僅允許管理者操作
    if not is_host(event.source.user_id): # 可以暫時刪掉not用來測試guest的邏輯
        # 非主辦人交給 handle_text 處理（避免吞掉事件）
        print("非主辦人")
        handle_text(event)
        # except:
        #     handle_audio(event)
        return

    # 取得輸入文字（語音→文字）
    text = get_event_text(event)
    if not text:
        reply_with_error(event, "⚠️ 無法處理的訊息類型")
        return

    for cmd, (handler, need_text) in COMMAND_HANDLERS.items():
        if text.startswith(cmd):
            if need_text:
                handler(event, event.message.text[len(cmd):].strip())
            else:
                handler(event)
            return

    # 如果沒有符合的指令，則回覆錯誤訊息
    handle_unknown_command(event)

def get_event_text(event):
    # if isinstance(event.message, AudioMessage):
    #     return handle_audio(event).strip()
    if isinstance(event.message, TextMessage):
        return event.message.text.strip()
    return None


# 指令與對應的處理函數，標記是否需要帶入text
COMMAND_HANDLERS = {
    "確認新增": (handle_confirm_add, True),
    "修改": (handle_modify, False),
    "刪除": (handle_delete, False),
    "查詢本日預約": (handle_query_for_today, False),
    "查詢今日預約": (handle_query_for_today, False),
    "查詢今天預約": (handle_query_for_today, False),
    "查詢明日預約": (handle_query_for_tomorrow, False),
    "查詢明天預約": (handle_query_for_tomorrow, False),
    "查詢預約": (handle_query_by_date, True),
    "查詢客人": (handle_query_by_name, True),
}