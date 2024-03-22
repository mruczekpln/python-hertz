import onvif
import cv2 as cv
import numpy as np
import time
from datetime import timedelta


def drawDistanceLine(x, y, windowCenter):
    cv.line(frame, windowCenter, (x, y), (255, 255, 255), 1)


def moveCamera(horizontal, vertical):
    global moveRequest, ptz
    moveRequest.Velocity.PanTilt.x = horizontal * -1
    moveRequest.Velocity.PanTilt.y = vertical * -1
    moveRequest.Velocity.Zoom.x = 0

    ptz.ContinuousMove(moveRequest)


def evaluateMovement(x, y, windowCenter):
    global moving

    windowCenterX, windowCenterY = windowCenter

    xMovement, yMovement = 0, 0
    xOffset = x - windowCenterX
    yOffset = y - windowCenterY

    if xOffset > 150:
        xMovement = 50
    elif xOffset < -150:
        xMovement = -50

    if yOffset > 150:
        yMovement = 50
    elif yOffset < -150:
        yMovement = -50

    if yMovement | xMovement:
        moving = True

        cv.line(frame, windowCenter, (windowCenterX + xMovement, windowCenterY + yMovement), (255, 0, 0), 4)

        cv.putText(frame, f"xOffset: {xOffset}, yOffset: {yOffset}", (0, 100), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

        # moveCamera(xMovement * 0.02, yMovement * 0.02)
    else:
        if moving == True:
            moving == False
            # ptz.Stop(profileToken, True)


def detectDroneObjects(frame, windowCenter):
    global moving

    grayFrame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    grayFrame = cv.equalizeHist(grayFrame)

    droneObjects = droneCascade.detectMultiScale(grayFrame)
    if len(droneObjects) > 0:
        firstX, firstY, firstWidth, firstHeight = droneObjects[0]
        cv.rectangle(frame, (firstX, firstY), (firstX + firstWidth, firstY + firstHeight), (255, 255, 255), 2)
        cv.putText(frame, "drone", (firstX, firstY - 10), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        firstXCenter = firstX + firstWidth // 2
        firstYCenter = firstY + firstHeight // 2

        if canShowInfoLines:
            evaluateMovement(firstXCenter, firstYCenter, windowCenter)
            drawDistanceLine(firstXCenter, firstYCenter, windowCenter)
    else:
        if moving == True:
            moving = False
            ptz.Stop(profileToken, True)


def showFrameStats(frame, frameStart, frameEnd):
    frametime = frameEnd - frameStart
    averageFrametime.append(frametime)
    fps = 1 / frametime

    frametimeText = "Frametime: {:.4f} s".format(frametime)
    averageFrametimeText = "Average frametime: {:.4f} s".format(np.mean(averageFrametime))

    cv.putText(frame, frametimeText, (0, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv.putText(frame, averageFrametimeText, (0, 50), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv.putText(frame, f"FPS: {fps}", (560, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


# camera = onvif.ONVIFCamera('192.168.255.108', 80, 'admin', '')
camera = onvif.ONVIFCamera("192.168.255.108", 80, "admin", "")

profileToken = "MediaProfile00000"

ptz = camera.create_ptz_service()
ptzConfigurationOptions = ptz.GetConfigurationOptions("00000")

moving = False
moveRequest = ptz.create_type("ContinuousMove")
moveRequest.ProfileToken = profileToken
moveRequest.Velocity = ptz.GetStatus({"ProfileToken": profileToken}).Position

droneCascade = cv.CascadeClassifier("models/haarcascade_drone_20.xml")
capture = cv.VideoCapture(0)

canShowInfoLines = False
canShowFrameStats = False
averageFrametime = []

WINDOW_WIDTH, WINDOW_HEIGHT = (640, 480)
windowCenter = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

while True:
    ret, frame = capture.read()
    if frame is None:
        print("No frames from camera")
        break

    frameStart = time.time()

    detectDroneObjects(frame, windowCenter)
    cv.putText(frame, f"moving: {True if moving else False}", (0, 120), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    frameEnd = time.time()

    if canShowFrameStats:
        showFrameStats(frame, frameStart, frameEnd)

    cv.imshow("Drone recognition", frame)

    key = cv.waitKey(1) & 0xFF

    if key == ord("q"):
        break
    elif key == ord("s"):
        canShowInfoLines = not canShowInfoLines
    elif key == ord("f"):
        canShowFrameStats = not canShowFrameStats
    elif key == ord("h"):
        ptz.GotoHomePosition(profileToken)

capture.release()
cv.destroyAllWindows()
