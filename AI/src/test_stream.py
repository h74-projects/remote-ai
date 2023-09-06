import socket
import cv2
import numpy as np
import io
from PIL import Image
HOST = "3.239.80.86"  # The server's hostname or IP address
PORT = 3000  # The port used by the server
stp = bytearray([0, 0, 0, 0])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
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