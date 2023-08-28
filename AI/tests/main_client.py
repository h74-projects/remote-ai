from src.recognition_movement import MovementDetector
from src.client import ImageClient
import cv2

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    movement_detector = MovementDetector(cap)
    movement_detected_frame = movement_detector.detect_movement()
    cap.release()

    server_host = 'localhost'
    server_port = 8080
    client = ImageClient(server_host, server_port)
    
    client.connect_to_server()
    image_data = cv2.imencode('.jpg', movement_detected_frame)[1].tobytes()
    
    response = client.send_image(image_data)
    print(response)
    
    client.close_connection()