import cv2

class FaceDetector:
    def __init__(self, cascade_path , cap):
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.cap = cap

    def detect_faces(self):
        while True:
            save_face = False
            ret, frame = self.cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                face_region = gray[y:y+h, x:x+w]
                if cv2.waitKey(10) & 0xFF == ord('s'):
                    self.save_face_to_file(face_region)
                    save_face = True
            cv2.imshow('Feed', frame)
            if cv2.waitKey(20) & 0xFF == ord('q'):
                break


    def save_face_to_file(self, face_region):
        file_path = 'face.jpg'
        cv2.imwrite(file_path, face_region)
        print(f"Face saved to {file_path}")