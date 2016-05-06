# import the necessary packages
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
rawCapture = PiRGBArray(camera)

# allow the camera to warmup
time.sleep(0.1)

# grab an image from the camera
camera.capture(rawCapture, format="bgr")
image = rawCapture.array

# find all the '?' shapes in the image
lower = np.array([0, 20, 0])
upper = np.array([50, 255, 50])
shapeMask = cv2.inRange(image, lower, upper)

# find the contours in the mask
(_, cnts, _) = cv2.findContours(shapeMask.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
print "I found %d shapes" % (len(cnts))
cv2.imshow("Mask", shapeMask)
cv2.waitKey(0)

# loop over the contours
#for c in cnts:
	# draw the contour and show it
	#cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
	#cv2.imshow("Image", image)
	#cv2.waitKey(0)
