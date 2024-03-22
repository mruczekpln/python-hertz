import cv2 as cv
import numpy as np

drawing = False
shape = 'c'
circleSize = 5
ix, iy = -1, -1

def drawCircle(event, x, y, flags, param):
    global drawing, shape, ix, iy

    if event == cv.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y 

    elif event == cv.EVENT_MOUSEMOVE:
        if drawing == True:
            if shape == 'c':
                cv.circle(img, (x, y), circleSize, (255, 0, 0), -1)
            elif shape == 'r':
                cv.rectangle(img, (ix, iy), (x, y), (0, 255, 0), -1)

    elif event == cv.EVENT_LBUTTONUP:
        drawing = False
        if shape == 'c':
            cv.circle(img, (x, y), circleSize, (255, 0, 0), -1)
        elif shape == 'r':
            cv.rectangle(img, (ix, iy), (x, y), (0, 255, 0), -1)

def drawGUI(): 
    global circleSize

    cv.rectangle(img, (0, 0), (512, 50), (255, 255, 255), -1)
    cv.putText(img, f'Circle size: {circleSize}', (0, 30), font, .75, (0,0,0), 2, cv.LINE_AA)


blank = np.zeros((512, 512, 3), np.uint8)
img = np.copy(blank)

font = cv.FONT_HERSHEY_SIMPLEX
drawGUI()

cv.namedWindow('image')
cv.setMouseCallback('image', drawCircle)

while True:
    cv.imshow('image', img)

    keyPressed = cv.waitKey(1) & 0xFF

    if keyPressed == ord('m'):
        shape = 'r' if shape == 'c' else 'c'

    elif keyPressed == ord('+'):
        circleSize += 5
        drawGUI()
    elif keyPressed == ord('-'):
        circleSize -= 5
        drawGUI()

    elif keyPressed == ord('r'):
        img = np.copy(blank)
        drawGUI()

    elif keyPressed == ord('q'):
        break

cv.destroyAllWindows()