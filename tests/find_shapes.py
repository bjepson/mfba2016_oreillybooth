# import the necessary packages
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

def findColor(image, lower, upper):

	found = False
	shapeMask = cv2.inRange(image, lower, upper)

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
		approx = cv2.approxPolyDP(c, .01 * cv2.arcLength(c, True), True)
		if len(approx) == 4:
			print "Square!"
			found = True
			cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
	return found

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
rawCapture = PiRGBArray(camera)

# allow the camera to warmup
time.sleep(0.1)

# grab an image from the camera
camera.capture(rawCapture, format="bgr")
image = rawCapture.array

# find all the 'green' shapes in the image
lower = np.array([10, 70, 10])
upper = np.array([30, 90, 30])
green_found = findColor(image, lower, upper)

# find all the 'violet' shapes in the image
lower = np.array([55, 65, 85])
upper = np.array([75, 85, 105])
violet_found = findColor(image, lower, upper)

cv2.imshow("Image", image)
while (1):
	if cv2.waitKey(0) == 27:
		break
cv2.destroyAllWindows()
