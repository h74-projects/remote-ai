import cv2
import mediapipe as mp
from collections import deque

class HandDetector:
    def __init__(self, static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5, history_length=5):
        self.hands = mp.solutions.hands.Hands(static_image_mode=static_image_mode, 
                                              max_num_hands=max_num_hands, 
                                              min_detection_confidence=min_detection_confidence, 
                                              min_tracking_confidence=min_tracking_confidence)
        self.mpDraw = mp.solutions.drawing_utils

        # Deques to store recent wrist coordinates
        self.x_history = deque(maxlen=history_length)
        self.y_history = deque(maxlen=history_length)
        self.x_threshold = 0.01  # You can adjust this value based on testing
        self.y_threshold = 0.01  # You can adjust this value based on testing

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
    
    def detect_wave_direction(self, landmarks):
        wrist_x = landmarks.landmark[0].x
        
        if len(self.x_history) > 1:
            movement = abs(wrist_x - self.x_history[-1])

            # Check for stationary hand
            if movement < self.x_threshold:
                return "Stationary"

            # Check direction
            if wrist_x > self.x_history[-1] and self.x_history[-1] > self.x_history[-2]:
                return "Right"
            elif wrist_x < self.x_history[-1] and self.x_history[-1] < self.x_history[-2]:
                return "Left"

        # Add current wrist_x to history
        self.x_history.append(wrist_x)
        return None
    
    def detect_vertical_movement(self, landmarks):
        wrist_y = landmarks.landmark[0].y
        
        if len(self.y_history) > 1:
            movement = abs(wrist_y - self.y_history[-1])

            # Check for stationary hand
            if movement < self.y_threshold:
                return "Stationary"

            # Check direction
            if wrist_y > self.y_history[-1] and self.y_history[-1] > self.y_history[-2]:
                return "Down"
            elif wrist_y < self.y_history[-1] and self.y_history[-1] < self.y_history[-2]:
                return "Up"

        # Add current wrist_y to history
        self.y_history.append(wrist_y)
        return None
