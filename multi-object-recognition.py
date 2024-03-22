import cv2 as cv
import numpy as np

droneCascade = cv.CascadeClassifier("models/haarcascade_drone_20.xml")
faceCascade = cv.CascadeClassifier("models/haarcascade_frontalface_alt.xml")
eyesCascade = cv.CascadeClassifier("models/haarcascade_eye.xml")

capture = cv.VideoCapture(0)

while True:
    ret, frame = capture.read()
    if frame is None:
        print('No frames from camera')
        break

    grayFrame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    grayFrame = cv.equalizeHist(grayFrame) 

    droneObjects = droneCascade.detectMultiScale(grayFrame)
    for (x, y, w, h) in droneObjects:
        frame = cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 5)
        frame = cv.putText(frame, 'dron', (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 4)

    faceObjects = faceCascade.detectMultiScale(grayFrame)
    for (x, y, w, h) in faceObjects:
        faceCenter = (x + w // 2, y + h // 2)

        frame = cv.ellipse(frame, faceCenter, (w // 2, h // 2), 0, 0, 360, (0, 255, 0), 4)
        frame = cv.putText(frame, 'twarz', (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 4)

        faceRegion = grayFrame[y:y+h, x:x+w]

        eyeObjects = eyesCascade.detectMultiScale(faceRegion)
        for (x2, y2, w2, h2) in eyeObjects:
            eyeCenter = (x + x2 + w2 // 2, y + y2 + h2 // 2)
            radius = int(round((w2 + h2) * .25))

            frame = cv.circle(frame, eyeCenter, radius, (255, 167, 0), 2)
    
    cv.imshow('Drone recognition', frame)

    if cv.waitKey(1) == ord('q'):
        break

capture.release()
cv.destroyAllWindows()