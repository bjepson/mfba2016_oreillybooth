# import the necessary packages
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

x_co = 0
y_co = 0
hsv_data = 0
def on_mouse(event,x,y,flag,param):
  global x_co
  global y_co
  global hsv_data
  if(event==cv2.EVENT_MOUSEMOVE):
    x_co=x
    y_co=y
  if(event==cv2.EVENT_LBUTTONDOWN):
    print "H:",hsv_data[0]," S:",hsv_data[1]," V:",hsv_data[2]
      
def findColor(img, lower, upper):

    found = False
    shapeMask = cv2.inRange(img, lower, upper)

    # find the contours in the mask
    (_, cnts, _) = cv2.findContours(shapeMask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    #print "I found %d shapes" % (len(cnts))
    #cv2.imshow("Mask", shapeMask)
    #while (1):
        #if cv2.waitKey(0) == 27:
            #break

    # loop over the contours
    for c in cnts:
        area = cv2.contourArea(c)
        #print area
        if area > 10000:
            print "book of size " + str(area)
            found = True
            cv2.drawContours(img, [c], -1, ((lower[0] + upper[0])/2, 128, 255), 8)
    return found

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
# allow the camera to warmup
time.sleep(0.1)

cv2.namedWindow("cv", 1)
cv2.setMouseCallback("cv",on_mouse, 0);

while (True):
    rawCapture = PiRGBArray(camera)

    # grab an image from the camera
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # find all the 'green' shapes in the image
    lower = np.array([50, 50, 50])
    upper = np.array([80, 255, 255])
    green_found = findColor(hsv, lower, upper)
    
    # find all the 'pink' shapes in the image
    lower = np.array([320/2, 100, 100])
    upper = np.array([340/2, 255, 255])
    pink_found = findColor(hsv, lower, upper)

    # find all the 'red' shapes in the image
    lower = np.array([341/2, 100, 100])
    upper = np.array([360/2, 255, 255])
    red_found = findColor(hsv, lower, upper)
    
    # find all the 'violet' shapes in the image
    lower = np.array([250/2, 50, 50])
    upper = np.array([299/2, 255, 255])
    violet_found = findColor(hsv, lower, upper)

    hsv = cv2.resize(hsv, (0, 0), fx=0.5, fy=0.5)
    hsv_data=hsv[y_co,x_co]
    cv2.putText(hsv, 
                str(hsv_data[0])+","+str(hsv_data[1])+","+str(hsv_data[2]), 
                (x_co,y_co),
                cv2.FONT_HERSHEY_SIMPLEX, .5, (55,25,255), 2)

    image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    cv2.imshow("cv", image)
    if cv2.waitKey(10) == 27:
        break
