drafts = {}

def save_draft(user_id, draft_data):
    drafts[user_id] = draft_data

def update_draft(user_id, **kwargs):
    if user_id in drafts:
        drafts[user_id].update(kwargs)

def delete_draft(user_id):
    if user_id in drafts:
        del drafts[user_id]

def confirm_draft(user_id):
    return drafts.pop(user_id)
