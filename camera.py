import numpy as np
import cv2 as cv

cap = cv.VideoCapture(0)

if not cap.isOpened():
    print("Couldn't open your camera!")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Can't receive frame, exiting...")
        break

    cv.imshow('frame', frame)

    if (cv.waitKey(1) == ord('q')):
        break

cap.release()
cv.destroyAllWindows()