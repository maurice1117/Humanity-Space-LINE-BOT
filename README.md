
### 一、專案概述

「`reservation_bot`」是一個基於 LINE Messaging API 的多功能聊天機器人專案，主要用於自動化處理「預約（reservation）」相關流程。使用者可以透過文字或語音在 LINE 群組／私人對話中提出預約請求，機器人會自動辨識意圖、擷取必要資訊、生成預約草稿，並將草稿推送給管理者審核。管理者在 LINE 中執行相關指令後，機器人會將最終確認訊息回覆給使用者。此外，專案還內建提醒功能，可在指定時間（例如預約時間前兩小時或隔日）自動發送通知。

### 二、主要功能

1. **文字與語音訊息處理**

   * 使用者可直接以文字輸入預約資訊。
   * 使用者亦可透過附件語音，機器人會先透過 Whisper 將語音轉為文字，再進行後續處理。

2. **預約意圖判斷與資訊擷取**

   * 透過內部整合的 LLM（大型語言模型）服務，判斷使用者訊息是否為「預約」相關。
   * 抽取關鍵資料（如預約日期、時間、人數、需求等），並以 JSON 格式暫存為「預約草稿」。

3. **預約草稿審核流程**

   * 當機器人產生一份新的預約草稿後，自動推播（push）「待審核草稿」給管理者 LINE 帳號。
   * 管理者可使用特定指令（如「同意」、「駁回」等）來核准或取消預約。
   * 一旦管理者確認，機器人會將「預約已確認」的通知推播給該位使用者。

4. **預約資料儲存與查詢**

   * 所有正式通過的預約紀錄會以 JSONL（JSON Lines）格式寫入 `data/reservation.json`，方便日後查閱或做統計。
   * 檔案型式：每一行是一個獨立的 JSON 物件，包含預約者 ID、預約時間、備註、狀態等欄位。

5. **定時提醒機制**

   * 利用 `services/notify_text.py` 中的定時查詢（`search_date.py`），每天自動搜尋「明日」以及「兩小時後」將有預約的使用者。
   * 系統若偵測到符合條件的預約，就會自動發送「預約提醒」給該使用者。
   * 成功或失敗的推播紀錄會記錄至 `data/notifing.log` 與 `data/notification_log.json`。

6. **管理者權限驗證**

   * `services/host_control.py` 負責檢查發送訊息者是否為管理者（由 `.env` 中設定的管理者 ID 列表），避免非管理者誤用審核指令。

7. **環境設定與相依套件**

   * `.env`：儲存 LINE Channel Token、管理者 ID 等機密變數。
   * `requirements.txt`：列出 Python 相依套件（如 `flask`、`line-bot-sdk`、`openai-whisper`、`langchain` 等），執行 `pip install -r requirements.txt` 即可安裝所有需求。

---

### 三、專案架構與檔案說明

```
reservation_bot/
├── app.py                            # 主入口：設定 Flask Webhook，註冊各種 handler
├── handlers/                         # 處理使用者與管理者的 LINE 訊息
│   ├── unified_router.py             # 統一路由：將文字、語音、管理者訊息導向對應 handler
│   ├── text_handler.py               # 使用者文字訊息處理：呼叫 llm_service 提取預約資訊
│   ├── audio_handler.py              # 使用者語音訊息處理：先下載語音，再呼叫 whisper_service
│   ├── host_reply_handler.py         # 管理者訊息處理：辨識審核指令並回覆結果
│   └── host_command_handlers/        # 管理者各項子指令實作（如同意、駁回、查詢預約清單等）
├── services/                         # 商業邏輯模組（服務層）
│   ├── whisper_service.py            # Whisper API 包裝：將音檔轉文字
│   ├── llm_service.py                # LLM 判斷與資料抽取：確認是否為預約、擷取日期、時間等欄位
│   ├── notify_admin.py               # 推播草稿通知給管理者：組成提醒內容並呼叫 LINE API
│   ├── notify_customer.py            # 推播「預約已確認」通知給使用者
│   ├── reservation_flow.py           # 預約流程控制：格式化資料、暫存 JSON、觸發通知
│   ├── reservation_draft.py          # 暫存草稿：將抽取到的預約資料保存在記憶體中的字典結構
│   ├── response_builder.py           # 組裝 LINE 訊息回覆：文字訊息與 Flex Message 格式
│   ├── timepicker.py                 # 視覺化選擇日期：產生可互動的按鈕或日期時間選單
│   ├── notify_text.py                # 定時提醒主控制：查詢符合條件的預約並發送提醒
│   │   └── search_date.py            # 協助函式：搜尋「明日」與「兩小時後」的預約資料
│   └── host_control.py               # 管理者認證：檢查發訊者是否為管理者
├── data/                             # 資料儲存與記錄
│   ├── reservation.json              # 正式預約紀錄：JSONL 格式，一行一筆資料
│   ├── RAG_enhancer.py               # （可選）反向檢索增強模組：對 LLM 提供知識來源
│   ├── notifing.log                  # 推播紀錄（純文字 log）
│   └── notification_log.json         # 推播詳細紀錄：包含發送失敗原因等欄位
├── static/                           # 靜態資源
│   └── audio/                        # 暫存下載的語音檔，供 Whisper 處理
├── .env                              # 環境變數：LINE Channel Token、管理者 ID、Whisper/LLM API 金鑰等
├── requirements.txt                  # Python 套件需求清單
└── README.md                         # 專案說明（範例，可自行補充）
```

#### 1. `app.py`

* 使用 Flask 或其他輕量 Web 框架作為 HTTP server，主要職責是：

  1. 監聽 LINE Webhook（`/callback` 路由）。
  2. 初始化 LINE Bot SDK 的 `LineBotApi` 與 `WebhookHandler`。
  3. 把來自 LINE 伺服器的事件分派給 `handlers/unified_router.py` 進行下一步處理。

#### 2. `handlers/` 目錄

* **`unified_router.py`**

  * 統一處理來自使用者或管理者的事件（包含文字訊息、語音訊息、以及 JSON 格式的系統事件）。
  * 依據事件屬性（`message.type`、`event.source.userId` 是否為管理者等）決定呼叫哪個 handler。

* **`text_handler.py`**

  * 處理使用者傳送的文字訊息：

    1. 呼叫 `llm_service.py`，判斷是否為「我要預約」的意圖。
    2. 若為預約意圖，從文字中抽取日期、時間、人數等欄位。
    3. 將抽取結果存到 `reservation_draft.py` 的暫存草稿。
    4. 呼叫 `notify_admin.py` 推播草稿給管理者等待審核。

* **`audio_handler.py`**

  * 處理使用者傳送的語音（Voice）訊息：

    1. 接收到包含 `audio` 的 `event`，先下載 `.m4a` 或 `.aac` 檔至 `static/audio/`。
    2. 呼叫 `whisper_service.py`，使用 Whisper 模型將語音轉為文字。
    3. 將轉成文字後的結果丟給 `text_handler.py` 以統一流程處理。

* **`host_reply_handler.py`**

  * 處理管理者在 LINE 中的文字回覆／指令：

    1. 檢查發送者是否通過 `host_control.py` 驗證。
    2. 根據特定關鍵字（如「同意 #id」、「駁回 #id」）呼叫對應的 `host_command_handlers` 中的函式。
    3. 函式會更新 `reservation.json`（例如把草稿狀態標記為已確認），並將結果回覆給使用者或管理者。

* **`host_command_handlers/`**

  * 儲存各種管理者指令的具體實作函式，例如：

    * `approve_reservation(id)`: 通過預約，更新檔案並發送「已確認」通知。
    * `reject_reservation(id, reason)`: 拒絕預約，並將原因回覆給使用者。
    * `list_pending_reservations()`: 列出所有待審核的草稿清單。
    * ……

#### 3. `services/` 目錄

* **`whisper_service.py`**

  * 封裝 Whisper API 的呼叫邏輯。
  * 輸入：本機音檔路徑。
  * 輸出：Whisper 轉寫後的文字結果。

* **`llm_service.py`**

  * 封裝與 LLM（如 OpenAI GPT 系列／其他自建模型）的互動邏輯。
  * 主要功能：

    1. **意圖分類**：根據文字內容，判斷是否為「預約」相關。
    2. **槽位抽取**：將文字中的關鍵資訊（日期、時間、人數、備註等）提取為結構化資料。
  * 通常會接收「純文字內容」，回傳一個 Python `dict`，包含抽取後的欄位。

* **`notify_admin.py`**

  * 組裝將「待審核草稿」透過 LINE 推播給管理者的 Flex Message 或文字訊息。
  * Flex Message 可以包含：

    * 預約者名稱／ID
    * 期望預約日期與時段
    * 人數／需求說明
    * 快速操作按鈕（例如「同意」、「駁回」）

* **`notify_customer.py`**

  * 在管理者「同意」或「駁回」後，將最終結果透過 LINE 推播給使用者。
  * 若「同意」，訊息內容通常包括：

    * 預約時間確認
    * 注意事項
    * 取消方式等

* **`reservation_flow.py`**

  * 負責串聯整個預約流程的核心邏輯：

    1. 接收 `llm_service` 回傳的結構化資料。
    2. 依需求建構「預約草稿」物件，並呼叫 `reservation_draft.py` 儲存暫存。
    3. 呼叫 `notify_admin.py` 通知管理者。
    4. 監聽管理者審核結果，若通過則呼叫 `notify_customer.py`，並寫入 `data/reservation.json`。
    5. 若被駁回，則回覆使用者「很抱歉，您的預約未通過審核」並可選擇重新填寫。

* **`reservation_draft.py`**

  * 以 Python 字典或其他簡單資料結構（如 `dict[id] = draft_data`）暫時保留各筆預約草稿，直到管理者審核完成。
  * 可以搭配 TTL（time-to-live）機制，若草稿逾時（如 1 天內未審核），則自動清除或通知使用者重新申請。

* **`response_builder.py`**

  * 用於生成各種 LINE 訊息格式：

    1. **文字訊息（`TextSendMessage`）**
    2. **Flex Message**
    3. **Buttons Template、Confirm Template**（若需要簡單互動按鈕）

* **`timepicker.py`**

  * 提供一套前端（Flex）日期／時間選擇器的組件範本，使用者點擊後可直接選擇「今天」、「明天」或「自訂日期」。
  * 透過 Flex Message 的 quick reply 或 carousel 形式，提升使用者體驗。

* **`notify_text.py`**

  * 負責定時任務的主邏輯，例如：每天凌晨自動執行一次，去 `data/reservation.json` 中搜尋「明天」有預約的使用者。

  * 以及執行「預約時間前兩小時」的第二輪提醒。

  * 如果發現符合條件者，統一呼叫 `notify_customer.py` 發送「提醒」訊息。

  * **`search_date.py`**

    * 協助 `notify_text.py` 計算「明日日期」與「兩小時後時間區間」，並回傳符合條件的預約資料列表。

* **`host_control.py`**

  * 從 `.env` 讀取「管理者 ID 列表」。
  * 對於所有管理者專屬指令（例如審核、查詢總表、手動發送提醒等），先檢查 `event.source.userId` 是否在管理者名單中。
  * 若非管理者，回覆「您沒有使用此功能的權限」。

#### 4. `data/` 目錄

* **`reservation.json`**

  * 正式的預約紀錄，以 JSONL 格式（一行一筆 JSON）存放。
  * 每筆內容範例：

    ```jsonc
    {"id": "abc123", "userId": "Uxxxxxxxxx", "name": "王小明", "date": "2025-06-10", "time": "14:30", "people": 3, "note": "需要無障礙空間", "status": "confirmed", "timestamp": "2025-06-05T12:00:00+08:00"}
    ```
  * `status` 欄位可為 `"pending"`、`"confirmed"`、`"rejected"` 等。

* **`RAG_enhancer.py`**

  * 若專案需要在回答中加入「反向檢索增強（RAG）」，此模組可負責連結外部知識庫（如 QA 文件集），在 LLM 推斷意圖時提供更多上下文。
  * 具備將「使用者輸入」與「RAG 文檔」結合的預處理流程。

* **`notifing.log`**

  * 紀錄推播（push）成功或失敗的文字 log，例如：

    ```
    [2025-06-05 01:00:00] 推播成功：提醒發送給 Uxxxxxxxxx
    [2025-06-05 01:00:05] 推播失敗：Uyyyyyyyyy 請求逾時
    ```

* **`notification_log.json`**

  * 更結構化的推播紀錄 JSON，包含使用者 ID、訊息類型（提醒、確認、拒絕）、發送時間、狀態、失敗原因（若有）等欄位。

#### 5. `static/audio/` 目錄

* 存放從 LINE 伺服器下載下來的語音檔，待 `whisper_service.py` 處理完畢後可定期清除，避免佔用空間過大。

#### 6. `.env` 檔案

```
LINE_CHANNEL_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LINE_CHANNEL_ACCESS_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ADMIN_USER_IDS=U1234567890abcdef,U0987654321fedcba   # 可用逗號分隔多個管理者
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

* 將上述環境變數放在 `.env`，執行時可使用 `python-dotenv` 或其他套件載入。

#### 7. `requirements.txt`

* 將所有套件及版本寫在此檔，範例：

  ```
  flask==2.1.0
  line-bot-sdk==2.0.1
  openai-whisper==1.0.0
  openai==0.29.0
  python-dotenv==0.21.0
  langchain==0.0.88
  ```
* 使用者只要執行：

  ```bash
  pip install -r requirements.txt
  ```

  即可自動安裝專案所需的所有 Python 套件。

---

### 四、資料流程示意

1. **使用者端（User → Bot）**

   * 使用者在 LINE 群組或私聊中輸入文字：「我想要預約明天下午兩點，三位用餐」。
     或者：使用者錄製語音：「我要預約 6 月 10 號 18:00，五人包廂」，並傳送至機器人。

2. **Line 伺服器 → `app.py`**

   * LINE Webhook 事件觸發，由 Flask 的 `/callback` 接收。

3. **`unified_router.py` → 選擇對應 Handler**

   * 如果是文字訊息：轉到 `text_handler.py`。
   * 如果是語音訊息：先轉到 `audio_handler.py`，再由 Whisper 服務轉成文字，最終送到 `text_handler.py`。

4. **`text_handler.py`**

   * 呼叫 `llm_service.py`：

     * 判斷意圖（是否為預約）。
     * 進行槽位抽取（抽出「日期」、「時間」、「人數」、「備註」等）。
   * 抽取成功後，呼叫 `reservation_flow.py` 建立草稿。

5. **`reservation_flow.py` → `reservation_draft.py`**

   * 生成一筆草稿（包含上述抽取到的資訊和使用者 ID），存到記憶體的字典中。
   * 透過 `notify_admin.py` 組裝訊息並推播給所有管理者。

6. **管理者端（Host）**

   * 管理者在 LINE 上收到「預約草稿」的 Flex Message，點擊「同意」或輸入「同意 #草稿ID」。
   * 此事件回到 `host_reply_handler.py`，並由 `host_command_handlers` 中的函式處理：

     * 更新 `reservation.json`：把草稿資料以 JSONL 通常一行一筆的方式寫入（狀態為 `confirmed`）。
     * 呼叫 `notify_customer.py` 組裝「您的預約已確認」訊息，發給使用者。

7. **定時提醒**

   * `notify_text.py`（透過排程，例如每天 00:00 觸發）會執行：

     * 呼叫 `search_date.py`：找出「明天」有預約的所有使用者，並發送「提醒訊息」。
     * 接著找出「兩小時後」的預約，發送第二波提醒。
   * 成功／失敗資訊寫入 `notifing.log` 與 `notification_log.json`。

8. **結束**

   * 使用者收到提醒後，若臨時要取消，可以再主動傳訊息，機器人再次進行流程（判斷為「取消預約」意圖 → 將原本存的 `reservation.json` 中該筆預約狀態設為 `cancelled` → 通知管理者與使用者）。

---

### 五、技術重點與特色

1. **Whisper 語音轉文字**

   * 讓使用者可直接以語音提出預約需求，擴大使用情境。
   * 對於長音檔或語速語調較快的語音，Whisper 具備較高的辨識率。

2. **LLM 意圖與槽位抽取**

   * 借助 GPT 系列或其他 NLP 模型，大幅提升「中文自然語言」的意圖辨識與資訊抽取能力。
   * 可靈活擴充至更多語意理解場景（如查詢可用時段、修改預約、刪除預約等）。

3. **Flex Message + 按鈕互動**

   * 針對管理者審核與使用者選擇時間，提供豐富的 Flex 版面，提升使用體驗。
   * 使用者點擊「選擇日期」按鈕後，可由 `timepicker.py` 組裝動態日期選單，直接選擇當日可用時段，避免手動輸入錯誤。

4. **彈性化草稿與審核流程**

   * `reservation_draft.py` 透過短期暫存方式（Memory Cache），可讓使用者先自行確認草稿內容，並有機會在管理者介入前修改或取消。
   * 草稿逾時可自動清除，避免殘留大量未處理資料。

5. **定時提醒與推播日誌**

   * `notify_text.py` 結合 `search_date.py`，每天自動偵測並提醒明日與兩小時後的使用者，減少遺忘情形。
   * 所有提醒行為都有完善的 log 紀錄（`notifing.log`、`notification_log.json`），方便日後稽核與排查錯誤。

6. \*\*環境與安全

   * **`.env` 管理敏感資訊**：將 LINE Channel Token、OpenAI API Key、管理者 ID 等機密放在環境變數，避免硬編碼在程式碼中。
   * **管理者權限驗證**：`host_control.py` 嚴格檢查所有管理者專屬指令，避免非管理者濫用審核功能。
   * **JSONL 儲存結構**：`reservation.json` 採用一行一筆獨立 JSON，方便後續使用 `jq`、Pandas 或其他工具做批次處理與統計分析。

---

## English Description

### 1. Project Overview

The **`reservation_bot`** is a LINE-based chatbot application designed to automate the entire reservation workflow. Clients (users) can create reservation requests via text or voice messages in LINE. The bot automatically detects reservation intents, extracts required information, generates a reservation “draft,” and notifies administrators for approval. Once an administrator approves or rejects a draft, the bot sends a confirmation or rejection message back to the user. Additionally, the bot has a built-in reminder system that automatically sends notifications to users: for example, a day before and two hours before their confirmed reservation.

### 2. Key Features

1. **Text & Voice Message Handling**

   * Users can send reservation requests as plain text.
   * They can also record and send voice messages; Whisper converts speech to text automatically.

2. **Intent Recognition & Slot Extraction**

   * An integrated LLM (Large Language Model) service determines if the incoming message is a “reservation” intent.
   * The bot extracts key fields (e.g., date, time, number of people, special requests) from user input and stores them temporarily as a “draft.”

3. **Draft Approval Flow**

   * Once a draft is generated, the bot pushes a “Pending Approval” notification to administrators (via LINE).
   * Administrators can approve or reject requests by issuing specific commands (e.g., “Approve #draftID” or “Reject #draftID”).
   * Upon approval, the bot stores the reservation permanently and notifies the user of the confirmation.
   * If rejected, the user receives a rejection message with optional instructions to reapply.

4. **Data Persistence & Query**

   * Confirmed reservations are saved in `data/reservation.json` using JSONL (JSON Lines) format—each line is a standalone JSON record.
   * Each record contains fields such as user ID, reservation timestamp, status, and any additional notes for future reference or analytics.

5. **Automated Reminder System**

   * The script `services/notify_text.py` periodically (e.g., daily at midnight) scans `reservation.json` for reservations happening the next day or in two hours.
   * Matching entries trigger automatic reminder messages sent to users.
   * All push notifications, successes, and failures are logged to `data/notifing.log` and `data/notification_log.json`.

6. **Administrator Authentication**

   * `services/host_control.py` enforces an authentication check: only user IDs listed in `.env` as administrators can execute admin commands (e.g., approve or reject).

7. **Environment Configuration & Dependencies**

   * `.env` stores LINE Channel Token, admin user IDs, and Whisper/LLM API keys.
   * `requirements.txt` lists all Python dependencies (e.g., Flask, line-bot-sdk, openai-whisper, langchain). Installing is as simple as `pip install -r requirements.txt`.

---

### 3. Project Structure & File Descriptions

```
reservation_bot/
├── app.py                            # Entry point: sets up Flask webhook and registers handlers
├── handlers/                         # Modules for handling user and admin LINE messages
│   ├── unified_router.py             # Registers routes for Text, Audio, Admin events
│   ├── text_handler.py               # Handles user text messages
│   ├── audio_handler.py              # Handles user voice messages → Whisper transcription
│   ├── host_reply_handler.py         # Handles admin messages and commands
│   └── host_command_handlers/        # Functions backing admin command handling
├── services/                         # Business logic / service-layer modules
│   ├── whisper_service.py            # Wrapper for Whisper speech-to-text
│   ├── llm_service.py                # Intent detection & slot extraction via LLM
│   ├── notify_admin.py               # Pushes draft notifications to admin
│   ├── notify_customer.py            # Sends “Reservation Confirmed” to users
│   ├── reservation_flow.py           # Formats data, saves drafts, triggers notifications
│   ├── reservation_draft.py          # In-memory storage of reservation drafts
│   ├── response_builder.py           # Builds LINE text/Flex message payloads
│   ├── timepicker.py                 # Creates interactive date/time selection interface
│   ├── notify_text.py                # Main logic for sending scheduled reminders
│   │   └── search_date.py            # Helper for finding “tomorrow” and “two hours later” slots
│   └── host_control.py               # Verifies if a sender is an admin
├── data/                             # Data storage and logs
│   ├── reservation.json              # All confirmed reservations in JSONL format
│   ├── RAG_enhancer.py               # (Optional) Retrieval-Augmented Generation module
│   ├── notifing.log                  # Plain-text log of push notification attempts
│   └── notification_log.json         # Detailed JSON log of notifications
├── static/                           # Static resources
│   └── audio/                        # Temporary storage for downloaded audio files
├── .env                              # Environment variables: LINE tokens, admin IDs, API keys
├── requirements.txt                  # List of required Python packages
└── README.md                         # Example project documentation (you can expand)
```

#### 1. `app.py`

* Runs a Flask (or similar) web server that:

  1. Exposes the `/callback` endpoint for LINE Webhook events.
  2. Initializes `LineBotApi` and `WebhookHandler` from the LINE Bot SDK.
  3. Routes incoming events to `handlers/unified_router.py` for further processing.

#### 2. `handlers/` Directory

* **`unified_router.py`**

  * Central router for all incoming events (text, audio, and admin-related).
  * Decides which handler to invoke based on event type and whether the sender is an admin.

* **`text_handler.py`**

  * Processes user text messages by:

    1. Calling `llm_service.py` to check if the message relates to a reservation intent.
    2. If yes, extracting relevant slots (date, time, party size, notes).
    3. Storing the draft in memory (`reservation_draft.py`).
    4. Invoking `notify_admin.py` to push a draft notification to the administrators.

* **`audio_handler.py`**

  * Handles user voice messages:

    1. Downloads the audio file (e.g., `.m4a`) into `static/audio/`.
    2. Calls `whisper_service.py` to transcribe the speech to text.
    3. Forwards the transcribed text to `text_handler.py` so that the subsequent flow is identical to processing text.

* **`host_reply_handler.py`**

  * Processes administrator replies/commands in LINE:

    1. Verifies the sender via `host_control.py`.
    2. Checks for specific keywords or command patterns (e.g., “approve #id”, “reject #id”).
    3. Calls functions in `host_command_handlers/` to update or reject drafts, write to `reservation.json`, and notify users/admins.

* **`host_command_handlers/`**

  * Contains concrete implementations for each admin command, for instance:

    * `approve_reservation(id)`: Marks a draft as confirmed, writes it to `reservation.json`, and sends a confirmation.
    * `reject_reservation(id, reason)`: Marks a draft as rejected and sends a rejection notice to the user.
    * `list_pending_reservations()`: Returns all drafts still awaiting approval.
    * Additional admin utilities (e.g., manual resend reminders, debug commands).

#### 3. `services/` Directory

* **`whisper_service.py`**

  * Wraps Whisper API or local model calls.
  * Input: Path to local audio file.
  * Output: Transcribed text string.

* **`llm_service.py`**

  * Interfaces with an LLM (e.g., OpenAI GPT or another deployed model).
  * Provides:

    1. **Intent Classification**: Determines whether a given text is a reservation request.
    2. **Slot Extraction**: Parses out structured fields (date, time, headcount, remarks, etc.).
  * Returns a Python `dict` representing extracted data or a “no intent” result.

* **`notify_admin.py`**

  * Assembles a push message (Flex or plain text) containing the reservation draft details to send to administrators.
  * The Flex Message may include:

    * Requester’s LINE display name or user ID.
    * Desired reservation date & time.
    * Party size and special requests.
    * Quick-action buttons: “Approve”, “Reject”.

* **`notify_customer.py`**

  * After admin approval/rejection:

    * If approved, sends a “Your reservation has been confirmed” message to the user.
    * If rejected, sends an apologetic message and possibly instructions to resubmit.

* **`reservation_flow.py`**

  * Orchestrates the end-to-end reservation logic:

    1. Receives structured data from `llm_service.py`.
    2. Builds a draft object and calls `reservation_draft.py` to store it temporarily.
    3. Calls `notify_admin.py` to notify admins.
    4. Listens for admin approval events; on approval, writes to `reservation.json` and calls `notify_customer.py`.
    5. If rejected, notifies the user and optionally cleans up the draft.

* **`reservation_draft.py`**

  * Temporarily holds draft reservations in an in-memory dictionary (e.g., `drafts[id] = { … }`).
  * Optionally implements a TTL (time-to-live) mechanism so drafts expire if not approved within a certain window (e.g., 24 hours).

* **`response_builder.py`**

  * Constructs various LINE message payloads:

    1. `TextSendMessage` (plain text).
    2. Flex Messages (rich layouts).
    3. Templates like Buttons or Confirm templates when needed.

* **`timepicker.py`**

  * Generates interactive date/time picker UI components for Flex Messages.
  * Users can click to select predefined options (e.g., “Today”, “Tomorrow”) or pick a custom date/time.

* **`notify_text.py`**

  * Core script for scheduled reminders. For example, set up as a cron job or scheduled task:

    * At midnight, calls `search_date.py` to find reservations scheduled for tomorrow, and sends reminders.
    * Continuously (or at certain intervals) checks for reservations happening in two hours and sends second reminders.

  * Logs all attempts (success/failure) to `data/notifing.log` and `data/notification_log.json`.

  * **`search_date.py`**

    * Helper that calculates “tomorrow’s date” and “two hours from now,” then filters `data/reservation.json` for matches, returning a list of relevant reservations.

* **`host_control.py`**

  * Verifies if the LINE user ID belongs to an administrator (based on IDs stored in `.env`).
  * Rejects any admin-specific command requests from non-admins with a polite “You do not have permission” message.

#### 4. `data/` Directory

* **`reservation.json`**

  * Stores all confirmed reservations in JSONL format (one JSON object per line).
  * Example entry:

    ```jsonc
    {"id":"abc123","userId":"Ux1y2z3w4","name":"Alice","date":"2025-06-10","time":"14:30","people":3,"note":"Wheelchair access needed","status":"confirmed","timestamp":"2025-06-05T12:00:00+08:00"}
    ```
  * The `status` field can be `"pending"`, `"confirmed"`, `"rejected"`, `"cancelled"`, etc.

* **`RAG_enhancer.py`**

  * (Optional) If you want to implement Retrieval-Augmented Generation, this module connects to a knowledge base (documents, FAQs) to provide context to the LLM when extracting intent or answering questions.

* **`notifing.log`**

  * Plain-text log of all push notification attempts with timestamps, success/failure messages.
  * Example:

    ```
    [2025-06-05 01:00:00] Notification SUCCESS to Ux1y2z3w4 (Reminder for 2025-06-10 14:30)
    [2025-06-05 01:00:05] Notification FAILED to Ux5y6z7w8 (Timeout)
    ```

* **`notification_log.json`**

  * A structured JSON log storing detailed information about each notification, including:

    * `userId`, `messageType` (reminder, confirmation, rejection), `timestamp`, `status`, `failureReason` (if any).

#### 5. `static/audio/` Directory

* Temporarily stores downloaded audio files from LINE (e.g., `.m4a`) for use by `whisper_service.py`.
* Clean-up logic (e.g., delete after transcription) should be implemented to prevent disk usage from ballooning.

#### 6. `.env` File

```dotenv
LINE_CHANNEL_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LINE_CHANNEL_ACCESS_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ADMIN_USER_IDS=U1234567890abcdef,U0987654321fedcba   # Comma-separated admin IDs
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

* Store all sensitive credentials and IDs here. At runtime, use `python-dotenv` or a similar library to load these environment variables.

#### 7. `requirements.txt`

* Lists all Python dependencies and their versions.
* Example:

  ```
  flask==2.1.0
  line-bot-sdk==2.0.1
  openai-whisper==1.0.0
  openai==0.29.0
  python-dotenv==0.21.0
  langchain==0.0.88
  ```
* Install via:

  ```bash
  pip install -r requirements.txt
  ```

---

### 4. Data Flow Diagram (概念流程)

1. **User → Bot**

   * A user sends either:

     * Text: e.g., “I want to reserve a table tomorrow at 2 PM for 3 people.”
     * Voice: “Reserve June 10th, 6 PM, for 5 people in a private room.”

2. **LINE Server → `app.py`**

   * LINE Webhook event triggers, calling the Flask endpoint `/callback`.

3. **`unified_router.py` → Select Handler**

   * If it’s text: forward to `text_handler.py`.
   * If it’s audio: forward to `audio_handler.py` → transcribe via `whisper_service.py` → send transcribed text back to `text_handler.py`.

4. **`text_handler.py`**

   * Calls `llm_service.py`:

     * Intent classification (reservation or not).
     * Slot extraction to get structured fields.
   * If slot extraction succeeds: calls `reservation_flow.py` to create a draft.

5. **`reservation_flow.py` → `reservation_draft.py`**

   * Builds a draft object (`{id, userId, name, date, time, people, note, status:"pending"}`) and stores it in memory.
   * Calls `notify_admin.py` to push a draft notification to admin(s).

6. **Admin → LINE → `host_reply_handler.py`**

   * Admin receives the draft (Flex Message) and clicks “Approve” or types “Approve #draftID.”
   * Event is routed to `host_reply_handler.py`, then to `host_command_handlers`.
   * E.g., `approve_reservation()` writes a confirmed record to `reservation.json` and calls `notify_customer.py` to inform the user.

7. **Scheduled Reminder**

   * At scheduled times (e.g., midnight daily), a scheduler triggers `services/notify_text.py`:

     * `search_date.py` finds reservations happening “tomorrow” → send reminders.
     * Also finds reservations “two hours from now” → send second reminders.
   * Logs all outcomes in `notifing.log` and `notification_log.json`.

8. **User Receives Reminder**

   * The bot sends a notification like “Reminder: Your reservation is tomorrow at 14:30. Please remember to arrive on time.”
   * If the user needs to cancel, they can send another request (e.g., “Cancel my reservation on June 10, 14:30”), which triggers a new round of intent classification and processing (setting status to “cancelled,” notifying admin, etc.).

---

### 5. Technical Highlights & Advantages

1. **Whisper Speech-to-Text Integration**

   * Allows users to voice their requests, which is automatically transcribed for natural language processing.
   * High accuracy for various speaking speeds and accents.

2. **LLM-Powered Intent & Slot Extraction**

   * Leverages GPT-series or other advanced NLP models for robust intent detection in Chinese/English.
   * High flexibility for extending to other conversational functionalities (e.g., availability queries, modifications, cancellations).

3. **Interactive UI via Flex Messages**

   * Custom Flex layouts for:

     * Admin review cards showing all draft details with “Approve”/“Reject” buttons.
     * Quick-reply or Buttons Template for users to pick dates/times without manual text input.

4. **Flexible Draft & Approval Workflow**

   * Temporary in-memory draft storage ensures that users can confirm or modify details before finalization.
   * TTL (time-to-live) can be added so unreviewed drafts vanish after a set period, keeping data clean.

5. **Automated Reminders & Logging**

   * `notify_text.py` + `search_date.py` implement scheduled tasks to proactively remind users, reducing no-shows.
   * Comprehensive logging (`notifing.log`, `notification_log.json`) ensures full traceability and easier debugging.

6. **Secure Environment & Permissions**

   * Sensitive data (LINE tokens, API keys, admin IDs) are stored in `.env`, preventing accidental commits.
   * `host_control.py` strictly checks admin-only commands, preventing unauthorized actions.

7. **Scalable Data Format**

   * Using JSONL (`reservation.json`) for storing records means each reservation is a standalone JSON object—simple to process with command-line tools (e.g., `jq`) or data analysis frameworks (e.g., Pandas).
