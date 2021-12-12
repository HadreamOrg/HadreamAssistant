import serial
import time

ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
# ser.open()

while True:

    time.sleep(0.15)
    response = str(ser.readline(), "utf-8").replace("\r\n", "")
    print(response)