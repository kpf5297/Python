import sys
import cv2
import numpy as np
import mediapipe as mp
from deepface import DeepFace
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

# Initialize Mediapipe and OpenCV
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Open Webcam
cap = cv2.VideoCapture(0)

class HandFaceDetectionApp(QWidget):
    def __init__(self):
        super().__init__()

        # Create UI Elements
        self.setWindowTitle("AI Hand & Face Detection")
        self.setGeometry(100, 100, 800, 600)

        self.video_label = QLabel(self)
        self.btn_face = QPushButton("Face Detection", self)
        self.btn_emotion = QPushButton("Emotion Analysis", self)
        self.btn_hand = QPushButton("Hand Gesture Detection", self)
        self.btn_exit = QPushButton("Exit", self)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.btn_face)
        layout.addWidget(self.btn_emotion)
        layout.addWidget(self.btn_hand)
        layout.addWidget(self.btn_exit)
        self.setLayout(layout)

        # Button Actions
        self.btn_face.clicked.connect(self.start_face_detection)
        self.btn_emotion.clicked.connect(self.start_emotion_analysis)
        self.btn_hand.clicked.connect(self.start_hand_detection)
        self.btn_exit.clicked.connect(self.close_app)

        # Video Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

        # Mode Control
        self.mode = None

    def update_frame(self):
        """Update the video frame in the GUI."""
        _, frame = cap.read()
        if frame is None:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if self.mode == "face":
            self.detect_faces(frame)
        elif self.mode == "emotion":
            self.analyze_emotions(frame)
        elif self.mode == "hand":
            self.detect_hand_gestures(frame)

        # Convert frame to PyQt format
        img = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        self.video_label.setPixmap(pixmap)

    def start_face_detection(self):
        self.mode = "face"

    def start_emotion_analysis(self):
        self.mode = "emotion"

    def start_hand_detection(self):
        self.mode = "hand"

    def close_app(self):
        cap.release()
        cv2.destroyAllWindows()
        self.close()

    def detect_faces(self, frame):
        """Detect faces using OpenCV."""
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    def analyze_emotions(self, frame):
        """Analyze emotions using DeepFace."""
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            face_roi = frame[y:y+h, x:x+w]
            face_rgb = cv2.cvtColor(face_roi, cv2.COLOR_RGB2BGR)

            try:
                analysis = DeepFace.analyze(face_rgb, actions=["emotion"], enforce_detection=False)
                emotion = analysis[0]["dominant_emotion"]
                cv2.putText(frame, f"Emotion: {emotion}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            except Exception as e:
                print("Emotion Analysis Error:", e)

    def detect_hand_gestures(self, frame):
        """Detect Thumbs Up 👍 and OK 👌 gestures using Mediapipe."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Extract key landmark positions
                landmarks = hand_landmarks.landmark
                thumb_tip = landmarks[4]
                index_tip = landmarks[8]
                middle_tip = landmarks[12]
                ring_tip = landmarks[16]
                pinky_tip = landmarks[20]
                wrist = landmarks[0]

                # Convert normalized landmarks to pixel coordinates
                h, w, _ = frame.shape
                thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
                middle_x, middle_y = int(middle_tip.x * w), int(middle_tip.y * h)
                ring_x, ring_y = int(ring_tip.x * w), int(ring_tip.y * h)
                pinky_x, pinky_y = int(pinky_tip.x * w), int(pinky_tip.y * h)

                # **Thumbs Up Detection** 👍
                if (thumb_y < index_y and thumb_y < middle_y and
                        thumb_y < ring_y and thumb_y < pinky_y):
                    cv2.putText(frame, "Thumbs Up 👍", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # **OK Gesture Detection** 👌
                # Condition: Thumb and Index are close together, others are apart
                thumb_index_dist = np.linalg.norm(np.array([thumb_x, thumb_y]) - np.array([index_x, index_y]))
                if thumb_index_dist < 30 and middle_y > index_y and ring_y > index_y and pinky_y > index_y:
                    cv2.putText(frame, "OK Gesture 👌", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                # **Peace Gesture Detection** ✌️
                # Condition: Index and Middle are close together, others are apart
                index_middle_dist = np.linalg.norm(np.array([index_x, index_y]) - np.array([middle_x, middle_y]))
                if index_middle_dist < 30 and thumb_y > index_y and ring_y > index_y and pinky_y > index_y:
                    cv2.putText(frame, "Peace Gesture ✌️", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # **Rock Gesture Detection** 🤘
                # Condition: Pinky and Ring are close together, others are apart
                pinky_ring_dist = np.linalg.norm(np.array([pinky_x, pinky_y]) - np.array([ring_x, ring_y]))
                if pinky_ring_dist < 30 and thumb_y > index_y and middle_y > index_y and ring_y > index_y:
                    cv2.putText(frame, "Rock Gesture 🤘", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

                # **Fist Gesture Detection** ✊
                # Condition: All fingers are close to the wrist
                thumb_wrist_dist = np.linalg.norm(np.array([thumb_x, thumb_y]) - np.array([wrist.x * w, wrist.y * h]))
                index_wrist_dist = np.linalg.norm(np.array([index_x, index_y]) - np.array([wrist.x * w, wrist.y * h]))
                middle_wrist_dist = np.linalg.norm(np.array([middle_x, middle_y]) - np.array([wrist.x * w, wrist.y * h]))
                ring_wrist_dist = np.linalg.norm(np.array([ring_x, ring_y]) - np.array([wrist.x * w, wrist.y * h]))
                pinky_wrist_dist = np.linalg.norm(np.array([pinky_x, pinky_y]) - np.array([wrist.x * w, wrist.y * h]))
                if (thumb_wrist_dist < 30 and index_wrist_dist < 30 and
                        middle_wrist_dist < 30 and ring_wrist_dist < 30 and pinky_wrist_dist < 30):
                    cv2.putText(frame, "Fist Gesture ✊", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HandFaceDetectionApp()
    window.show()
    sys.exit(app.exec_())
