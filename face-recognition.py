import cv2 as cv

def recognizeAndDisplay(frame):
    grayFrame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    grayFrame = cv.equalizeHist(grayFrame) 

    # Face recognition
    faces = faceCascade.detectMultiScale(grayFrame, )
    for (x, y, w, h) in faces:
        faceCenter = (x + w // 2, y + h // 2)
        frame = cv.ellipse(frame, faceCenter, (w // 2, h // 2), 0, 0, 360, (255, 0, 255), 4)

        faceROI = grayFrame[y:y+h, x:x+w]
    
        # Smile Recognition
        smiles = smileCascade.detectMultiScale(faceROI)
        for (x2, y2, w2, h2) in smiles:
            smileCenter = (x + x2 + w2 // 2, y + y2 + h2 // 2)
            frame = cv.ellipse(frame, smileCenter, (w2 //2, h2 // 2), 0, 0, 360, (0, 255, 255), 4)

    cv.imshow('Face recognition', frame)

faceCascade = cv.CascadeClassifier()
smileCascade = cv.CascadeClassifier()

# Loading cascades
faceCascade.load(cv.samples.findFile("models/haarcascade_frontalface_alt.xml"))
smileCascade.load(cv.samples.findFile("models/haarcascade_smile.xml"))

# Reading camera stream
capture = cv.VideoCapture(0)

# Reading online drone camera stream
# capture = cv.VideoCapture('http://192.168.255.106:9081')

if not capture.isOpened:
    print('Error reading camera stream')
    exit(0)

while True:
    ret, frame = capture.read()
    if frame is None:
        print('No frames from camera')
        break

    recognizeAndDisplay(frame)

    if cv.waitKey(1) == ord('q'):
        break

capture.release()
cv.destroyAllWindows()