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
from datetime import datetime, timedelta
import json
import os
import re

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

def handle_confirm_add(event, text):
    """
    處理確認新增預約的指令
    """
    try:
        # 確保 text 不為空，並嘗試解析
        # if not text:
        #     raise ValueError("輸入的文字內容為空，無法處理預約資訊。")

        # reservation = extract_reservation_info(text)
        # if not reservation or not isinstance(reservation, dict):
        #     raise ValueError("無法從輸入文字中解析出有效的預約資訊。")

        # print(f"[純文字草稿內容] {text}")
        # reservation["user_id"] = event.source.user_id
        # reservation["confirmed"] = True
        # finalize_and_save(event.source.user_id, reservation)

        # from services.reservation_draft import update_draft
        # update_draft(user_id=event.source.user_id, **{k: v for k, v in reservation.items() if k != "user_id"})

        reply_text = "✅ 已新增預約並通知使用者"
    except Exception as e:
        import traceback
        print(f"錯誤類型：{type(e).__name__}")
        print(f"錯誤詳情：{traceback.format_exc()}")
        reply_text = f"⚠️ 新增預約失敗：{e}"

    # 回覆錯誤或成功訊息
    reply_with_error(event, reply_text)

def handle_modify(event):
    from services.reservation_draft import get_draft

    try:
        re = get_draft(event.source.user_id)
        print(f"[純文字草稿內容] {re}")
        reply_text = (
            "📝 修改預約：\n\n"
            f"{re.get('name','')} {re.get('start_time','')} {re.get('tel','')} {re.get('memo','')}\n"
        )
    except Exception as e:
        reply_text = f"⚠️ 修改預約失敗：{e}"

    reply_with_error(event, reply_text)

def handle_delete(event):
    from services.reservation_draft import delete_draft

    try:
        delete_draft(event.source.user_id)
        reply_text = "🗑 訂單已刪除"
    except Exception as e:
        reply_text = f"⚠️ 刪除訂單失敗：{e}"

    reply_with_error(event, reply_text)

def handle_unknown_command(event):
    reply_text = (
        "您目前角色為老闆娘，請使用以下指令進行操作：\n"
        "- 查詢本日預約\n"
        "- 查詢明日預約\n"
        "- 查詢預約 [日期] (ex. 查詢預約 2025/5/15)\n"
        "- 查詢客人 [名字] (ex. 查詢客人 小明)\n"
    )
    reply_with_error(event, reply_text)

# 老闆娘查詢本日預約的邏輯
def handle_query_for_today(event):
    today = datetime.now().date()  # 只取日期部分

    reservations = []
    with open("data/reservation.json", "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                date_str = str(data.get("date", ""))
                # 嘗試將 date_str 轉成 datetime 物件
                try:
                    date_obj = datetime.strptime(date_str, "%Y/%m/%d").date()  # 只取日期部分
                except ValueError:
                    # 若格式不同（如 "2025/5/27"），再試一次
                    try:
                        date_obj = datetime.strptime(date_str, "%Y/%m/%d").replace(
                            month=int(date_str.split("/")[1]), day=int(date_str.split("/")[2])
                        ).date()  # 只取日期部分
                    except Exception:
                        date_obj = None
                # 比對日期或關鍵字
                if (date_obj and date_obj == today):
                    reservations.append(data)
            except Exception as e:
                print(f"資料解析錯誤: {e}")

    # 使用共用函數格式化回傳訊息
    reply_text = format_query_text(reservations, f"「{today}」")

    reply_with_error(event, reply_text)

# 老闆娘查詢明日預約的邏輯
def handle_query_for_tomorrow(event):
    tomorrow = (datetime.now() + timedelta(days=1)).date()  # 只取日期部分
    # print(f"查詢明日預約，日期為: {tomorrow}")

    reservations = []
    with open("data/reservation.json", "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                date_str = str(data.get("date", ""))
                # 嘗試將 date_str 轉成 datetime 物件
                try:
                    date_obj = datetime.strptime(date_str, "%Y/%m/%d").date()  # 只取日期部分
                    # print(f"日期解析成功: {date_obj}")
                except ValueError:
                    # 若格式不同（如 "2025/5/27"），再試一次
                    try:
                        date_obj = datetime.strptime(date_str, "%Y/%m/%d").replace(
                            month=int(date_str.split("/")[1]), day=int(date_str.split("/")[2])
                        ).date()  # 只取日期部分
                    except Exception:
                        date_obj = None
                # 比對日期或關鍵字
                if (date_obj and date_obj == tomorrow):
                    reservations.append(data)
            except Exception as e:
                print(f"資料解析錯誤: {e}")

    # 使用共用函數格式化回傳訊息
    reply_text = format_query_text(reservations, f"「{tomorrow}」")

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

    # 使用共用函數格式化回傳訊息
    reply_text = format_query_text(reservations, f"「{query_date}」")

    reply_with_error(event, reply_text)

# 老闆娘查詢客人名字的邏輯
def handle_query_by_name(event, query_text):

    name = query_text.strip()

    reservations = []
    with open("data/reservation.json", "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                # 比對名字（忽略大小寫）
                if name.lower() in str(data.get("name", "")).lower():
                    reservations.append(data)
            except Exception as e:
                print(f"資料解析錯誤: {e}")

    # 使用共用函數格式化回傳訊息
    reply_text = format_query_text(reservations, f"「{name}」")

    reply_with_error(event, reply_text)

# 在傳送確認預約後，使用按鈕選取分店
def handle_select_branch(event, text):
    """
    處理選擇分店的指令
    :param event: LINE 事件物件
    :param text: 使用者輸入的文字
    """
    try:
        # 假設 text 是分店名稱
        branch_name = text.strip()
        if not branch_name:
            raise ValueError("請提供有效的分店名稱。")

        # 儲存分店資訊到暫存資料中
        user_id = event.source.user_id
        save_text_draft(user_id, f"選擇分店: {branch_name}")

        reply_text = f"✅ 已選擇分店：{branch_name}"
    except Exception as e:
        reply_text = f"⚠️ 選擇分店失敗：{e}"

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

def format_query_text(reservations, title):
    """
    格式化預約資料為文字格式，統一包含姓名
    :param reservations: 預約資料列表
    :param title: 回傳訊息的標題
    :return: 格式化的文字訊息
    """
    if not reservations:
        return f"{title} 尚無預約紀錄。"

    reply_text = f"{title} 的預約如下：\n"
    for idx, r in enumerate(reservations, start=1):
        reply_text += (
            f"{idx}. 姓名：{r.get('name', '')}\n"
            f"   日期：{r.get('date', '')}\n"
            f"   時間：{r.get('start_time', '')}\n"
            f"   電話：{r.get('tel', '')}\n"
            f"   備註：{r.get('memo', '')}\n"
        )
    return reply_text