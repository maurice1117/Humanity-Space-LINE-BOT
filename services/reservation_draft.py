import json
import os
from .reservation_flow import pad_reservation  # 讓欄位統一格式

DRAFT_FILE = "data/drafts.json"
FINAL_FILE = "data/reservation.json"

# -------- 工具方法 --------
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_draft_id(user_id, date, start_time):
    # 把 date 裡的 / 全部換成 -
    safe_date = date.replace("/", "-")
    # 把 start_time 的冒號換成 -
    safe_start_time = start_time.replace(":", "-")
    return f"{user_id}_{safe_date}_{safe_start_time}"


# -------- 草稿操作 --------
def save_draft(user_id, draft_data):
    drafts = load_json(DRAFT_FILE)
    draft_data = pad_reservation(draft_data)
    date = draft_data.get("date", "未提供")
    start_time = draft_data.get("start_time", "未提供")
    draft_id = generate_draft_id(user_id, date, start_time)

    draft_data["user_id"] = user_id  # ⚠️ 確保草稿中有 user_id
    draft_data["draft_id"] = draft_id  # ⚠️ 寫入 draft_id 欄位

    # 檢查是否已有同樣的 draft_id，更新它
    drafts = [d for d in drafts if d["draft_id"] != draft_id]
    drafts.append(draft_data)
    save_json(DRAFT_FILE, drafts)

def update_draft(draft_id, **kwargs):
    drafts = load_json(DRAFT_FILE)
    for i, draft in enumerate(drafts):
        if draft.get("draft_id") == draft_id:
            kwargs.pop("draft_id", None)  # 移除避免重複
            drafts[i].update(kwargs)
            drafts[i] = pad_reservation(drafts[i])
            break
    save_json(DRAFT_FILE, drafts)

def get_draft(draft_id):
    drafts = load_json(DRAFT_FILE)
    for draft in drafts:
        print(draft["draft_id"])
        print(draft_id)
        if draft["draft_id"] == draft_id:
            return draft
    return {}

def delete_draft(draft_id):
    drafts = load_json(DRAFT_FILE)
    drafts = [d for d in drafts if d["draft_id"] != draft_id]
    save_json(DRAFT_FILE, drafts)


# -------- 額外：簡易文字備份 --------
text_drafts = {}

def save_text_draft(user_id, text):
    text_drafts[user_id] = text

def get_text_draft(user_id):
    return text_drafts.get(user_id, "")

def delete_text_draft(user_id):
    if user_id in text_drafts:
        del text_drafts[user_id]

# from .reservation_flow import pad_reservation  # 保持欄位統一

# drafts = {}

# # Store unconfirmed plain text reservation drafts
# text_drafts = {}

# def save_draft(user_id, draft_data):
#     drafts[user_id] = pad_reservation(draft_data)
#     # print(f"[草稿儲存] 使用者 {user_id} 的草稿已儲存: {drafts[user_id]}")

# def update_draft(user_id, **kwargs):
#     if user_id in drafts:
#         drafts[user_id].update(kwargs)
#         drafts[user_id] = pad_reservation(drafts[user_id])

# def delete_draft(user_id):
#     if user_id in drafts:
#         del drafts[user_id]

# def confirm_draft(user_id):
#     return drafts.pop(user_id)

# def get_draft(user_id):
#     return drafts.get(user_id, {})
# # Functions for plain text reservation drafts
# def save_text_draft(user_id, text):
#     text_drafts[user_id] = text

# def get_text_draft(user_id):
#     return text_drafts.get(user_id, "")

# def delete_text_draft(user_id):
#     if user_id in text_drafts:
#         del text_drafts[user_id]