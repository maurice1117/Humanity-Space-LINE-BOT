from linebot.models import FlexSendMessage
from services.reservation_draft import get_draft
from .host_command_handlers import handle_confirm_add, handle_modify, handle_delete, reply_with_error
from services.response_builder import build_branch_selection_flex
from linebot import LineBotApi
import os
from urllib.parse import parse_qs
from services.reservation_draft import (
    update_draft,get_draft
)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

def handle_postback(event):
    data = event.postback.data
    params = parse_qs(data)  # 解析 action=confirm&draft_id=xxx 成 dict
    action = params.get("action", [None])[0]
    draft_id = params.get("draft_id", [None])[0]

    if action == "select_branch":
        # 這裡不回覆訊息，可能只記錄log或更新狀態
        print(f"老闆 開始選擇分店，draft_id: {draft_id}")
        push_message = build_branch_selection_flex(draft_id)
        host_id = os.getenv("HOST_LINE_ID")
        line_bot_api.push_message(host_id, push_message)

    elif action == "confirm":
        branch = params.get("branch", [None])[0]
        if branch:
            draft = get_draft(draft_id)
            if draft:
                draft["branch"] = branch
                draft.pop("draft_id", None)
                update_draft(draft_id, **draft)

                # 執行最終新增動作
                handle_confirm_add(event, draft_id)

                # 如果你想通知用戶，可以用 push message 送，或等下回覆
                # line_bot_api.push_message(event.source.user_id, TextSendMessage(text="預約已新增"))

            else:
                print("找不到該預約草稿")
        else:
            print("尚未選擇分店")

    elif action == "edit":
        handle_modify(event, draft_id)

    elif action == "delete":
        handle_delete(event, draft_id)

    else:
        print("無法辨識的操作指令")