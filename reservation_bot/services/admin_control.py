import os

def is_admin(user_id: str) -> bool:
    return user_id == os.getenv("ADMIN_USER_ID")
