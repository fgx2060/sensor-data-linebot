import serial
import time
import csv

ser = serial.Serial('COM5', 9600)  # 依照實際藍牙序列埠修改

with open("sensor_log.csv", "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Temp", "Humidity", "Motion", "Timestamp"])

    while True:
        line = ser.readline().decode().strip()
        if line:
            try:
                temp, hum, motion = line.split(",")
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"{ts} - T:{temp}°C H:{hum}% Motion:{motion}")
                writer.writerow([temp, hum, motion, ts])
            except:
                continue
