import cv2
from src.client import *
from src.client_UI import *
from src.recognition_movement import *
import sys

if __name__ == "__main__":
    label_chooser = MenuChooser()
    chosen = label_chooser.run()
    print(f"Selected Number: {chosen}")
    cap = cv2.VideoCapture(0)
    detector = None
    detected_frame = None

    if chosen == 0:
        exit()
    elif chosen == 1:
        chosen = "@face+nisan"
    elif chosen == 2:
        chosen = "@object+nisan"
    elif chosen == 3:
        chosen = "@hand+nisan"
    elif chosen == 4:
        chosen = "@Expression+nisan"

    detector = MovementDetector(cap)
    detected_frame = detector.detect_movement()
    cap.release()

    server_host = 'localhost'
    server_port = 8080
    client = ImageClient(server_host, server_port)
    
    client.connect_to_server()
    image_data = cv2.imencode('.jpg', detected_frame)[1].tobytes()

    response = client.send_image(image_data)
    print(response)
    response = client.send_label(chosen)
    print(response)
    
    client.close_connection()