#include <SoftwareSerial.h>
#include <DHT.h>

// 感測器接腳定義
#define DHTPIN 2         // DHT11 資料腳位接到 D2
#define DHTTYPE DHT11    // 感測器型號
#define PIRPIN 3         // HC-SR501 輸出接 D3

DHT dht(DHTPIN, DHTTYPE);
SoftwareSerial BTSerial(10, 11); // HC-05 TX接D10, RX接D11（需降壓）

void setup() {
  dht.begin();
  pinMode(PIRPIN, INPUT);
  
  Serial.begin(9600);      // Debug用
  BTSerial.begin(9600);    // 與 HC-05 通訊
  
  Serial.println("系統啟動，開始傳送感測資料...");
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int motion = digitalRead(PIRPIN);  // 1：有人，0：沒人

  // 檢查讀值是否成功
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("❗ 無法讀取 DHT11 資料");
    return;
  }

  // 組合要傳送的資料
  String data = String(temperature, 1) + "," + String(humidity, 1) + "," + String(motion);
  
  // 傳送到藍牙模組與序列監控視窗
  BTSerial.println(data);
  Serial.println("傳送：" + data);

  delay(2000); // 每 2 秒傳送一次
}
