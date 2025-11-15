import cv2
import numpy as np
import time
import requests

ESP_IP = "10.76.103.27"  # ضع هنا IP اللي ظهر على الـ ESP
FORWARD_URL = f"http://{ESP_IP}/forward"
STOP_URL = f"http://{ESP_IP}/stop"
last_sent = 0

cap = cv2.VideoCapture(0)

def send_cmd(url):
    global last_sent
    try:
        if time.time() - last_sent > 0.5:  # يرسل كل نصف ثانية
            requests.get(url, timeout=0.5)
            last_sent = time.time()
    except requests.exceptions.RequestException:
        pass

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    white_area = cv2.countNonZero(thresh)

    if white_area > 120000:
        hand_state = "Open"
        send_cmd(FORWARD_URL)  # أمر الحركة
        color = (0, 255, 0)
    else:
        hand_state = "Closed"
        send_cmd(STOP_URL)  # أمر التوقف
        color = (0, 0, 255)

    cv2.putText(frame, f"Hand: {hand_state}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

    cv2.imshow("Frame", frame)
    cv2.imshow("Threshold", thresh)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # اضغط ESC للخروج
        break

cap.release()
cv2.destroyAllWindows()
