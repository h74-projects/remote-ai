import cv2
import mediapipe as mp

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


            thumb_up_down_threshold = 0.1
            thumb_left_right_threshold = 0.1

            if tip_y < base_y - thumb_up_down_threshold:
                thumb_state = 1  # Thumb up
            elif tip_y > base_y + thumb_up_down_threshold:
                thumb_state = -1  # Thumb down
            if tip_x < base_x - thumb_left_right_threshold:
                thumb_state += 0.5  # Thumb left
            elif tip_x > base_x + thumb_left_right_threshold:
                thumb_state -= 0.5  # Thumb right

        return thumb_state

# if __name__ == "__main__":
#     cap = cv2.VideoCapture(0)
#     tracker = HandTracker()  
#     raised = 0

#     for _ in range(5):
#         success, image = cap.read()
#         image = tracker.handsFinder(image)
#         raised = tracker.positionFinder(image)
#     if raised:
