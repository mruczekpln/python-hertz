import cv2 as cv
import sys

# image = cv.imread('drone-on-clear-sky1.webp')
image = cv.imread(cv.samples.findFile('assets/drone-on-clear-sky1.webp'))

if image is None:
    sys.exit("Could not find your image.")

cv.imshow("Display window", image)
k = cv.waitKey(0)

# if k == ord("s"):
#     cv.imwrite