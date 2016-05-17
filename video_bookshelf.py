#!/usr/bin/env python
# import the necessary packages
from collections import deque
from os import system
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import pprint
import time

hsv_ranges = {
     'blue':      {'high': [99, 255, 255], 'low': [85, 50, 50]},
     'fl yellow': {'high': [40, 175, 225], 'low': [26, 140, 190]},
     'green':     {'high': [75, 255, 255], 'low': [40, 50, 50]},
     'navy':      {'high': [110, 255, 255], 'low': [100, 60, 70]},
     'orange':    {'high': [18, 255, 255], 'low': [5, 180, 200]},
     'pink':      {'high': [170, 255, 255], 'low': [150, 60, 120]},
     'red':       {'high': [5, 255, 255], 'low': [0, 100, 100]},
     'violet':    {'high': [150, 150, 180], 'low': [115, 60, 75]},
     'yellow':    {'high': [25, 255, 255], 'low': [20, 150, 150]}}

shortcuts = {
        'g': 'green',
        'b': 'blue',
        'n': 'navy',
        'p': 'pink',
        'o': 'orange',
        'r': 'red',
        'v': 'violet',
        'y': 'yellow',
        'f': 'fl yellow',
        }

rects = {
        'green': (20, 500),
        'blue': (20, 500),
        'navy': (20, 500),
        'pink': (20, 500),
        'orange': (20, 500),
        'red': (20, 500),
        'violet': (20, 500),
        'yellow': (20, 500),
        'fl yellow': (20, 500),
        }

pp = pprint.PrettyPrinter()

rect_x = 30
rect_y = 333
x_co = 0
y_co = 0
hsv_data = 0

def calibrate_colors():
    global log
    for s,c in shortcuts.iteritems():
        if k == ord(s) and len(log) > 0:
            low  = []
            high = []
            for i in range (0, len(log)):
                if len(low) == 0:
                    low = list(log[i])
                else:
                    low[0] = min(low[0], log[i][0])
                    low[1] = min(low[1], int(log[i][1] *.66))
                    low[2] = min(low[2], int(log[i][2] *.66))
                if len(high) == 0:
                    high = list(log[i])
                else:
                    high[0] = max(high[0], log[i][0])
                    high[1] = 255 #max(high[1], log[i][1])
                    high[2] = 255 #max(high[2], log[i][2])
            hsv_ranges[c]['high'] = list(high)
            hsv_ranges[c]['low'] = list(low)
            rects[c] = (rect_x, rect_y)
            log.clear()

def on_mouse(event,x,y,flag,param):
  global x_co
  global y_co
  global hsv_data
  global log
  if(event==cv2.EVENT_MOUSEMOVE):
    x_co=x
    y_co=y
  if(event==cv2.EVENT_LBUTTONDOWN):
    if hsv_data.any():
        log.append(hsv_data)
    #log.popleft()
      
def findColor(img, img2, lower, upper, color, row):

    found = False
    shapeMask = cv2.inRange(img, lower, upper)

    # find the contours in the mask
    (_, cnts, _) = cv2.findContours(shapeMask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_TC89_L1)

    # contour approximation methods:
    # CHAIN_APPROX_NONE
    # CHAIN_APPROX_SIMPLE
    # CHAIN_APPROX_TC89_L1
    # CHAIN_APPROX_TC89_KCOS

    status = color + ":"
    #status2 = color + " range: " + str(lower) + " to " + str(upper)
    # loop over the contours
    for c in cnts:
        area = cv2.contourArea(c)
        target_area = rects[color][0] * rects[color][1]
        if area > target_area:
            status += " " + str(area)
            found = True
            cv2.drawContours(img2, [c], -1, (
                (lower[0] * 1.0+ upper[0] * 1.0)/2, 
                255, 255 ), 2)
    cv2.putText(img2, status, (10, 10+row * 15), cv2.FONT_HERSHEY_SIMPLEX, .5, (55,25,255), 1)
    return found

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera(resolution=(1024,768))
# allow the camera to warmup
time.sleep(0.1)

cv2.namedWindow("cv", 1)
cv2.setMouseCallback("cv", on_mouse, 0);


log = deque(maxlen=10)
while (True):
    rawCapture = PiRGBArray(camera)

    # grab an image from the camera
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array
    #image = cv2.resize(image, (0, 0), fx=0.75, fy=0.75)
    image = cv2.blur(image, (2,2))
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv_copy = hsv.copy()

    disp_row = 1
    for k, v in hsv_ranges.iteritems():
        lower = np.array(v['low'])
        upper = np.array(v['high'])
        color_found = findColor(hsv, hsv_copy, lower, upper, k, disp_row)
        disp_row += 1

    for i in range (0, len(log)):
        hsv_data = log[i]
        if hsv_data != "":
            logstr =   "H:" + str(hsv_data[0]) + \
                      " S:" + str(hsv_data[1]) + \
                      " V:" + str(hsv_data[2])
            cv2.putText(hsv_copy, logstr, (10, 12 + (disp_row + i) * 15), cv2.FONT_HERSHEY_SIMPLEX, .5, (55, 25, 255), 1)

    # overlay the HSV data of pixel under cursor
    hsv_data=hsv[y_co,x_co]
    cv2.putText(hsv_copy, 
                str(hsv_data[0])+","+str(hsv_data[1])+","+str(hsv_data[2]), 
                (x_co,y_co),
                cv2.FONT_HERSHEY_SIMPLEX, .5, (55,25,255), 2)

    # draw the selection rectangle
    hsv_copy = cv2.rectangle(hsv_copy, 
            (x_co, y_co), (x_co+rect_x, y_co+rect_y), (179,255,255), 1)

    image = cv2.cvtColor(hsv_copy, cv2.COLOR_HSV2BGR)
    cv2.imshow("cv", image)

    k = cv2.waitKey(5)
    if k == -1:
        continue
    elif k == 27:
        break
    elif k == ord('c'):
        log.clear()
    elif k == ord('w'):
        rect_y = rect_y + 25
    elif k == ord('s'):
        rect_y = rect_y - 25
    elif k == ord('d'):
        rect_x = rect_x + 25
    elif k == ord('a'):
        rect_x = rect_x - 25
    else:
        calibrate_colors()
                    
print "\nhsv_ranges ="
pp.pprint(hsv_ranges)

