import cv2
import mediapipe as mp

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
                base_y = Hand.landmark[id - 1].y
                is_raised = tip_y < base_y
                raised_fingers.append(is_raised)

        return raised_fingers

# if __name__ == "__main__":
#     cap = cv2.VideoCapture(0)
#     tracker = HandTracker()  

#     while True:
#         success, image = cap.read()
#         image = tracker.handsFinder(image)
#         raised_fingers = tracker.positionFinder(image)

#         # Print the state of each finger and draw a circle on the tip
#         for finger_id, is_raised in enumerate(raised_fingers, start=1):
#             if is_raised:
#                 print(f"Finger {finger_id + 1} is raised")
#                 cx, cy = tracker.results.multi_hand_landmarks[0].landmark[(finger_id + 1)* 4].x, tracker.results.multi_hand_landmarks[0].landmark[(finger_id + 1)* 4].y
#                 h, w, _ = image.shape
#                 cx, cy = int(cx * w), int(cy * h)
#                 cv2.circle(image, (cx, cy), 15, (255, 0, 255), cv2.FILLED)  # Draw a filled circle on raised finger

#         cv2.imshow("Video", image)
#         key = cv2.waitKey(20)
#         if key == ord('q'):
#             cv2.destroyAllWindows()
#             break
        