import os

def is_host(user_id: str) -> bool:
        if os.getenv("HOST_LINE_ID") == user_id:
            return True
