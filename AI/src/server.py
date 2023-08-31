from src.recognition_face import *
from src.recognition_objects import *
from src.recognition_hand import *
# from src.recognition_facial_expression import *
from src.encoder import Encoder
import cv2
import numpy as np
import socket
import threading
import struct
import sys
import requests

class SimpleServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.server_socket = None
        self.face_detector = None
        self.terminate_server = False
        
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_socket.bind((self.host, self.port))

        self.server_socket.listen(1)
        print(f"Server is listening on {self.host}:{self.port}")

        server_thread = threading.Thread(target=self._server_thread)
        server_thread.start()
        
        server_thread.join()
        self.server_socket.close()
        
    def _server_thread(self):     
        client_socket, client_address = self.server_socket.accept()
        print(f"Accepted connection from {client_address}")

        # Receive image size
        image_size = struct.unpack("!I", client_socket.recv(4))[0]
        print(image_size)

        # Receive image data
        image_data = b""
        while True:
            chunk = client_socket.recv(image_size - len(image_data))
            image_data += chunk
            print(len(image_data))
            if len(image_data) == image_size:
                break
        print("passed image loop")

        response = "image - OK"
        client_socket.send(response.encode('utf-8'))

        label_bytes = client_socket.recv(1024)
        print("passed label data")
        
        # Convert image data to a NumPy array
        image = np.frombuffer(image_data, dtype=np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        # Convert label data to a string
        label = label_bytes.decode("utf-8")
        
        print(label)

        topic, source = label.split("+")

        if topic == "@face":
            self.face_detector = FaceDetector(image)
            image, roi = self.face_detector.detect_faces()
            # self.save_face_to_file(image)
            #TODO : this should have the actual name of the person as the topic ie @nisan or @ron etc
        elif topic == "@object":
            obj_det = ObjectDetector(image)
            object, roi = obj_det.detect_objects()
            topic = object
        elif topic == "@hand":
            tracker = HandTracker()  
            image = tracker.handsFinder(image)
            raised_fingers = tracker.positionFinder(image)
            x, y, w, h = (0,0,0,0)
            roi = [(x,y,w,h)]

            topic = "@fingers:"
            for index,bool in enumerate(raised_fingers):
                if bool:
                    topic += str(index + 2)

        print(topic, source)
        
        encoder = Encoder(topic , source , roi)
        response = encoder.encode()
        
        print(response)
        
        client_socket.send(response.encode('utf-8'))
        client_socket.close()
        # server_answer = requests.post('http://44.200.153.80:3000', data=response)

    def is_image(self, data):
        image_signatures = [b'\xFF\xD8\xFF',  # JPEG
                            b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A']  # PNG

        for signature in image_signatures:
            if data.startswith(signature):
                return True

        return False
    
    def save_face_to_file(self, frame):
        if frame is not None and isinstance(frame, np.ndarray) and frame.size > 0:
            file_path = 'face.jpg'
            cv2.imwrite(file_path, frame)
            print(f"Face saved to {file_path}")
        else:
            print("Received an invalid or empty frame, cannot save to file.")
            self.terminate_server = True