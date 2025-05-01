from datetime import datetime, timedelta
import json


def load_reservations(path = "J:\Humanity-Space-LINE-BOT\\reservation_bot\data\\reservation.json"):
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

def normalize_date(date_str):
    try:
        parts = date_str.split("/")
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
        dt = datetime(year, month, day)
        return dt.strftime("%Y/%m/%d")
    except:
        return date_str  # 如果轉換失敗，就保留原始字串

def search_data_date():
    notify_list = []
    reservations_data = load_reservations()
    now = datetime.now()
    tomorrow = (now+timedelta(days=1)).strftime("%Y/%m/%d")   ## 明天
    for r in reservations_data:
        date = normalize_date(r.get("date"))

        if date == tomorrow:
            notify_list.append(r)
            
    return notify_list

