import json
import pandas as pd

# 讀取多行 JSON 檔案
file_path = "reservation_bot/data/reservation.json"

try:
    with open(file_path, "r", encoding="utf-8") as file:
        data = [json.loads(line) for line in file]
except FileNotFoundError:
    print(f"Error: The file {file_path} was not found.")
    data = []
except json.JSONDecodeError as e:
    print(f"Error: Failed to decode JSON. {e}")
    data = []

# 將資料轉換為 DataFrame
df = pd.DataFrame(data)

# 嘗試將 "date" 欄位轉換為 datetime 格式
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# 再次檢查資料類型
print(df.dtypes)

# 檢視資料
print(df.head())