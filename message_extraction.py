import re

def extract_reservation_data(text):
    try:
        time = re.search(r'時間：(.+)', text).group(1).strip()
        people = re.search(r'人數：(.+)', text).group(1).strip()
        purpose = re.search(r'目的：(.+)', text).group(1).strip()
        note = re.search(r'備註：(.+)', text).group(1).strip()

        return {
            "time": time,
            "people": people,
            "purpose": purpose,
            "note": note
        }
    except AttributeError:
        return None
