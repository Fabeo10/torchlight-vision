import cv2
import mediapipe as mp
import threading

class HandDetector:
    def __init__(self):
        self.hand_detected = False
        self.running = True
        self.lock = threading.Lock()

        self.cap = cv2.VideoCapture(0)
        self.hands = mp.solutions.hands.Hands()

        self.thread = threading.Thread(target=self.detect_loop)
        self.thread.start()

    def detect_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)

            with self.lock:
                self.hand_detected = results.multi_hand_landmarks is not None

    def is_hand_detected(self):
        with self.lock:
            return self.hand_detected

    def stop(self):
        self.running = False
        self.thread.join()
        self.cap.release()
