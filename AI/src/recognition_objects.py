import cv2
import numpy as np

class ObjectDetector:
    def __init__(self, a_frame):
        self.frame = a_frame
        self.net = cv2.dnn.readNet("assets/yolov3.weights", "assets/yolov3.cfg")
        with open("assets/coco.names", "r") as f:
            self.classes = [line.strip() for line in f.readlines()]

        self.output_layers = ['yolo_82', 'yolo_94', 'yolo_106']

    def detect_objects(self):
        self.frame = cv2.resize(self.frame, None, fx=0.4, fy=0.4)
        height, width, channels = self.frame.shape

        blob = cv2.dnn.blobFromImage(self.frame, 1 / 255.0, (416, 416), swapRB=True, crop=True)
        self.net.setInput(blob)

        outs = self.net.forward(self.output_layers)
        
        class_ids = []
        confidences = []
        boxes = []

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.66: #Can be changed for better accuracy
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Apply Non-Maximum Suppression (NMS) to remove duplicate detections
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        # Draw bounding boxes and labels
        font = cv2.FONT_HERSHEY_PLAIN
        colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
        objects = []
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]])
                confidence = confidences[i]
                color = colors[class_ids[i]]

                # Draw the bounding box and label
                text = f"{label} {confidence:.2f}"
                objects = f"@{label}"
                cv2.rectangle(self.frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(self.frame, text, (x, y + 30), font, 2, color, 3)

        return objects, boxes
    
        # print(objects)
        # while True:
        #     cv2.imshow("Object Detection", self.frame)
        #     # Press 'q' to exit the loop
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break
        
    def save_object_to_file(self, face_region):
        file_path = 'object.jpg'
        cv2.imwrite(file_path, face_region)
        print(f"object saved to {file_path}")

    def convert_to_jpeg(self, image_array):
        _, jpeg_data = cv2.imencode('.jpg', image_array)
        jpeg_bytes = jpeg_data.tobytes()

        return jpeg_bytes


# if __name__ == "__main__":
#     video_capture = cv2.VideoCapture(0)
#     ret, img = video_capture.read()
#     obj_det = ObjectDetector(img)
#     obj_det.detect_objects()
