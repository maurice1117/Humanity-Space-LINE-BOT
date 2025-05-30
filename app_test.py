# test5.py
print("1. 開始載入...")

from dotenv import load_dotenv
print("2. dotenv 載入完成")

from flask import Flask, request, abort, jsonify
print("3. Flask 載入完成")

from linebot import LineBotApi, WebhookHandler
print("4. LINE Bot SDK 載入完成")

from datetime import datetime
print("5. datetime 載入完成")

import os
print("6. os 載入完成")

from handlers.unified_router import register_handlers
print("7. unified_router 載入成功")

from services.notify_text import daily_evening_notify, hourly_check_notify
print("8. notify_text 載入成功")

print("9. 所有模組載入完成")

load_dotenv()
print("10. dotenv 載入完成")

app = Flask(__name__)
print("11. Flask app 創建完成")

# 正確創建 LINE Bot 物件
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
print("12. LINE Bot 物件創建完成")

# 正確註冊 handlers
try:
    print("13. 準備註冊 handlers...")
    register_handlers(handler)  # 傳入 handler，而不是 app
    print("14. ✅ handlers 註冊成功")
except Exception as e:
    print(f"14. ❌ handlers 註冊失敗: {e}")
    import traceback
    traceback.print_exc()

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    
    if not signature:
        print("❌ 缺少 X-Line-Signature 標頭")
        abort(400)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"❌ 處理錯誤: {e}")
        abort(500)

    return 'OK'

@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

@app.route("/test/daily-notify", methods=["GET"])
def test_daily_notify():
    try:
        print("🧪 開始測試每日晚間通知...")
        success_count = daily_evening_notify()
        
        result = {
            "status": "success",
            "message": "每日晚間通知測試完成",
            "notifications_sent": success_count,
            "timestamp": str(datetime.now())
        }
        
        print(f"✅ 測試完成: {result}")
        return jsonify(result), 200
        
    except Exception as e:
        import traceback
        error_msg = f"每日通知測試失敗: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        
        return jsonify({
            "status": "error",
            "message": error_msg,
            "timestamp": str(datetime.now())
        }), 500

print("15. 路由設定完成")

@app.route("/test/hour-notify", methods=["GET"])
def test_hour_notify():
    try:
        print("🧪 開始測試小時通知...")
        success_count = hourly_check_notify()
        
        result = {
            "status": "success",
            "message": "小時通知測試完成",
            "notifications_sent": success_count,
            "timestamp": str(datetime.now())
        }
        
        print(f"✅ 測試完成: {result}")
        return jsonify(result), 200
        
    except Exception as e:
        import traceback
        error_msg = f"小時通知測試失敗: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        
        return jsonify({
            "status": "error",
            "message": error_msg,
            "timestamp": str(datetime.now())
        }), 500
print("18. 路由設定完成")
if __name__ == "__main__":
    print("16. 準備啟動 Flask...")
    try:
        app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
        print("17. Flask 啟動成功")
    except Exception as e:
        print(f"17. ❌ Flask 啟動失敗: {e}")
        import traceback
        traceback.print_exc()
        
