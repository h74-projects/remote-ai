import sys
sys.path.append("../")

import cv2
from src.hand_detector import HandDetector

def main():
    cap = cv2.VideoCapture(0)
    detector = HandDetector()

    while True:
        success, image = cap.read()
        hand_landmarks = detector.find_hands(image)
        
        if hand_landmarks:
            num_raised, raised_fingers = detector.count_raised_fingers(hand_landmarks)
            if num_raised == 0:
                print("No fingers are raised!")
            else:
                print(f"{num_raised} fingers are raised!")
                detector.mark_raised_fingers(image, raised_fingers)

        cv2.imshow("Output", image)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
