from src.recognition_face import *
from src.recognition_objects import *
from src.recognition_hand import *
from src.recognition_facial_expression import *
from src.recognition_thumbs import *
from src.encoder import Encoder
import cv2
import numpy as np
import socket
import threading
import struct
import sys
import requests
from PIL import Image
import io
import time

class LPU:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.server_socket = None
        self.face_detector = None
        self.terminate_server = False

        self.server_ip = "3.239.80.86"
        self.server_port = 3000
        
    def start(self):
        while True:
            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.bind((self.host, self.port))
                break
            except OSError as e:
                if e.errno == 98:  # Address already in use (errno 98 on Linux)
                    print(f"Port {self.port} is already in use. Trying the next port.")
                    self.port += 1

        self.server_socket.listen(128)
        print(f"Server is listening on {self.host}:{self.port}")

        server_thread = threading.Thread(target=self._server_thread)
        server_thread.start()
        server_thread.join()

        self.server_socket.close()
        
    def _server_thread(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Accepted connection from {client_address}")

            label_bytes = client_socket.recv(1024)
            response = "label - OK"
            client_socket.send(response.encode('utf-8'))
            label = label_bytes.decode("utf-8")

            print(label)
            topic, source = label.split("+")

            if topic == "@exit":
                break
                
            image = None

            if topic != "@robot_view":
                image_data = self.receive_image_data_from_client(client_socket)
                response = "image - OK"
                client_socket.send(response.encode('utf-8'))
                image = self.get_image_from_binary(image_data)


            topic , roi = self.get_API_topic(image, topic)

            print(topic)

            if topic !="/sub/robot_view":
                self.package_API(client_socket, source, topic, roi)
        
            if topic != "/sub/robot_view":
                stp = bytearray([0, 0, 0, 0])
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

                        # server_ans = requests.post(self.ron, data=response, timeout= 1)  
                        s.connect((self.server_ip, self.server_port))
                        s.send(response.encode('utf-8'))

                        s.send(stp)

                        res = s.recv(1024)
                        print(res)

                except requests.exceptions.Timeout:
                        print("Request timed out (no response expected)")
                except requests.exceptions.RequestException as e:
                        print(f"An error occurred: {e}")
            else:
                self.get_robot_stream()

    def package_API(self, client_socket, source, topic, roi):
        encoder = Encoder(topic , source , roi)
        response = encoder.encode()
        client_socket.send(response.encode('utf-8'))
        print(response)

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

    def receive_image_data_from_client(self, client_socket):     
        image_size = struct.unpack("!I", client_socket.recv(4))[0]
        image_data = b""
        while True:
            chunk = client_socket.recv(image_size - len(image_data))
            image_data += chunk
            if len(image_data) == image_size:
                break
        
        return image_data
    
    def get_image_from_binary(self, image_data):
        image = np.frombuffer(image_data, dtype=np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image

    def get_API_topic(self, image, topic):
        if topic == "@face":
            self.face_detector = FaceDetector(image)
            image, roi = self.face_detector.detect_faces()
            if roi == (-1,-1,-1,-1):
                topic = "@noface"
        elif topic == "@object":
            obj_det = ObjectDetector(image)
            objects, roi = obj_det.detect_objects()
            topic = objects
        elif topic == "@fingers":
            tracker = HandTracker()  
            image = tracker.handsFinder(image)
            raised_fingers = tracker.positionFinder(image)
            x, y, w, h = (0,0,0,0)
            roi = [(x,y,w,h)]

            for index,bool in enumerate(raised_fingers):
                if bool:
                    topic += str(index + 2)
        elif topic == "@expression":
            emotion_detector = EmotionDetector()
            emotion, roi = emotion_detector.detect_emotions(image)
            topic =f"@{emotion}"

        elif topic == "@robot":
            tracker = ThumbTracker()
            raised = 0
            image = tracker.handsFinder(image)
            state = tracker.thumbsFinder(image)

            x, y, w, h = (0,0,0,0)
            roi = [(x,y,w,h)]
            if state:
                if state == 1:
                    topic = "@forward"
                elif state == -1:
                    topic = "@backward"
                elif state == 0.5:
                    topic = "@right"
                elif state == -0.5:
                    topic = "@left"

        elif topic == "@robot_view":
            x, y, w, h = (0,0,0,0)
            roi = [(x,y,w,h)]
            topic = "/sub/robot_view"

        return topic, roi

    def get_robot_stream(self):
        stp = bytearray([0, 0, 0, 0])

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.server_ip, self.server_port))
            s.sendall(b"/sub/robot_view")
            s.sendall(stp)
            img = bytes()
            while True:
                data = s.recv(640 * 480 * 3)
                tmp = str(data)
                if tmp.startswith("b'robot_view|"):
                    data = data[11:]
                    img = data
                else:
                    img += data
                try:
                    raw_img = Image.open(io.BytesIO(img))
                    open_cv_image = np.array(raw_img)
                    cv2.imshow("t",open_cv_image)
                    cv2.waitKey(50)
                    img = bytes()
                except Exception as error:
                    print(error)