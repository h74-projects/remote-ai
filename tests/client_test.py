import socket

# Specify the server's host and port
server_host = 'localhost'
server_port = 8080

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((server_host, server_port))

# Read the image file as binary data
image_path = 'face.jpg'  # Replace with the path to your image file
message = "dogs"

try:
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    # Send the image data to the server
    client_socket.send(image_data)

    # Receive data from the server (optional)
    data = client_socket.recv(1024)
    print("Received from server:", data.decode('utf-8'))
except FileNotFoundError:
    print(f"File not found: {image_path}")

# Close the client socket
client_socket.close()
