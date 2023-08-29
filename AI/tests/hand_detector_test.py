import sys
sys.path.append("../")

import cv2
import time

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

            wave_direction = detector.detect_wave_direction(hand_landmarks)
            if wave_direction:
                print(f"Hand waved to the {wave_direction}")

            vertical_movement = detector.detect_vertical_movement(hand_landmarks)
            if vertical_movement:
                print(f"Hand moved {vertical_movement}")

        cv2.imshow("Output", image)
        
        time.sleep(0.5)

        # Press 'q' to exit the loop and close the window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

