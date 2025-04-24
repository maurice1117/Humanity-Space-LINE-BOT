# LINE 預約系統機器人 Reservation Bot

這是一個模組化設計的 LINE Bot 專案，可接收使用者透過文字或語音進行預約，並由管理者在 LINE 上審核、備註與確認，最終儲存格式化資料。

支援功能包含：

- 語音訊息 → Whisper 轉文字
- LLM 判斷是否為預約相關訊息
- 管理者收到預約草稿後可直接用 LINE 回覆進行確認、修改、刪除
- 備註欄可透過語音回覆
- 使用 RAG（人性空間資訊.txt）補強客戶偏好欄位
- 最終資料以 JSONL 形式儲存

---

## 📁 專案結構說明

reservation_bot/
├── app.py                            # 主入口，處理 webhook 並註冊 handler
├── handlers/                         # 處理使用者與管理者的 LINE 訊息
│   ├── unified_router.py            # 註冊 Text、Audio、Admin 訊息
│   ├── text_handler.py              # 處理使用者文字訊息
│   ├── audio_handler.py             # 處理語音訊息 → Whisper 轉文字
│   └── admin_reply_handler.py       # 管理者的審核、修改、刪除與語音備註
├── services/                         # 處理邏輯功能模組
│   ├── whisper_service.py           # Whisper 語音轉文字工具
│   ├── llm_service.py               # 判斷是否為預約 + 抽取資料
│   ├── notify_admin.py              # 推播草稿通知給管理者
│   ├── notify_customer.py           # 推播「預約已確認」通知給使用者
│   ├── reservation_flow.py          # 格式化資料 + 儲存 JSON + 通知
│   ├── reservation_draft.py         # 暫存草稿（記憶體內 dict）
│   ├── response_builder.py          # 產生文字或 Flex 訊息格式
│   └── admin_control.py             # 驗證是否為管理者帳號
├── data/
│   ├── reservation.json             # 所有預約紀錄會寫入這個 JSONL 檔
│   └── RAG_enhancer.py              # 加入 RAG 處理
├── static/audio/                    # 暫存下載語音檔用於 Whisper 轉換
├── .env                             # 儲存 LINE Channel Token、管理者 ID
├── requirements.txt                 # 所有套件需求

---

## 🚀 快速啟動（本地測試）

```
pip install -r requirements.txt
python app.py
```

**測試中可使用 [ngrok](https://ngrok.com/) 暴露本機 port 以對接 LINE Webhook**

```
ngrok http 5000
```

---

## ☁️ 雲端部署（Render）

1. **建立 Web Service，連接 Git 分支**
2. **設定環境變數（如上）**
3. **設定啟動指令：**

```
gunicorn app:app
```

4. **將 Render 網址貼到 LINE Developers Console 的 Webhook URL**

---

## ✅ 管理者審核操作指令

**管理者收到 Flex 預約通知後，可直接在 LINE 對話中回覆：**

* **確認新增** → 寫入 JSON 並通知使用者
* **修改 電話 0933xxxxxx** → 更新草稿中的欄位
* **刪除** → 刪除該筆草稿
* **語音備註 → 自動轉文字後填入 **memo** 欄位**

---

## 🧠 補充功能：RAG 個人化補強

* **檔案路徑：**data/人性空間資訊.txt
* **格式建議（每行一筆）：**

```
王小明：吃素、過敏海鮮、常來
0912xxxxxx：喜歡靠窗
```

* 
* **系統會自動比對姓名或電話並補充進 memo 欄**

---

## 🛠️ 未來擴充建議

* **草稿快取使用 Redis（防止記憶體重啟遺失）**
* **加入 LLM 自動回答用戶非預約訊息**
* **管理者多角色支援（多個 LINE ID）**
