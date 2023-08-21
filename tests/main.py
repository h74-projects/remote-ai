from src import recognition_face, recognition_movement
import cv2

if __name__ == "__main__":
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    movement_detector = recognition_movement.MovementDetector(cap)
    movement_detector.detect_movement()
    
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    detector = recognition_face.FaceDetector(cascade_path, cap)
    detector.detect_faces()
    
    cap.release()
    cv2.destroyAllWindows()