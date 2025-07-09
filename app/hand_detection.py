import cv2
import mediapipe as mp
import threading
import numpy as np

class HandDetector:
    def __init__(self):
        self.hand_detected = False
        self.hand_piece = False
        self.latest_frame = None
        self.running = True
        self.lock = threading.Lock()

        self.cap = cv2.VideoCapture(1)  # External camera
        self.hands = mp.solutions.hands.Hands()

        self.thread = threading.Thread(target=self.detect_loop)
        self.thread.start()

    def detect_loop(self):
        mp_drawing = mp.solutions.drawing_utils

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)

            annotated_frame = frame.copy()
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        annotated_frame,
                        hand_landmarks,
                        mp.solutions.hands.HAND_CONNECTIONS
                    )

            with self.lock:
                self.hand_detected = results.multi_hand_landmarks is not None
                self.hand_piece = False
                self.latest_frame = annotated_frame  

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        def extended(tip_idx, pip_idx):
                            return hand_landmarks.landmark[tip_idx].y < hand_landmarks.landmark[pip_idx].y - 0.02

                        index_extended = extended(8, 6)
                        middle_extended = extended(12, 10)
                        ring_curled = hand_landmarks.landmark[16].y > hand_landmarks.landmark[14].y + 0.02
                        pinky_curled = hand_landmarks.landmark[20].y > hand_landmarks.landmark[18].y + 0.02
                        thumb_curled = hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x  # right hand

                        is_peace_sign = (
                            index_extended and
                            middle_extended and
                            ring_curled and
                            pinky_curled and
                            thumb_curled
                        )

                        if is_peace_sign:
                            self.hand_piece = True
                            break


    def is_hand_detected(self):
        with self.lock:
            return self.hand_detected

    def is_hand_piece(self):
        with self.lock:
            return self.hand_piece

    def get_latest_frame(self):
        with self.lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None

    def stop(self):
        self.running = False
        self.thread.join()
        self.cap.release()
