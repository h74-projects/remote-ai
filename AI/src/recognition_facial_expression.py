import cv2
from deepface import DeepFace

# Load the pre-trained emotion detection model
emotion_model = DeepFace.build_model('Emotion')

# Initialize the webcam
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    if not ret:
        break

    # Detect emotions in the frame
    emotions = DeepFace.analyze(frame, actions=['emotion'])

    # Get the emotion predictions
    emotion_predictions = emotions[0]['emotion']

    # Find the dominant emotion with the highest confidence
    dominant_emotion_label = max(emotion_predictions, key=emotion_predictions.get)

    # Display the dominant emotion label on the frame
    cv2.putText(frame, dominant_emotion_label, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    # Display the frame
    cv2.imshow('Facial Expression Detection', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close OpenCV windows
cap.release()
cv2.destroyAllWindows()
