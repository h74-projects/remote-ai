import cv2
from src.client import *
from src.client_UI import *
from src.recognition_movement import *

def choose_label():
    label_chooser = MenuChooser()
    chosen = label_chooser.run()
    print(f"Selected Number: {chosen}")
    return chosen

def map_chosen_to_string(chosen):
    label_mapping = {
        0: "@exit+nisan",
        1: "@face+nisan",
        2: "@object+nisan",
        3: "@fingers+nisan",
        4: "@expression+nisan",
        5: "@robot+nisan",
        6: "@robot_view+nisan"
    }
    return label_mapping.get(chosen, "@exit+nisan")

def main():
    chosen = choose_label()
    chosen = map_chosen_to_string(chosen)
    server_host = 'localhost'
    server_port = 8080
    client = ImageClient(server_host, server_port)

    if chosen == "@exit+nisan" or chosen == "@robot_view+nisan":
        client = ImageClient(server_host, server_port)
        client.connect_to_server()
        response = client.send_label(chosen)
        return
    
    cap = cv2.VideoCapture(0)
    detector = MovementDetector(cap)
    detected_frame = detector.detect_movement()
    cap.release()
    
    client.connect_to_server()
    image_data = cv2.imencode('.jpg', detected_frame)[1].tobytes()

    response = client.send_label(chosen)
    print(response)
    response = client.send_image(image_data)
    print(response)
    
    client.close_connection()

if __name__ == "__main__":
    main()
