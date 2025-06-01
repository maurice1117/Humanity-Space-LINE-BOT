import json
from services.notify_customer import notify_user_reservation_confirmed

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

def finalize_and_save(user_id,reservation_data):
    save_reservation_to_json(reservation_data)
    notify_user_reservation_confirmed(user_id, reservation_data)
