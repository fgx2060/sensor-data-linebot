import serial
import time
import csv
from linebot import LineBotApi
from linebot.models import TextSendMessage

# === LINE Bot 設定 ===
LINE_CHANNEL_ACCESS_TOKEN = 'KGbX3Tk6JBOrhIj5RzV9km+eCkgJwX7YOVg5uIV77OrLKmlktVOpG+LdMZvq2xz7sWNo4iSFioPFjGWbSGOXYODclALutYYIkD8FixBI6TOZ4n4zfgpB+5Cu5+lG4kOnaWh+9KDpkVE4AW+YhIyHagdB04t89/1O/w1cDnyilFU='
TO_USER_ID = 'U99735fe437538daac832e55513d08724'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def send_linebot_message(message):
    try:
        line_bot_api.push_message(
            TO_USER_ID,
            TextSendMessage(text=message)
        )
        print("✅ 已發送 LINE Bot 通知")
    except Exception as e:
        print("❌ 傳送 LINE Bot 訊息失敗：", e)

# === 溫濕度是否舒適的判斷條件 ===
def is_comfortable(temp, hum):
    return 26.0 <= temp <= 28.0 and 45 <= hum <= 65

# === HC-05 COM 埠設定 ===
PORT = 'COM5'
BAUD_RATE = 9600

try:
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
    print(f"✅ 成功連接至 {PORT}")
except:
    print(f"❌ 無法開啟 {PORT}，請確認 HC-05 是否配對成功並有對應 COM 埠")
    exit()

# === 儲存資料 + 檢查條件 ===
with open("sensor_log.csv", "a", newline="") as f:
    writer = csv.writer(f)
    if f.tell() == 0:
        writer.writerow(["Time", "Temperature", "Humidity", "Motion"])

    print("📡 開始接收資料中，按 Ctrl+C 可停止")

    try:
        last_alert_time_person = 0
        last_alert_time_empty = 0
        cooldown = 60  # 通知冷卻時間（秒）

        while True:
            line = ser.readline().decode().strip()
            if line:
                try:
                    temp, hum, motion = line.split(",")
                    temp = float(temp)
                    hum = float(hum)
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"{timestamp} -> T:{temp}°C H:{hum}% 有人:{motion}")
                    writer.writerow([timestamp, temp, hum, motion])

                    comfort = is_comfortable(temp, hum)
                    now = time.time()

                    if motion.strip() == "1":
                        if now - last_alert_time_person > cooldown:
                            if not comfort:
                                send_linebot_message(
                                    f"👤 有人進入環境\n🕒 時間：{timestamp}\n🌡️ 溫度：{temp}°C\n💧 濕度：{hum}%\n⚠️ 感測數據不舒適，建議開冷氣"
                                )
                            else:
                                send_linebot_message(
                                    f"👤 有人進入環境\n🕒 時間：{timestamp}\n🌡️ 溫度：{temp}°C\n💧 濕度：{hum}%\n✅ 感測數據舒適，無需開冷氣"
                                )
                            last_alert_time_person = now

                    elif motion.strip() == "0":
                        if now - last_alert_time_empty > cooldown:
                            if comfort:
                                send_linebot_message(
                                    f"🏃 無人偵測中\n🕒 時間：{timestamp}\n🌡️ 溫度：{temp}°C\n💧 濕度：{hum}%\n🔔 感測數據舒適，是否忘記關冷氣？"
                                )
                            else:
                                send_linebot_message(
                                    f"🏃 無人偵測中\n🕒 時間：{timestamp}\n🌡️ 溫度：{temp}°C\n💧 濕度：{hum}%\n✅ 很棒，出門沒有忘記關冷氣！"
                                )
                            last_alert_time_empty = now

                except ValueError:
                    print("⚠️ 資料格式錯誤：", line)

    except KeyboardInterrupt:
        print("🚪 已中止接收")
        ser.close()
