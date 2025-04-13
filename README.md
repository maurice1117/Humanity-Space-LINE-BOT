# Humanity-Space-LINE-BOT

目前部署於 [Render](https://render.com)，並接入 LINE Messaging API。

- Line ID = "@209pldsf"

---

## 專案架構

```
.
├── app.py              # 主程式入口
├── .env                # 環境變數（本地用，請勿上傳）
├── requirements.txt    # 套件清單
├── .gitignore
└── README.md
```


---

## 快速啟動

### 本地測試（開發用）

1. 安裝套件：
   ```bash
   pip install -r requirements.txt
   ```

2. 建立 `.env` 檔（依照 `.env.example`）：
   ```bash
   LINE_CHANNEL_ACCESS_TOKEN=...
   LINE_CHANNEL_SECRET=...
   ```

3. 執行 Flask app：
   ```bash
   python app.py
   ```

---

## `.env` 設定範例（請勿上傳此檔）

```env
LINE_CHANNEL_ACCESS_TOKEN=你的Token
LINE_CHANNEL_SECRET=你的Secret
```

---

### 🌐 Render 部署設定

1. 在 Render 建立 Web Service，連接本專案 Git 分支
2. 設定Environment Variables：
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
3. 設定Start Command：
   ```bash
   gunicorn app:app
   ```
4. Webhook URL 設為：
   ```
   https://你的-service.onrender.com/callback
   ```
5. 前往 LINE Developers Console：
   - 開啟 Use Webhook
   - 貼上 URL 並點 Verify
---

看了一下LINE只能夠貼一個Webhook，所以目前可能暫時只能夠從我這裡進行測試。