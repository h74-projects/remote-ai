from src.recognition_face import FaceDetector
from src.encoder import Encoder
import numpy as np
import socket
import threading
import cv2
import sys

class SimpleServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.server_socket = None
        self.face_detector = None
        self.terminate_server = False
        self.buffer_size = 128 * 1024
        
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
        
        while not self.terminate_server:
            client_socket, client_address = self.server_socket.accept()
            print(f"Accepted connection from {client_address}")
            
            frame_bytes = client_socket.recv(self.buffer_size)   
            frame = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            
            self.face_detector = FaceDetector(frame)
            image, roi = self.face_detector.detect_faces()
            self.save_face_to_file(image)
            
            encoder = Encoder("test" , "local" , roi)
            response = encoder.encode()
            
            print(response)
            
            client_socket.send(response.encode('utf-8'))
            client_socket.close()

    def is_image(self, data):
        image_signatures = [b'\xFF\xD8\xFF',  # JPEG
                            b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A']  # PNG

        for signature in image_signatures:
            if data.startswith(signature):
                return True

        return False
    
    def save_face_to_file(self, frame):
        if frame is not None:
            file_path = 'face.jpg'
            cv2.imwrite(file_path, frame)
            print(f"Face saved to {file_path}")
        else:
            print("Received an invalid or empty frame, cannot save to file.")
            self.terminate_server = True
