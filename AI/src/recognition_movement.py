import cv2

class MovementDetector:
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
                    # return frame

            cv2.imshow('Feed', frame)
            key = cv2.waitKey(20)
            if key == ord('q'):
                cv2.destroyAllWindows()
                return frame

            self.prev_frame = current_frame

        # self.cap.release()
        # cv2.destroyAllWindows()
