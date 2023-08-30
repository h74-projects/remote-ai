import cv2
from src.client import *
from src.client_UI import *
from src.recognition_movement import *
# from src.recognition_face import *
# from src.recognition_objects import *
# from src.recognition_hand import *
# from src.recognition_facial_expression import *
import struct

if __name__ == "__main__":
    label_chooser = MenuChooser()
    chosen = label_chooser.run()
    print(f"Selected Number: {chosen}")
    cap = cv2.VideoCapture(0)
    detector = None
    detected_frame = None
    label = None

    if chosen == 1:
        label = "@movement"
        detector = MovementDetector(cap)
        detected_frame = detector.detect_movement()
    # elif chosen == 2:
    #     chosen = "@face"
    #     detector = FaceDetector(cap)
    #     detected_frame = movement_detector.detect_movement()
    # elif chosen == 3:
    #     chosen = "@object"
    #     detector = ObjectDetector(cap)
    #     detected_frame = movement_detector.detect_movement()
    # elif chosen == 4:
    #     chosen = "@hand"
    #     detector = HandTracker(cap)
    #     detected_frame = movement_detector.detect_movement()
    # elif chosen == 5:
        pass
        # detector = ExpressionDetector(cap)
        # detected_frame = movement_detector.detect_movement()
    else:
        pass

    cap.release()

    server_host = 'localhost'
    server_port = 8080
    client = ImageClient(server_host, server_port)
    
    client.connect_to_server()
    image_data = cv2.imencode('.jpg', detected_frame)[1].tobytes()

    response = client.send_image(image_data)
    print(response)
    
    response = client.send_label(label)
    print(response)
    
    client.close_connection()