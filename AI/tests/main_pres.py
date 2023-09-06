import cv2
from src.client import *
from src.client_UI import *
from src.recognition_movement import *
import cv2
import numpy as np
import mediapipe as mp
from deepface import DeepFace

class MovementDetectorDemo:
    def __init__(self, cap):
        self.cap = cap
        self.prev_frame = None

    def detect_movement(self):
        while True:
            ret, frame = self.cap.read()
            if self.prev_frame is None:
                self.prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                continue
            
            current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_diff = cv2.absdiff(self.prev_frame, current_frame)
            _, thresholded = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if cv2.contourArea(contour) > 100:
                    cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
                    return frame

            cv2.imshow(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            self.prev_frame = current_frame

class FaceDetector:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.frame = None

    def detect_faces(self, frame):
            self.frame = frame
            while True:
                gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(20, 20))
                face_region = None

                if len(faces) != 0:  
                    for (x, y, w, h) in faces:
                        cv2.rectangle(self.frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        face_region = gray[y:y+h, x:x+w]
                    return True, self.frame
                else:
                    return False, self.frame

    def rotate_image(self, image, angle):
        height, width = image.shape[:2]
        rotation_matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1)
        rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height), flags=cv2.INTER_LINEAR)
        return rotated_image

class ObjectDetector:
    def __init__(self):
        self.frame = None
        self.net = cv2.dnn.readNet("assets/yolov3.weights", "assets/yolov3.cfg")
        with open("assets/coco.names", "r") as f:
            self.classes = [line.strip() for line in f.readlines()]

        self.output_layers = ['yolo_82', 'yolo_94', 'yolo_106']

    def detect_objects(self, frame):
        self.frame = frame
        self.frame = cv2.resize(self.frame, None, fx=0.4, fy=0.4)
        height, width, channels = self.frame.shape

        blob = cv2.dnn.blobFromImage(self.frame, 1 / 255.0, (416, 416), swapRB=True, crop=True)
        self.net.setInput(blob)

        outs = self.net.forward(self.output_layers)
        
        class_ids = []
        confidences = []
        boxes = []

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.66: #Can be changed for better accuracy

                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        font = cv2.FONT_HERSHEY_PLAIN
        colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
        objects = []

        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]])
                confidence = confidences[i]
                color = colors[class_ids[i]]

                # Draw the bounding box and label
                text = f"{label} {confidence:.2f}"
                objects = f"@{label}"
                cv2.rectangle(self.frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(self.frame, text, (x, y + 30), font, 2, color, 3)

        return True, self.frame

class HandTracker():
    def __init__(self, mode=False, maxHands=1, detectionCon=0.5, modelComplexity=1, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.modelComplex = modelComplexity
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            self.mode, self.maxHands, self.modelComplex,
            self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def handsFinder(self, image, draw=True):
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imageRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(
                        image, handLms, self.mpHands.HAND_CONNECTIONS)
             
        return image
    
    def positionFinder(self, image): #index finger to pinky , no thumb
        raised_fingers = []
        
        if self.results.multi_hand_landmarks:
            Hand = self.results.multi_hand_landmarks[0]  # single hand , if more then pass maxHands > 1

            finger_tip_ids = [8, 12, 16, 20] #no thumb
            for id in finger_tip_ids:
                tip_y = Hand.landmark[id].y
                base_y = Hand.landmark[id - 2].y
                is_raised = tip_y < base_y
                raised_fingers.append(is_raised)

        return raised_fingers

class EmotionDetector:
    def __init__(self):
        self.emotion_model = DeepFace.build_model('Emotion')
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def detect_emotions(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            emotions = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            emotion_predictions = emotions[0]['emotion']
            dominant_emotion_label = max(emotion_predictions, key=emotion_predictions.get)
            x, y, w, h = faces[0]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, dominant_emotion_label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        else:
            cv2.putText(frame, 'No Face Detected', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        return frame

class ThumbTracker():
    def __init__(self, mode=False, maxHands=1, detectionCon=0.5, modelComplexity=1, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.modelComplex = modelComplexity
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            self.mode, self.maxHands, self.modelComplex,
            self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def handsFinder(self, image, draw=True):
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imageRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(
                        image, handLms, self.mpHands.HAND_CONNECTIONS)
             
        return image
    
    def thumbsFinder(self, image):
        thumb_state = 0  # -1: Thumb down, 0: Thumb neutral, 1: Thumb up, -0.5: Thumb left, 0.5: Thumb right

        if self.results.multi_hand_landmarks:
            Hand = self.results.multi_hand_landmarks[0]  

            thumb_tip_landmark_id = 4
            thumb_base_landmark_id = 2

            # Get the X and Y coordinates of the thumb tip and base landmarks
            tip_x = Hand.landmark[thumb_tip_landmark_id].x
            tip_y = Hand.landmark[thumb_tip_landmark_id].y
            base_x = Hand.landmark[thumb_base_landmark_id].x
            base_y = Hand.landmark[thumb_base_landmark_id].y

            
            cx, cy = self.results.multi_hand_landmarks[0].landmark[(thumb_tip_landmark_id)].x, self.results.multi_hand_landmarks[0].landmark[(thumb_tip_landmark_id)].y
            h, w, _ = image.shape
            cx, cy = int(cx * w), int(cy * h)
            cv2.circle(image, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
            
            thumb_up_down_threshold = 0.1
            thumb_left_right_threshold = 0.0

            if abs(tip_y < base_y - thumb_up_down_threshold):
                thumb_state = 1  # Thumb up
                cv2.putText(image, "Thumbs Up", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 200, 100), 3)
            elif abs(tip_y > base_y + thumb_up_down_threshold):
                thumb_state = -1  # Thumb down
                cv2.putText(image, "Thumbs Down", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 200, 100), 3)
            elif abs(tip_x < base_x - thumb_left_right_threshold):
                thumb_state += 0.5  # Thumb left
                cv2.putText(image, "Thumbs Left", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 200, 100), 3)
            elif abs(tip_x > base_x + thumb_left_right_threshold):
                thumb_state -= 0.5  # Thumb right
                cv2.putText(image, "Thumbs Right", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 200, 100), 3)
        
        return thumb_state

def choose_label():
    label_chooser = MenuChooser()
    chosen = label_chooser.run()
    return chosen

def map_chosen_to_string(chosen):
    label_mapping = {
        0: "exit",
        1: "face",
        2: "object",
        3: "fingers",
        4: "expression",
        5: "thumb",
    }
    return label_mapping.get(chosen, "@exit+nisan")

def main():
    chosen = choose_label()
    chosen = map_chosen_to_string(chosen)
    
    cap = cv2.VideoCapture(0)
    detector = MovementDetector(cap)
    detected_frame = detector.detect_movement()

    if chosen == "face":
        detector = FaceDetector()
        while True:
            ret, frame = cap.read()
            res, detected_frame = detector.detect_faces(frame)
            if res == True:
                cv2.imshow("faces", detected_frame)
            else:
                cv2.imshow("faces", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
    if chosen == "object":
        detector = ObjectDetector()
        while True:
            ret, frame = cap.read()
            res, detected_frame = detector.detect_objects(frame)
            if res == True:
                cv2.imshow("objects", detected_frame)
            else:
                cv2.imshow("objects", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
    if chosen == "fingers":
        tracker = HandTracker()  
        while True:
            success, image = cap.read()
            image = tracker.handsFinder(image)
            raised_fingers = tracker.positionFinder(image)
            raised_finger_count = ""

            for finger_id, is_raised in enumerate(raised_fingers, start=1):
                if is_raised:
                    cx, cy = tracker.results.multi_hand_landmarks[0].landmark[(finger_id + 1)* 4].x, tracker.results.multi_hand_landmarks[0].landmark[(finger_id + 1)* 4].y
                    h, w, _ = image.shape
                    cx, cy = int(cx * w), int(cy * h)
                    cv2.circle(image, (cx, cy), 15, (255, 0, 255), cv2.FILLED)  # Draw a filled circle on raised finger
                    raised_finger_count += f"{finger_id + 1}"
                    cv2.putText(image, f"Raised fingers: {raised_finger_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 200, 100), 3)

            cv2.imshow("fingers", image)
            key = cv2.waitKey(20)
            if key == ord('q'):
                cv2.destroyAllWindows()
                break
    if chosen == "expression":
        detector = EmotionDetector()
        while True:
            ret, frame = cap.read()
            detected_frame = detector.detect_emotions(frame)
            cv2.imshow("faces", detected_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
    if chosen == "thumb":
        detector = ThumbTracker()
        while True:
            ret, frame = cap.read()
            detected_frame = detector.handsFinder(frame)
            detector.thumbsFinder(frame)

            cv2.imshow("faces", detected_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break


    cap.release()
if __name__ == "__main__":
    main()
