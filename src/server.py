import socket
import threading
import sys

class SimpleServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.server_socket = None
        self.terminate_server = False

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_socket.bind((self.host, self.port))

        self.server_socket.listen(1)
        print(f"Server is listening on {self.host}:{self.port}")

        server_thread = threading.Thread(target=self._server_thread)
        server_thread.start()

        try:
            while not self.terminate_server:
                key_press = input("Press 'q' to quit: ")
                if key_press == 'q':
                    self.terminate_server = True
                    break
        except KeyboardInterrupt:
            pass
        
        server_thread.join()
        self.server_socket.close()
    def _server_thread(self):
        while not self.terminate_server:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"Accepted connection from {client_address}")

                data = client_socket.recv(1024)
                
                if self.is_image(data):
                    response = "You sent an image."
                else:
                    response = "You sent something that is not an image."

                client_socket.send(response.encode('utf-8'))

                client_socket.close()
            except Exception as e:
                print(f"Error: {e}")

    def is_image(self, data):
        image_signatures = [b'\xFF\xD8\xFF',  # JPEG
                            b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A']  # PNG

        for signature in image_signatures:
            if data.startswith(signature):
                return True

        return False
