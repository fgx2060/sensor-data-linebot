# sensor-data-linebot
人工智慧實務實作 - 感測器數據分析與 LINE Bot 輔助通報系統

## 📖 專案簡介
整合 Arduino 感測器與 Python，將數據即時回報至 LINE Bot，適用於智慧監控與警示。

## ⚙️ 功能特色
- 支援溫濕度 / 人體感測
- LINE Bot 即時推送
- 簡單擴充新感測器

## 🛠️ 技術架構
- **硬體**：Arduino + Sensor
- **後端**：Python
- **通訊**：LINE Messaging API

## 🚀 使用說明
### Arduino 端
 - sketch_jun5a.ino → 感測器讀取程式（溫濕度、PIR 動作感測，透過序列傳送資料）。

### Python 端
#### test.py
 - 透過序列埠讀取溫度/濕度/動作偵測資料並存入 CSV
  - → 屬於 「感測器數據分析」的基礎紀錄程式

#### test2.py
 - Flask + LINE Bot，讀取感測器資料後呼叫 Ollama (qwen3 模型) 生成回覆
 - 加入 AI 解釋功能

#### test3.py
 - 即時接收感測資料並判斷是否舒適
 - 自動透過 LINE Bot 推播提醒（例如「有人進入環境」「出門忘記關冷氣」）



## 成果報告書
 - 人工智慧實務實作-感測器數據分析與LINE Bot 輔助通報系統.pdf
