from linebot import LineBotApi
from .response_builder import notify_before_one_day
import os
from dotenv import load_dotenv
from .search_date import search_data_date
load_dotenv()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

def daily_notify():
    
    notify_list = search_data_date()
    for reservation in notify_list:
        try:
            user_id = reservation.get("user_id")
            if not user_id:
                continue
            message = notify_before_one_day(reservation)
            line_bot_api.push_message(user_id, message)
        except Exception as e:
            print(f"❌ 推播失敗，reservation: {reservation}, error: {e}")


## 測試
# if __name__ == "__main__":
#     daily_notify()