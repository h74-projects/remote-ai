import socket
import struct

class ImageClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        while True:  
            try:
                self.client_socket.connect((self.server_host, self.server_port))
                break
            except OSError as e:
                    if e.errno == 111:  
                        self.server_port += 1

    def send_image(self, image_data):
        try:
            if self.client_socket:
                image_size = len(image_data)
                self.client_socket.sendall(struct.pack("!I", image_size))  # Send the size of the image
                self.client_socket.sendall(image_data)
                data = self.client_socket.recv(1024)
                return data
        except Exception as e:
            print(f"Error sending image: {e}")

    def send_label(self, label):
        try:
            if self.client_socket:
                label_bytes = label.encode("utf-8")
                self.client_socket.send(label_bytes)
                data = self.client_socket.recv(1024) 
                return data
        except Exception as e:
            print(f"Error sending label: {e}")


    def close_connection(self):
        if self.client_socket:
            self.client_socket.close()

