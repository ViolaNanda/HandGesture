import cv2
import mediapipe as mp
import os
import time
import threading
from gtts import gTTS
from playsound import playsound

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

def speak(text):
    def run():
        print(f"🗣️ {text}")
        tts = gTTS(text=text, lang='id', tld='co.id')
        tts.save("voice.mp3")
        playsound("voice.mp3")
        os.remove("voice.mp3")
    threading.Thread(target=run, daemon=True).start()

last_spoken = ""
last_time = 0
delay = 2
display_text = ""
display_time = 0

PINK_PASTEL = (203, 192, 255) 

def draw_glow_text(frame, text, pos, font, scale, color, thickness):
    x, y = pos
    glow_color = (255, 255, 255)
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx != 0 or dy != 0:
                cv2.putText(frame, text, (x + dx, y + dy), font, scale, glow_color, thickness)
    cv2.putText(frame, text, pos, font, scale, color, thickness + 1, cv2.LINE_AA)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = hand_landmarks.landmark
            finger_tips = [4, 8, 12, 16, 20]
            finger_states = []

            if landmarks[finger_tips[0]].x < landmarks[finger_tips[0] - 1].x:
                finger_states.append(1)
            else:
                finger_states.append(0)

            for id in range(1, 5):
                if landmarks[finger_tips[id]].y < landmarks[finger_tips[id] - 2].y:
                    finger_states.append(1)
                else:
                    finger_states.append(0)

            text = ""

            if finger_states == [1, 1, 1, 1, 1]:
                text = "Halo , Perkenalkan!"
            elif finger_states == [1, 0, 0, 0, 0]:
                text = "Nama Saya"
            elif finger_states == [0, 1, 1, 0, 0]:
                text = "Viola Nanda Hasnia"
            elif finger_states == [0, 0, 0, 0, 1]:
                text = "Salam Kenal Ya!"
            elif finger_states == [1, 1, 0, 0, 1]:
                text = "Terimakasih!"

            if text and (text != last_spoken or time.time() - last_time > delay):
                speak(text)
                last_spoken = text
                last_time = time.time()
                display_text = text
                display_time = time.time()

    if display_text and time.time() - display_time < 2:
        draw_glow_text(frame, display_text, (50, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, PINK_PASTEL, 2)
    else:
        display_text = ""

    cv2.imshow("Hand Gesture Speaker - Viola Nanda Hasnia 💖", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
