import json
from services.notify_customer import notify_user_reservation_confirmed, notify_user_reservation_confirmed_modify

DEFAULT_KEYS = ["name", "tel", "date", "start_time", "branch", "memo"]

def pad_reservation(data):       
    for key in DEFAULT_KEYS:
        if key not in data:
            data[key] = ""
    return data
    
def save_reservation_to_json(data: dict, path="data/reservation.json"):
    data = pad_reservation(data)  # 寫入前補齊欄位
    with open(path, "a", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")

def get_user_short_id(user_id: str) -> str:
    return user_id[:4].upper()  # 取前四碼並大寫

def finalize_and_save(user_id, reservation_data):
    date = reservation_data.get("date", "unknown")  # 例如 "2025/06/08"
    time = reservation_data.get("start_time", "unknown")  # 例如 "14:00"
    branch = reservation_data.get("branch", "X")
    
    # 取 MMDD
    mmdd = date.replace("/", "")[-4:] if len(date) >= 5 else "0000"
    # 取 HHMM
    hhmm = time.replace(":", "")[:4] if len(time) >= 4 else "0000"
    # 取 user_id 前四碼
    user_short = get_user_short_id(user_id)

    reservation_id = f"{branch[0].upper()}{mmdd}-{hhmm}-{user_short}"
    reservation_data["uid"] = reservation_id
    
    save_reservation_to_json(reservation_data)
    notify_user_reservation_confirmed(user_id, reservation_data)

def finalize_and_save_modify(user_id,reservation_data):
    date = reservation_data.get("date", "unknown")  # 例如 "2025/06/08"
    time = reservation_data.get("start_time", "unknown")  # 例如 "14:00"
    branch = reservation_data.get("branch", "X")
    
    # 取 MMDD
    mmdd = date.replace("/", "")[-4:] if len(date) >= 5 else "0000"
    # 取 HHMM
    hhmm = time.replace(":", "")[:4] if len(time) >= 4 else "0000"
    # 取 user_id 前四碼
    user_short = get_user_short_id(user_id)

    reservation_id = f"{branch[0].upper()}{mmdd}-{hhmm}-{user_short}"
    reservation_data["uid"] = reservation_id
    save_reservation_to_json(reservation_data)
    notify_user_reservation_confirmed_modify(user_id, reservation_data)
