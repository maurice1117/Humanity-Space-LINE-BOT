import re
from datetime import datetime, timedelta

def extract_date_from_text(text):
    # 支援 yyyy/m/d 或 yyyy/mm/dd
    match = re.search(r'(\d{4}/\d{1,2}/\d{1,2})', text)
    if match:
        return match.group(1)
    # 也可擴充支援「今天」、「明天」等
    if "今天" in text:
        return datetime.now().strftime("%Y/%m/%d")
    if "明天" in text:
        return (datetime.now() + timedelta(days=1)).strftime("%Y/%m/%d")
    return None