from flask import Flask, request
import serial
import ollama
import re
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# === LINE Bot 設定 ===
LINE_CHANNEL_ACCESS_TOKEN = 'KGbX3Tk6JBOrhIj5RzV9km+eCkgJwX7YOVg5uIV77OrLKmlktVOpG+LdMZvq2xz7sWNo4iSFioPFjGWbSGOXYO DclALutYYIkD8FixBI6TOZ4n4zfgpB+5Cu5+lG4kOnaWh+9KDpkVE4AW+YhIyHagdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '19099c57fbf08f73b927a478d8094722'
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# === HC-05 藍牙 COM 設定 ===
PORT = 'COM5'
BAUD_RATE = 9600
ser = serial.Serial(PORT, BAUD_RATE, timeout=2)

def read_sensor_line():
    try:
        line = ser.readline().decode().strip()
        if line:
            temp, hum, motion = line.split(",")
            return {
                "temp": temp,
                "hum": hum,
                "motion": motion
            }
    except:
        return None

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return 'Invalid signature', 400

    return 'OK', 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    sensor_data = read_sensor_line()

    if not sensor_data:
        reply = "目前無法讀取感測資料，請稍後再試。"
    else:
        system_prompt = f"""
目前偵測到的環境資料如下：
- 溫度：{sensor_data['temp']}°C
- 濕度：{sensor_data['hum']}%
- 是否有人：{'有' if sensor_data['motion']=='1' else '無'}

請根據以上資料回答使用者問題：{user_message}
"""
        try:
            response = ollama.chat(
                model='qwen3:8b',
                messages=[
                    {"role": "system", "content": "你是環境感測分析專家。"},
                    {"role": "user", "content": system_prompt}
                ]
            )
            raw_reply = response['message']['content']
            # ⛔ 移除 <think> ... </think> 區塊（包含內容）
            reply = re.sub(r"<think>.*?</think>", "", raw_reply, flags=re.DOTALL).strip()
        except Exception as e:
            print("❌ Ollama 錯誤：", e)
            reply = "❌ 模型處理錯誤，請稍後再試。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    app.run(port=5000)
    print(f"✅ Flask 伺服器已啟動，監聽端口 5000")
    print(f"✅ 已連接至 HC-05 藍牙模組，COM 埠：{PORT}")