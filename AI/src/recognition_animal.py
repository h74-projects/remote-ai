import cv2

# add this line if cv2.data isnt found
# export PYTHONPATH=/usr/local/lib/python2.7/site-packages:$PYTHONPATH

class FaceDetector:
    def __init__(self, a_frame):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.frame = a_frame

    def detect_faces(self):
            save_face = False
            gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
            
            for (x, y, w, h) in faces:
                # cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                face_region = gray[y:y+h, x:x+w]
                return face_region, [(x, y, w, h)]
                
                # if cv2.waitKey(10) & 0xFF == ord('s'):
                # save_face = True

            # cv2.imshow('Feed', frame)
            # if cv2.waitKey(20) & 0xFF == ord('q'):
            #     break

    def save_face_to_file(self, face_region):
        file_path = 'face.jpg'
        cv2.imwrite(file_path, face_region)
        print(f"Face saved to {file_path}")

    def convert_to_jpeg(self, image_array):
        _, jpeg_data = cv2.imencode('.jpg', image_array)
        jpeg_bytes = jpeg_data.tobytes()

        return jpeg_bytes