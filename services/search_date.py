from datetime import datetime, timedelta
import json


def load_reservations(path = "data\\reservation.json"):
##(path="data/reservation.json"):
    reservations = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                reservations.append(data)
            except:
                continue
    return reservations

def normalize_date(date_str, start_time_str):
    try:
        parts = date_str.split("/")
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
        # dt = datetime(year, month, day)
        # return dt.strftime("%Y/%m/%d")
        # 處理時間格式 (假設格式是 "14:30" 或 "14:00")
        if ":" in start_time_str:
            time_parts = start_time_str.strip().split(":")
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            
            # # 處理 12 小時制
            # if "PM" in start_time_str and hour != 12:
            #     hour += 12
            # elif "AM" in start_time_str and hour == 12:
            #     hour = 0
                
            return datetime(year, month, day, hour, minute)
        else:
            hour, minute = 0, 0  # 若無時間，預設為午夜
            return datetime(year, month, day, hour, minute)
    except:
        return None

def search_tomorrow_reservations():
    """搜尋明天的預約 (每天晚上10點發送)"""
    reservations_data = load_reservations()
    now = datetime.now()
    tomorrow = now.date() + timedelta(days=1)
    
    tomorrow_list = []
    for user in reservations_data:
        date = normalize_date(user.get("date", ""), user.get("start_time",""))
        # print(date)
        # print(tomorrow)
        if isinstance(date, datetime) and date.date() == tomorrow:
            # 為每個預約添加唯一識別
            user['notification_id'] = f"daily_{user.get('user_id')}_{date}"
            tomorrow_list.append(user)
    
    return tomorrow_list

def search_two_hour_before_reservations():
    """搜尋2小時後的預約 (每次執行時檢查)"""
    reservations_data = load_reservations()
    now = datetime.now()   
    start_time = now 
    end_time = now + timedelta(hours=2)
    
    two_hour_list = []
    for user in reservations_data:
        reservation_datetime = normalize_date(user.get("date", ""), user.get("start_time", ""))
        # print(reservation_datetime)
        # print(start_time)
        # print(end_time)
        if not isinstance(reservation_datetime, datetime):
            continue
            
        if start_time <= reservation_datetime <= end_time:
            user['notification_id'] = f"hourly_{user.get('user_id')}_{reservation_datetime}"
            two_hour_list.append(user)

    return two_hour_list


def search_data_date():
    """搜尋明天的預約 (保持原有功能)"""
    return search_tomorrow_reservations()


# 測試函數
if __name__ == "__main__":
    print("明天的預約:")
    tomorrow_reservations = search_data_date()
    for r in tomorrow_reservations:
        print(r['notification_id'])
        print(f"  {r.get('user_id')} - {r.get('date')} {r.get('start_time')}")
    
    print("\n兩小時後的預約:")
    one_hour_reservations = search_two_hour_before_reservations()
    for r in one_hour_reservations:
        print(r['notification_id'])
        print(f"  {r.get('user_id')} - {r.get('date')} {r.get('start_time')}")
        
        
# def search_data_date(hours_ahead):
#     notify_list = []
#     reservations_data = load_reservations()
#     now = datetime.now()
#     tomorrow = (now+timedelta(days=1)).strftime("%Y/%m/%d")   ## 明天
#     for r in reservations_data:
#         date = normalize_date(r.get("date"))

#         if date == tomorrow:
#             notify_list.append(r)
            
#     return notify_list

