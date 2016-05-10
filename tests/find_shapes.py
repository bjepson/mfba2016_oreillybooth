# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from os import system
import numpy as np
import time
import cv2
import curses
from collections import deque

hsv_ranges = {
        'green': { 'low': [30, 50, 50],    'high': [70,  255, 255] },
        'blue':  { 'low': [85, 50, 50],    'high': [105, 255, 255] },
        'pink':  { 'low': [160, 100, 150], 'high': [180, 255, 255] },
        'orange':{ 'low': [5,   200, 200], 'high': [15,  255, 255] },
        'red':   { 'low': [0,   100, 100], 'high': [5,   255, 255] },
        'violet':{ 'low': [140,  80,  50], 'high': [180, 150, 199] },
        'yellow':{ 'low': [20,  200, 200], 'high': [ 30, 255, 255] }
        }

shortcuts = {
        'g': 'green',
        'b': 'blue',
        'p': 'pink',
        'o': 'orange',
        'r': 'red',
        'v': 'violet',
        'y': 'yellow'
        }

x_co = 0
y_co = 0
hsv_data = 0

def on_mouse(event,x,y,flag,param):
  global x_co
  global y_co
  global hsv_data
  global log
  if(event==cv2.EVENT_MOUSEMOVE):
    x_co=x
    y_co=y
  if(event==cv2.EVENT_LBUTTONDOWN):
    log.append(hsv_data)
    log.popleft()
      
def findColor(img, img2, lower, upper, color, screen, row):

    found = False
    shapeMask = cv2.inRange(img, lower, upper)

    # find the contours in the mask
    (_, cnts, _) = cv2.findContours(shapeMask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)

    status = color + ":"
    status2 = color + " range: " + str(lower) + " to " + str(upper)
    # loop over the contours
    for c in cnts:
        area = cv2.contourArea(c)
        #print area
        if area > 15000:
            status += " " + str(area)
            found = True
            cv2.drawContours(img2, [c], -1, (
                (lower[0] * 1.0+ upper[0] * 1.0)/2, 
                255, #(lower[1] + upper[1])/2, 
                255 #(lower[2] + upper[2])/2, 
                ), 4)
    screen.addstr(row, 2, status)
    screen.addstr(row + 20, 2, status2)
    return found

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
# allow the camera to warmup
time.sleep(0.1)

cv2.namedWindow("cv", 1)
cv2.setMouseCallback("cv", on_mouse, 0);

screen = curses.initscr()
screen.border(0)

log = deque(["", "", "", "", "", "", "", "", "", ""])
pad = curses.newpad(12, 26)
pad.border(0)
while (True):
    rawCapture = PiRGBArray(camera)

    # grab an image from the camera
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array
    image = cv2.blur(image, (5,5))

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv_copy = hsv.copy()

    screen.clear()
    screen.border(0)
    disp_row = 3
    for k, v in hsv_ranges.iteritems():
        lower = np.array(v['low'])
        upper = np.array(v['high'])
        color_found = findColor(hsv, hsv_copy, lower, upper, k, screen, disp_row)
        disp_row += 1

    pad.clear()
    pad.border(0)
    for i in range (0, len(log)):
        hsv_data = log[i]
        if hsv_data != "":
            logstr =   "H:" + str(hsv_data[0]) + \
                      " S:" + str(hsv_data[1]) + \
                      " V:" + str(hsv_data[2])
            pad.addstr(i + 1, 1, logstr)
    screen.refresh()
    pad.refresh(0,0, 10,2, 40,40)

    #hsv = cv2.resize(hsv, (0, 0), fx=0.75, fy=0.75)
    hsv_data=hsv[y_co,x_co]
    cv2.putText(hsv_copy, 
                str(hsv_data[0])+","+str(hsv_data[1])+","+str(hsv_data[2]), 
                (x_co,y_co),
                cv2.FONT_HERSHEY_SIMPLEX, .5, (55,25,255), 2)

    image = cv2.cvtColor(hsv_copy, cv2.COLOR_HSV2BGR)
    cv2.imshow("cv", image)
    k = cv2.waitKey(10)
    if k == 27:
        break
    for s,c in shortcuts.iteritems():
        if k == ord(s):
            low  = []
            high = []
            for i in range (0, len(log)):
                if len(low) == 0:
                    low = list(log[i])
                else:
                    low[0] = min(low[0], log[i][0])
                    print type(low[0])
                    low[1] = min(low[1], log[i][1])
                    low[2] = min(low[2], log[i][2])
                if len(high) == 0:
                    high = list(log[i])
                else:
                    high[0] = max(high[0], log[i][0])
                    high[1] = max(high[1], log[i][1])
                    high[2] = max(high[2], log[i][2])
            hsv_ranges[c]['high'] = list(high)
            hsv_ranges[c]['low'] = list(low)
            log = deque(["", "", "", "", "", "", "", "", "", ""])
                    
curses.endwin()
#print '\n'.join(log)

