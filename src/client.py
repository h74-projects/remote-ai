import socket

class ImageClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = None

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_host, self.server_port))

    def send_image(self, image_data):
        try:
            if self.client_socket:
                self.client_socket.send(image_data)
                data = self.client_socket.recv(1024)
                return data
        except Exception as e:
            print(f"Error sending image: {e}")

    def close_connection(self):
        if self.client_socket:
            self.client_socket.close()