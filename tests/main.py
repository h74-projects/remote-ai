from ..src.recognition_movement import MovementDetector
from ..src.recognition_face import FaceDetector
from ..src.client import ImageClient
from ..src.encoder import Encoder
import cv2

if __name__ == "__main__":
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    movement_detector = MovementDetector(cap)
    movement_detector.detect_movement()
    
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    detector = FaceDetector(cascade_path, cap)
    detector.detect_faces()
    
    cap.release()
    cv2.destroyAllWindows()
    
    server_host = 'localhost'
    server_port = 8080
    image_path = 'face.jpg'
    
    client = ImageClient(server_host, server_port)
    client.connect_to_server()
    client.send_image(image_path)
    client.close_connection()