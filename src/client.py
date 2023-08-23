import socket

class ImageClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = None

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_host, self.server_port))

    def send_image(self, image_path):
        try:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()

            if self.client_socket:
                self.client_socket.send(image_data)
                data = self.client_socket.recv(1024)
                print("Received from server:", data.decode('utf-8'))
        except FileNotFoundError:
            print(f"File not found: {image_path}")

    def close_connection(self):
        if self.client_socket:
            self.client_socket.close()