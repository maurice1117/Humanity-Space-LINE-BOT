# host_reply_handler.py
from services.host_control import is_host
from services.reservation_draft import confirm_draft, update_draft, delete_draft
from services.reservation_flow import finalize_and_save
from handlers.audio_handler import handle_audio
from handlers.text_handler import handle_text
from services.reservation_draft import delete_draft
from services.reservation_draft import confirm_draft
from services.reservation_draft import update_draft
from services.response_builder import text_reply
from linebot import LineBotApi
from linebot.models import AudioMessage, TextMessage
from linebot.exceptions import LineBotApiError
import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
host_id = os.getenv("HOST_LINE_ID")


def handle_host_reply(event):
    # 僅允許管理者操作
    if not is_host(event.source.user_id):
        # 非主辦人交給 handle_text 處理（避免吞掉事件）
        try:
            handle_text(event)
        except:
            handle_audio(event)
        return
 
    # 取得輸入文字（語音→文字）
    if isinstance(event.message, AudioMessage):
        text = handle_audio(event).strip()
        print(f"Is audio {text}")
    elif isinstance(event.message, TextMessage):
        user_id = event.source.user_id
        user_text = event.message.text.strip()

        # 主辦人輸入控制指令才執行主辦邏輯，其餘照一般訊息處理
        if user_id == host_id and (
            user_text.startswith("確認新增") or
            user_text.startswith("修改") or
            user_text.startswith("刪除")
        ):
            text = user_text
        else:
            text = handle_text(event).strip()

        print(f"Is text {text}")
    else:
        text = None
    reply_text = ""
    # 根據指令執行
    if text.startswith("確認新增"):
        from services.reservation_draft import get_text_draft
        from services.llm_service import extract_reservation_info
        text_draft = get_text_draft(event.source.user_id)
        reservation = extract_reservation_info(text_draft)
        reservation["user_id"] = event.source.user_id
        reservation["confirmed"] = True
        finalize_and_save(event.source.user_id, reservation)
        from services.reservation_draft import update_draft
        update_draft(user_id=event.source.user_id, **{k: v for k, v in reservation.items() if k != "user_id"})
        reply_text = "✅ 已新增預約並通知使用者"

    elif text.startswith("修改"):
        from services.reservation_draft import get_text_draft
        draft_text = get_text_draft(event.source.user_id)
        print(f"[純文字草稿內容] {draft_text}")
        reply_text = (
            "📝 修改預約：\n\n"
            f"{draft_text}\n"
        )
    

    elif is_host(event.source.user_id):
        from services.reservation_draft import save_text_draft
        from services.llm_service import extract_reservation_info
        try:
            if text.startswith("📝 修改預約"):
                print("這是修改預約的訊息")
                raw_content = text.replace("📝 修改預約", "", 1).strip()
                reservation_info = extract_reservation_info(raw_content)
                preview_lines = [f"{k}: {v}" for k, v in reservation_info.items() if k != "missing"]
                reply_text = (
                    "🔍 以下是解析後的預約內容預覽，請輸入「確認新增」以儲存：\n\n"
                    + "\n".join(preview_lines)
                )
                save_text_draft(event.source.user_id, raw_content)
        except Exception as e:
            reply_text = f"⚠️ 預約內容解析失敗：{e}"
       
    elif text.startswith("刪除"):
        delete_draft(event.source.user_id)
        reply_text = "🗑 草稿已刪除"

    else:
        reply_text = (
            "⚠️ 無法辨識操作，請輸入：\n"
            "1. 確認新增\n"
            "2. 修改 [欄位] [值]\n"
            "3. 刪除"
        )

    try:
        line_bot_api.reply_message(
            event.reply_token,  # Corrected to use reply_token
            text_reply(reply_text)  # Ensure this returns a valid TextSendMessage
        )
    except LineBotApiError as e:
        print(f"❌ 無法回覆訊息，錯誤：{e.status_code} - {e.message}")
