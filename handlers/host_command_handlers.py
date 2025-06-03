# 用來存放老闆娘的指令處理邏輯的functions
# 服務層
from services.reservation_draft import (
    update_draft, delete_draft, get_text_draft, save_text_draft,get_draft, get_reservation
)
from services.reservation_flow import finalize_and_save, finalize_and_save_modify
from services.response_builder import text_reply, notify_reservation_being_delete, build_delete_confirm_flex
from services.date_extraction import extract_date_from_text
from services.llm_service import extract_reservation_info
from services.notify_customer import notify_user_reservation_confirmed
# linebot
from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage, FlexSendMessage
# 內建
from datetime import datetime, timedelta
import json
import os
import re

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))


def handle_confirm_add(event, draft_id):
    try:
        print(draft_id)
        # 讀取該使用者的暫存預約草稿
        draft = get_draft(draft_id)
        if not draft:
            raise ValueError("找不到該使用者的預約草稿")

        draft["confirmed"] = True
        user_id = draft.get("user_id", "unknown")
        draft.pop("draft_id", None)  # ✅ 加上這行避免重複
        update_draft(draft_id=draft_id, **draft)
        
        # 最終存檔
        finalize_and_save(user_id, draft)    # user id 拿來通知

        reply_text = "✅ 已新增預約並通知使用者"

    except Exception as e:
        import traceback
        print(f"錯誤類型：{type(e).__name__}")
        print(f"錯誤詳情：{traceback.format_exc()}")
        reply_text = f"⚠️ 新增預約失敗：{e}"

    reply_with_error(event, reply_text)
    

# def handle_confirm_add(event, text):
#     """
#     處理確認新增預約的指令
#     """
#     try:
#         # 確保 text 不為空，並嘗試解析
#         # if not text:
#         #     raise ValueError("輸入的文字內容為空，無法處理預約資訊。")

#         # reservation = extract_reservation_info(text)
#         # if not reservation or not isinstance(reservation, dict):
#         #     raise ValueError("無法從輸入文字中解析出有效的預約資訊。")

#         # print(f"[純文字草稿內容] {text}")
#         # reservation["user_id"] = event.source.user_id
#         # reservation["confirmed"] = True
#         # finalize_and_save(event.source.user_id, reservation)

#         # from services.reservation_draft import update_draft
#         # update_draft(user_id=event.source.user_id, **{k: v for k, v in reservation.items() if k != "user_id"})

#         reply_text = "✅ 已新增預約並通知使用者"
#     except Exception as e:
#         import traceback
#         print(f"錯誤類型：{type(e).__name__}")
#         print(f"錯誤詳情：{traceback.format_exc()}")
#         reply_text = f"⚠️ 新增預約失敗：{e}"

#     # 回覆錯誤或成功訊息
#     reply_with_error(event, reply_text)

def handle_modify(event, draft_id):
    from services.reservation_draft import get_draft

    try:
        draft = get_draft(draft_id)
        print(f"[純文字草稿內容] {draft}")
        
        name = draft.get("name", "")
        date = draft.get("date", "")
        time = draft.get("start_time", "")
        tel = draft.get("tel", "")
        memo = draft.get("memo", "")
        
        tip = "請直接複製以下範例並再傳回更改後內容："
        example = f"姓名 {name}\n日期 {date}\n時間 {time}\n電話 {tel}\n備註 {memo}\nId:{draft_id}"
        reply_text = f"{tip}\n{example}"
        
    except Exception as e:
        reply_text = f"⚠️ 修改預約失敗：{e}"

    reply_with_error(event, reply_text)

def handle_modify_input(event, text):
    from services.reservation_draft import get_draft, update_draft

    lines = text.strip().split("\n")
    content = {}

    for line in lines:
        line = line.strip()
        # 支援格式：key [任意空格] [: 或 ： 或 空格] [任意空格] value
        match = re.match(r"^(.*?)\s*[:：]?\s+(.*)$", line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            content[key] = value

    draft_id = content.get("Id")
    if not draft_id:
        line_bot_api.reply_message(
            event.reply_token,
            text_reply("❌ 未提供草稿 ID，請確認格式為 `Id: xxx` 或 `Id xxx`。")
        )
        return

    draft = get_draft(draft_id)
    if not draft:
        line_bot_api.reply_message(
            event.reply_token,
            text_reply(f"找不到對應的預約草稿，請確認 ID 是否正確。\n（嘗試 ID: {draft_id}）")
        )
        return

    # 更新欄位
    draft["name"] = content.get("姓名", draft.get("name", ""))
    draft["date"] = content.get("日期", draft.get("date", ""))
    draft["start_time"] = content.get("時間", draft.get("start_time", ""))
    draft["tel"] = content.get("電話", draft.get("tel", ""))
    draft["memo"] = content.get("備註", draft.get("memo", ""))

    user_id = draft["user_id"]
    draft.pop("draft_id", None)  # 移除多餘欄位
    update_draft(draft_id=draft_id, **draft)
    finalize_and_save_modify(user_id, draft)

    line_bot_api.reply_message(
        event.reply_token,
        text_reply("✅ 預約內容已更新，請確認後再進行新增或其他操作。")
    )

def handle_request_delete(event, draft_id):
    # 根據 draft_id 取得 draft 資料
    draft = get_draft(draft_id)

    # 產生確認刪除用的 Flex message
    flex_json = build_delete_confirm_flex(draft)

    # 用 reply 傳送 Flex Message，請用戶確認
    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(alt_text="請確認是否刪除預約", contents=flex_json)
    )

def handle_delete(event, draft_id):
    # 這才是實際刪除動作
    from services.reservation_draft import delete_draft

    draft = get_draft(draft_id)
    user_id = draft["user_id"]
    try:
        delete_draft(draft_id)
        reply_text = "🗑 訂單已取消"
    except Exception as e:
        reply_text = f"⚠️ 取消訂單失敗：{e}"

    # 推播取消通知給用戶
    text = notify_reservation_being_delete(draft, 1)        
    message = TextSendMessage(text=text)
    line_bot_api.push_message(user_id, message)    # push_message 給user

    # 回覆用戶刪除結果
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )
    
    
# def handle_delete(event, draft_id):
#     from services.reservation_draft import delete_draft

#     draft = get_draft(draft_id)
#     # 產生確認刪除用的 Flex message
#     flex_json = build_delete_confirm_flex(draft)
#     user_id = draft["user_id"]
#     try:
#         delete_draft(draft_id)
#         reply_text = "🗑 訂單已取消"
#     except Exception as e:
#         reply_text = f"⚠️ 取消訂單失敗：{e}"
#     text = notify_reservation_being_delete(draft, 1)        # for user
    
#     message = TextSendMessage(text=text)
#     line_bot_api.push_message(user_id, message)
#     reply_with_error(event, reply_text)    # 回傳給user

def handle_reservation_delete(event, uid):
    # 根據 draft_id 取得 draft 資料
    reservation = get_reservation(uid)
    print(f'reservation是 {reservation}')
    # 產生確認刪除用的 Flex message
    flex_json = build_delete_confirm_flex(reservation)

    # 用 reply 傳送 Flex Message，請用戶確認
    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(alt_text="請確認是否刪除預約", contents=flex_json)
    )

def handle_delete_reservation(event, uid):
    from services.reservation_draft import delete_reservation
    
    reservation = get_reservation(uid)
    user_id = reservation["user_id"]
    # 產生確認刪除用的 Flex message
    
    try:
        delete_reservation(uid)
        reply_text = "🗑 已取消該預約"
    except Exception as e:
        reply_text = f"⚠️ 取消預約失敗：{e}"
    text = notify_reservation_being_delete(reservation, 0)
    
    message = TextSendMessage(text=text)
    line_bot_api.push_message(user_id, message) # 回傳給user
    reply_with_error(event, reply_text)    
    
    
def handle_unknown_command(event):
    reply_text = (
        "您目前角色為老闆娘，請使用以下指令進行操作：\n"
        "- 查詢本日預約\n"
        "- 查詢明日預約\n"
        "- 查詢預約 [日期] (ex. 查詢預約 2025/5/15)\n"
        "- 查詢客人 [名字] (ex. 查詢客人 小明)\n"
        "- 刪除預約 [uid] (ex. 查詢客人 uid)\n"
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

# def

# # 在傳送確認預約後，使用按鈕選取分店
# def handle_select_branch(event, text):
#     """
#     處理選擇分店的指令
#     :param event: LINE 事件物件
#     :param text: 使用者輸入的文字
#     """
#     try:
#         # 假設 text 是分店名稱
#         branch_name = text.strip()
#         if not branch_name:
#             raise ValueError("請提供有效的分店名稱。")

#         # 儲存分店資訊到暫存資料中
#         user_id = event.source.user_id
#         save_text_draft(user_id, f"選擇分店: {branch_name}")

#         reply_text = f"✅ 已選擇分店：{branch_name}"
#     except Exception as e:
#         reply_text = f"⚠️ 選擇分店失敗：{e}"

#     reply_with_error(event, reply_text)

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
            f"{idx}.姓名：{r.get('name', '')}\n"
            f"   電話：{r.get('tel', '')}\n"
            f"   日期：{r.get('date', '')}\n"
            f"   時間：{r.get('start_time', '')}\n"
            f"   分店：{r.get('branch', '')}\n"
            f"   備註：{r.get('memo', '')}\n"
            f"   Id：{r.get('uid', '')}\n"
        )
    return reply_text

