import os
import json
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from linebot import LineBotApi
from response_builder import notify_before_one_day
from search_date import search_tomorrow_reservations, search_two_hour_before_reservations
load_dotenv()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

# 設定 logging
logging.basicConfig(
    filename="data/notifing.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

# 建立 log 輔助函數
def log_info(msg):
    print(msg)
    logging.info(msg)

def log_error(msg):
    print(f"❌ {msg}")
    logging.error(msg)


load_dotenv()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

NOTIFICATION_LOG_PATH = "data/notification_log.json"


def load_notification_log():
    try:
        with open(NOTIFICATION_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"sent_notifications": []}
    except Exception as e:
        log_error(f"載入通知記錄失敗: {e}")
        return {"sent_notifications": []}

def save_notification_log(log_data):
    try:
        os.makedirs(os.path.dirname(NOTIFICATION_LOG_PATH), exist_ok=True)
        with open(NOTIFICATION_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_error(f"儲存通知記錄失敗: {e}")

def is_notification_sent(notification_id):            # check whether is sent or not
    log_data = load_notification_log()
    sent_notifications = log_data.get("sent_notifications", [])
    for notif in sent_notifications:
        if notif.get("notification_id") == notification_id:
            return True
    return False

def mark_notification_sent(notification_id):           # if not,  add it
    log_data = load_notification_log()
    sent_notifications = log_data.setdefault("sent_notifications", [])
    if not any(notif.get("notification_id") == notification_id for notif in sent_notifications):
        sent_notifications.append({
            "notification_id": notification_id,
            "sent_time": datetime.now().isoformat()
        })
        save_notification_log(log_data)

def send_single_notification(reservation, message_builder, notification_type):
    try:
        user_id = reservation.get("user_id")
        notification_id = reservation.get("notification_id")

        if not user_id:
            log_error(f"缺少 user_id: {reservation}")
            return False

        if not notification_id:
            log_error(f"缺少 notification_id: {reservation}")
            return False

        if is_notification_sent(notification_id):
            log_info(f"⏭️ 通知已發送過，跳過: {notification_id}")
            return False

        message = message_builder(reservation)
        line_bot_api.push_message(user_id, message)

        mark_notification_sent(notification_id)

        date = reservation.get("date", "N/A")
        time = reservation.get("start_time", "N/A")
        log_info(f"✅ {notification_type}發送成功: {user_id} - {date}_{time}")
        print(message)
        return True

    except Exception as e:
        log_error(f"{notification_type}發送失敗: {reservation}, 錯誤: {e}")
        return False

def daily_evening_notify():
    log_info("🌙 開始執行每日晚間提醒 (明天預約通知)...")

    tomorrow_reservations = search_tomorrow_reservations()

    if not tomorrow_reservations:
        log_info("📅 明天沒有預約，無需發送提醒")
        return 0

    success_count = 0
    for reservation in tomorrow_reservations:
        if send_single_notification(reservation, notify_before_one_day, "明天預約提醒"):
            success_count += 1

    log_info(f"📊 每日晚間提醒完成: 成功發送 {success_count}/{len(tomorrow_reservations)} 條訊息")
    return success_count


def hourly_check_notify():
    log_info("⏰ 開始檢查兩小時前提醒...")

    two_hour_reservations = search_two_hour_before_reservations()         ## lists

    if not two_hour_reservations:
        log_info("⏰ 兩小時後沒有預約，無需發送提醒")
        return 0

    success_count = 0
    for reservation in two_hour_reservations:        
        if send_single_notification(reservation, notify_before_one_day, "兩小時前提醒"):
            success_count += 1

    log_info(f"📊 兩小時前提醒完成: 成功發送 {success_count}/{len(two_hour_reservations)} 條訊息")
    return success_count


def cleanup_old_notifications(days_to_keep=30):
    try:
        log_data = load_notification_log()
        sent_notifications = log_data.get("sent_notifications", [])

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        # 篩選出 sent_time >= cutoff_date 的通知
        filtered_notifications = []
        for notif in sent_notifications:
            sent_time_str = notif.get("sent_time")  # 假設這是 ISO 格式字串
            if not sent_time_str:
                continue  # 沒有時間欄位的通知，可以選擇保留或丟棄
            try:
                sent_time = datetime.fromisoformat(sent_time_str)
                if sent_time >= cutoff_date:
                    filtered_notifications.append(notif)
            except Exception:
                # 如果時間格式錯誤，預設保留
                filtered_notifications.append(notif)

        log_data["sent_notifications"] = filtered_notifications
        save_notification_log(log_data)

        log_info(f"🧹 清理舊通知記錄完成，保留最近 {days_to_keep} 天的通知，清理前共 {len(sent_notifications)} 條，清理後共 {len(filtered_notifications)} 條")
    except Exception as e:
        log_error(f"清理通知記錄失敗: {e}")


# 測試主程式
if __name__ == "__main__":
    log_info("=== 測試通知功能 ===")

    daily_count = daily_evening_notify()

    log_info("\n" + "=" * 50 + "\n")

    hourly_count = hourly_check_notify()

    log_info(f"\n總計發送: {daily_count + hourly_count} 條通知")