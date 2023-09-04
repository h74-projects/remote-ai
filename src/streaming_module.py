import cv2 as cv

class streaming_module:
    
    def detect_motion(algo = 'MOG2'):
        if algo == 'MOG2':
            backSub = cv.createBackgroundSubtractorMOG2()
        else:
            backSub = cv.createBackgroundSubtractorKNN()
    
        capture = cv.VideoCapture("/dev/video0")
        
        if not capture.isOpened():
            print('Unable to open videoa device')
            exit(0)
        
        while True:
            ret, frame = capture.read()
            if frame is None:
                break
            
            fgMask = backSub.apply(frame)
            white_pixels = cv.findNonZero(fgMask)
            
            cv.rectangle(fgMask, (10, 2), (100,20), (255,255,255), -1)
            cv.putText(fgMask, str(len(white_pixels)), (15, 15),
            cv.FONT_HERSHEY_SIMPLEX, 0.5 , (0,0,0))

            if(len(white_pixels) > 1000):
                streaming_module.send("motion detected")
            
            #cv.imshow('Frame', frame)
            cv.imshow('FG Mask', fgMask)
            keyboard = cv.waitKey(30)
            if keyboard == 'q' or keyboard == 27:
                break
    
    def connect():
        pass

    def send(msg):
        print(msg)

if __name__ == '__main__':
    streaming_module.detect_motion()