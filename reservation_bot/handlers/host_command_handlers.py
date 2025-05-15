# 用來存放老闆娘的指令處理邏輯的functions
# 服務層
from services.reservation_draft import (
    confirm_draft, update_draft, delete_draft, get_text_draft, save_text_draft
)
from services.reservation_flow import finalize_and_save
from services.response_builder import text_reply
from services.date_extraction import extract_date_from_text
from services.llm_service import extract_reservation_info

# linebot
from linebot import LineBotApi
from linebot.exceptions import LineBotApiError

# 內建
from datetime import datetime
import json
import os
import re

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

def handle_confirm_add(event):

    try:
        text_draft = get_text_draft(event.source.user_id)
        reservation = extract_reservation_info(text_draft)
        reservation["user_id"] = event.source.user_id
        reservation["confirmed"] = True
        finalize_and_save(event.source.user_id, reservation)

        from services.reservation_draft import update_draft
        update_draft(user_id=event.source.user_id, **{k: v for k, v in reservation.items() if k != "user_id"})

        reply_text = "✅ 已新增預約並通知使用者"
    except Exception as e:
        reply_text = f"⚠️ 新增預約失敗：{e}"

    reply_with_error(event, reply_text)

def handle_modify(event):
    from services.reservation_draft import get_text_draft

    try:
        draft_text = get_text_draft(event.source.user_id)
        print(f"[純文字草稿內容] {draft_text}")
        reply_text = (
            "📝 修改預約：\n\n"
            f"{draft_text}\n"
        )
    except Exception as e:
        reply_text = f"⚠️ 修改預約失敗：{e}"

    reply_with_error(event, reply_text)

def handle_delete(event):
    from services.reservation_draft import delete_draft

    try:
        delete_draft(event.source.user_id)
        reply_text = "🗑 草稿已刪除"
    except Exception as e:
        reply_text = f"⚠️ 刪除草稿失敗：{e}"

    reply_with_error(event, reply_text)

def handle_unknown_command(event):
    reply_text = (
        "⚠️ 無法辨識操作，請輸入：\n"
        "- 確認新增\n"
        "- 修改 [欄位] [值]\n"
        "- 刪除"
        "- 查詢本日預約 (若要查詢本日預約)\n"
        "- 查詢預約 [日期] (ex. 查詢預約 2025/5/15)\n"
        "- 查詢客人 [名字] (ex. 查詢客人 小明)\n"
    )
    reply_with_error(event, reply_text)

# 老闆娘查詢本日預約的邏輯
def handle_query_for_today(event):
    today = datetime.now().strftime("%Y/%m/%d")
    today_keywords = ["今天", "today"]

    reservations = []
    with open("data/reservation.json", "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                date_str = str(data.get("date", ""))
                # 判斷是否為今天
                if today in date_str or any(kw in date_str for kw in today_keywords):
                    reservations.append(data)
            except Exception as e:
                print(f"資料解析錯誤: {e}")

    if not reservations:
        reply_text = "今天尚無預約紀錄。"
    else:
        reply_text = "今日預約如下：\n"
        for r in reservations:
            reply_text += f"{r.get('name','')} {r.get('start_time','')} {r.get('tel','')} {r.get('memo','')}\n"

    reply_with_error(event, reply_text)

# 老闆娘查詢任意日期預約的邏輯
def handle_query_by_date(event, query_text):
    query_date = extract_date_from_text(query_text)
    if not query_date:
        reply_with_error(event, "請輸入正確的日期格式（如 2025/5/20）或使用「今天」、「明天」等關鍵字。")
        return

    reservations = []
    with open("data/reservation.json", "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                date_str = str(data.get("date", ""))
                if query_date in date_str:
                    reservations.append(data)
            except Exception as e:
                print(f"資料解析錯誤: {e}")

    if not reservations:
        reply_text = f"{query_date} 尚無預約紀錄。"
    else:
        reply_text = f"{query_date} 預約如下：\n"
        for r in reservations:
            reply_text += f"{r.get('name','')} {r.get('start_time','')} {r.get('tel','')} {r.get('memo','')}\n"

    reply_with_error(event, reply_text)

# 老闆娘查詢客人名字的邏輯
def handle_query_by_name(event, query_text):
    # 從輸入文字中擷取名字（假設格式為：查詢客人 [名字]）
    match = re.search(r"查詢客人\s*(\S+)", query_text)
    if not match:
        reply_with_error(event, "請輸入正確格式，例如：查詢客人 小明")
        return
    name = match.group(1)

    reservations = []
    with open("data/reservation.json", "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if name.lower() in str(data.get("name", "")).lower():
                    reservations.append(data)
            except Exception as e:
                print(f"資料解析錯誤: {e}")

    if not reservations:
        reply_text = f"查無「{name}」的預約紀錄。"
    else:
        reply_text = f"「{name}」的預約如下：\n"
        for r in reservations:
            reply_text += f"{r.get('date','')} {r.get('start_time','')} {r.get('tel','')} {r.get('memo','')}\n"

    reply_with_error(event, reply_text)

def reply_with_error(event, message):
    try:
        line_bot_api.reply_message(
            event.reply_token,
            text_reply(message)
        )
    except LineBotApiError as e:
        print(f"❌ 無法回覆訊息，錯誤代碼：{e.status_code}")
        print(f"❌ 錯誤訊息：{e.message}")
    except Exception as e:
        print(f"⚠️ 未知錯誤：{type(e).__name__} - {e}")