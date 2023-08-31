import cv2
from deepface import DeepFace

class EmotionDetector:
    def __init__(self):
        self.emotion_model = DeepFace.build_model('Emotion')
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def detect_emotions(self, frame, show=False):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            emotions = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            emotion_predictions = emotions[0]['emotion']
            dominant_emotion_label = max(emotion_predictions, key=emotion_predictions.get)
            x, y, w, h = faces[0]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, dominant_emotion_label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        else:
            cv2.putText(frame, 'No Face Detected', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        if show:
            while True:
                cv2.imshow('Facial Expression Detection', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        return dominant_emotion_label, [(x, y, w, h)]
