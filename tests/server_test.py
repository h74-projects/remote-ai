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
        # Create a socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the address
        self.server_socket.bind((self.host, self.port))

        # Listen for incoming connections
        self.server_socket.listen(1)
        print(f"Server is listening on {self.host}:{self.port}")

        # Start the server thread
        server_thread = threading.Thread(target=self._server_thread)
        server_thread.start()

        # Check for the 'q' key press to terminate the server
        try:
            while not self.terminate_server:
                key_press = input("Press 'q' to quit: ")
                if key_press == 'q':
                    self.terminate_server = True
                    break
        except KeyboardInterrupt:
            pass

        # Wait for the server thread to finish
        server_thread.join()

        # Close the server socket
        self.server_socket.close()

    def _server_thread(self):
        while not self.terminate_server:
            try:
                # Accept incoming connection
                client_socket, client_address = self.server_socket.accept()
                print(f"Accepted connection from {client_address}")

                # Receive data from the client
                data = client_socket.recv(1024)
                
                # Check if the received data is an image
                if self.is_image(data):
                    response = "You sent an image."
                else:
                    response = "You sent something that is not an image."

                # Send a response to the client
                client_socket.send(response.encode('utf-8'))

                # Close the client socket
                client_socket.close()
            except Exception as e:
                print(f"Error: {e}")

    def is_image(self, data):
        # Check if the data starts with a common image signature
        image_signatures = [b'\xFF\xD8\xFF',  # JPEG
                            b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A']  # PNG

        for signature in image_signatures:
            if data.startswith(signature):
                return True

        return False

if __name__ == "__main__":
    server = SimpleServer()
    server.start()
    sys.exit(0)
