from .reservation_flow import pad_reservation  # 保持欄位統一

drafts = {}

# Store unconfirmed plain text reservation drafts
text_drafts = {}

def save_draft(user_id, draft_data):
    drafts[user_id] = pad_reservation(draft_data)

def update_draft(user_id, **kwargs):
    if user_id in drafts:
        drafts[user_id].update(kwargs)
        drafts[user_id] = pad_reservation(drafts[user_id])

def delete_draft(user_id):
    if user_id in drafts:
        del drafts[user_id]

def confirm_draft(user_id):
    return drafts.pop(user_id)

def get_draft(user_id):
    return drafts.get(user_id, {})
# Functions for plain text reservation drafts
def save_text_draft(user_id, text):
    text_drafts[user_id] = text
    print(f"[純文字草稿儲存] 使用者 {user_id} 的草稿已儲存: {text}")

def get_text_draft(user_id):
    return text_drafts.get(user_id, "")

def delete_text_draft(user_id):
    if user_id in text_drafts:
        del text_drafts[user_id]