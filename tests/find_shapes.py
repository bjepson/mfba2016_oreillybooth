# import the necessary packages
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

def findColor(img, lower, upper):

    found = False
    shapeMask = cv2.inRange(img, lower, upper)

    # find the contours in the mask
    (_, cnts, _) = cv2.findContours(shapeMask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    print "I found %d shapes" % (len(cnts))
    cv2.imshow("Mask", shapeMask)
    while (1):
        if cv2.waitKey(0) == 27:
            break
    cv2.destroyAllWindows()

    # loop over the contours
    for c in cnts:
        area = cv2.contourArea(c)
        #print area
        if area > 10000:
            print "book!"
            found = True
            cv2.drawContours(img, [c], -1, (70, 255, 255), 2)
    return found

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
rawCapture = PiRGBArray(camera)

# allow the camera to warmup
time.sleep(0.1)

# grab an image from the camera
camera.capture(rawCapture, format="bgr")
image = rawCapture.array
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# find all the 'green' shapes in the image
lower = np.array([60, 70, 70])
upper = np.array([110, 255, 255])
green_found = findColor(hsv, lower, upper)

# find all the 'violet' shapes in the image
lower = np.array([260/2, 70, 70])
upper = np.array([280/2, 255, 255])
violet_found = findColor(hsv, lower, upper)

image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
cv2.imshow("Image", image)
while (1):
    if cv2.waitKey(0) == 27:
        break
cv2.destroyAllWindows()
