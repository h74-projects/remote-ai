import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.hands = mp.solutions.hands.Hands(static_image_mode=static_image_mode, 
                                              max_num_hands=max_num_hands, 
                                              min_detection_confidence=min_detection_confidence, 
                                              min_tracking_confidence=min_tracking_confidence)
        self.mpDraw = mp.solutions.drawing_utils

    def find_hands(self, image):
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(imageRGB)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(image, handLms, mp.solutions.hands.HAND_CONNECTIONS)
                return handLms  # Return first hand's landmarks

        return None  # No hands detected

    def count_raised_fingers(self, landmarks):
        finger_tips = [
            landmarks.landmark[4],  # Thumb
            landmarks.landmark[8],  # Index
            landmarks.landmark[12], # Middle
            landmarks.landmark[16], # Ring
            landmarks.landmark[20]  # Pinky
        ]

        lower_joints = [
            landmarks.landmark[2],  # Thumb
            landmarks.landmark[5],  # Index
            landmarks.landmark[9],  # Middle
            landmarks.landmark[13], # Ring
            landmarks.landmark[17]  # Pinky
        ]

        raised_fingers = [] 

        # Check if hand is likely flipped (showing back of hand)
        back_of_hand_count = sum(1 for fingertip in finger_tips if fingertip.z > landmarks.landmark[0].z)
        if back_of_hand_count >= 3:
            print("Back of hand detected!")
            return 0, []

        # Thumb detection
        if finger_tips[0].x < lower_joints[0].x and finger_tips[0].y < lower_joints[0].y:
            raised_fingers.append(finger_tips[0])

        # Other fingers detection
        for i in range(1, 5):
            if finger_tips[i].y < lower_joints[i].y - 0.02:  # Adjust the threshold if needed
                raised_fingers.append(finger_tips[i])

        return len(raised_fingers), raised_fingers

    def mark_raised_fingers(self, image, raised_fingers):
        h, w, c = image.shape
        for finger in raised_fingers:
            cx, cy = int(finger.x * w), int(finger.y * h)
            cv2.circle(image, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
