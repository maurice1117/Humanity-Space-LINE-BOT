from .reservation_flow import pad_reservation  # 保持欄位統一

drafts = {}

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
