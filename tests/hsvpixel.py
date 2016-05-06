#!/usr/bin/env python
# -*- coding: utf-8 -*-
# returns HSV value of the pixel under the cursor in a video stream
# author: achuwilson
# achuwilson.wordpress.com
# Updated for cv2 api by bjepson
import cv2
import time
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera

x_co = 0
y_co = 0
def on_mouse(event,x,y,flag,param):
  global x_co
  global y_co
  if(event==cv2.EVENT_MOUSEMOVE):
    x_co=x
    y_co=y

cv2.namedWindow("camera", 1)
camera = PiCamera()

font = cv2.FONT_HERSHEY_SIMPLEX
while True:
    rawCapture = PiRGBArray(camera)
    camera.capture(rawCapture, format="bgr")
    src = rawCapture.array
    src = cv2.blur(src, (5,5))
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    cv2.setMouseCallback("camera",on_mouse, 0);
    s=hsv[y_co,x_co]
    print "H:",s[0],"      S:",s[1],"       V:",s[2]
    cv2.putText(src, 
                str(s[0])+","+str(s[1])+","+str(s[2]), 
                (x_co,y_co),
                font, 1, (55,25,255), 2)
    cv2.imshow("camera", src)
    if cv2.waitKey(10) == 27:
        break
