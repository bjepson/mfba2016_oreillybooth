#!/usr/bin/env python
# import the necessary packages
from collections import deque
from os import system
from picamera.array import PiRGBArray
from picamera import PiCamera
from subprocess import Popen
from pyomxplayer import OMXPlayer
import cv2
import numpy as np
import pprint
import time
from fractions import Fraction

modes = ['auto', 'off', 'sunlight', 'fluorescent', 'sunlight', 'cloudy', 'shade', 'tungsten', 'incandescent', 'flash', 'horizon']
mode = 3

# 'violet': {'high': [149, 255, 255], 'low': [139, 43, 70]},
# 'fl yellow': {'high': [32, 255, 255], 'low': [27, 55, 112]},
hsv_ranges = { 'blue': {'high': [110, 255, 255], 'low': [100, 90, 110]},
 'orange': {'high': [12, 255, 255], 'low': [11, 130, 130]},
 'green': {'high': [52, 255, 255], 'low': [49, 92, 77]},
 'navy': {'high': [120, 255, 255], 'low': [103, 50, 40]},
 'pink': {'high': [160, 255, 255], 'low': [158, 120, 130]},
 'black': {'high': [0, 255, 255], 'low': [0, 60, 120]},
 'yellow': {'high': [35, 255, 255], 'low': [25, 150, 105]}}

rects = {'blue': (55, 333),
 'fl yellow': (30, 200),
 'green': (55, 358),
 'navy': (20, 500),
 'pink': (20, 300),
 'black': (30, 333),
 'orange': (30, 333),
 'yellow': (30, 333)}
 
# 'violet': (30, 333),

# FIXME: allow multiple videos, random selection.
vid_path = '/home/pi/Desktop'
vids = {'yellow': 'raspi.mp4', 'green': 'bbblack.mp4', 'blue': 'margolis.mp4',
        'orange': 'popupfactory.mp4', 'navy': 'popupfactory.mp4', 'black': 'hardwarestartup.mp4', 'pink': 'kscottz.mp4'}
 
 #, 'orange': '', 'violet': ''}

shortcuts = { 'g': 'green', 
              'b': 'blue', 
              'n': 'navy', 
              'p': 'pink',
              'o': 'orange', 
              'y': 'yellow', 
              'f': 'fl yellow' }

#              'v': 'violet', 

def calibrate_colors():
    global hsv_samples
    for s,c in shortcuts.iteritems():
        if k == ord(s):
            rects[c] = (rect_x, rect_y)
            if len(hsv_samples) > 0:
                low  = []
                high = []
                for i in range (0, len(hsv_samples)):
                    if len(low) == 0:
                        low = list(hsv_samples[i])
                    else:
                        low[0] = min(low[0], hsv_samples[i][0])
                        low[1] = min(low[1], int(hsv_samples[i][1] *.66))
                        low[2] = min(low[2], int(hsv_samples[i][2] *.66))
                    if len(high) == 0:
                        high = list(hsv_samples[i])
                    else:
                        high[0] = max(high[0], hsv_samples[i][0])
                        high[1] = 255 #max(high[1], hsv_samples[i][1])
                        high[2] = 255 #max(high[2], hsv_samples[i][2])
                hsv_ranges[c]['high'] = list(high)
                hsv_ranges[c]['low'] = list(low)
                hsv_samples.clear()

def on_mouse(event,x,y,flag,param):
  global x_co
  global y_co
  global hsv_data
  global hsv_samples
  global last_seen
  if(event==cv2.EVENT_MOUSEMOVE):
    x_co=x
    y_co=y
  if(event==cv2.EVENT_LBUTTONDOWN):
    if hsv_data.any():
        hsv_samples.append(hsv_data)
    last_seen = {}
    #hsv_samples.popleft()
      
def findColor(img, img2, lower, upper, color, row):

    found = False
    shapeMask = cv2.inRange(img, lower, upper)

    # find the contours in the mask
    (_, cnts, _) = cv2.findContours(shapeMask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_NONE)

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

omx=False
curr_vid_color = ""
pp = pprint.PrettyPrinter()
rect_x = 30
rect_y = 333
x_co = 0
y_co = 0
hsv_data = 0
last_seen = {}
start_time = time.time()
lost_item_delay = 4; # something has gone missing for this long
zoom = 1

# initialize the camera 
camera = PiCamera(resolution=(1024,768))
camera.zoom = (.5 * (1-zoom), 0, zoom, zoom)
camera.awb_mode = modes[mode]
camera.flash_mode = 'on'
# allow the camera to warm up
time.sleep(1)

cv2.namedWindow("cv", cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow("cv", 0, 0)
cv2.setMouseCallback("cv", on_mouse, 0);
cv2.setWindowProperty("cv",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

hsv_samples = deque(maxlen=10)
while (True):
    rawCapture = PiRGBArray(camera)

    # grab an image from the camera
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array
    image = cv2.flip(image, 1)
    #image = cv2.resize(image, (0, 0), fx=0.75, fy=0.75)
    image = cv2.blur(image, (2,2))
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv_copy = hsv.copy()
    bottom = hsv_copy.shape[0]

    disp_row = 1
    for k, v in hsv_ranges.iteritems():
        lower = np.array(v['low'])
        upper = np.array(v['high'])
        color_found = findColor(hsv, hsv_copy, lower, upper, k, disp_row)
        disp_row += 1
        if color_found:
            last_seen[k] = time.time() - start_time
        last_seen_str = ""
        if k in last_seen:
            now = time.time() - start_time
            last_seen_str = str(int(now) - int(last_seen[k]))
        cv2.putText(hsv_copy, k + " last seen: " + last_seen_str, (10, bottom - (disp_row* 15)), cv2.FONT_HERSHEY_SIMPLEX, .5, (55,25,255, 1))

    # Display the current list of accumulated color samples
    for i in range (0, len(hsv_samples)):
        hsv_data = hsv_samples[i]
        if hsv_data != "":
            hsv_samplestr =   "H:" + str(hsv_data[0]) + \
                      " S:" + str(hsv_data[1]) + \
                      " V:" + str(hsv_data[2])
            cv2.putText(hsv_copy, hsv_samplestr, (10, 12 + (disp_row + i) * 15), cv2.FONT_HERSHEY_SIMPLEX, .5, (55, 25, 255), 1)

    # Display current awb mode
    cv2.putText(hsv_copy, "AWB mode: " + camera.awb_mode, (10, bottom - 15), cv2.FONT_HERSHEY_SIMPLEX, .5, (55,25,255, 1))

    # overlay the HSV data of pixel under cursor
    try:
        hsv_data=hsv[y_co,x_co]
        cv2.putText(hsv_copy, 
                    str(hsv_data[0])+","+str(hsv_data[1])+","+str(hsv_data[2]), 
                    (x_co,y_co),
                    cv2.FONT_HERSHEY_SIMPLEX, .5, (55,25,255), 2)
    except Error as e:
        print e

    # draw the selection rectangle
    hsv_copy = cv2.rectangle(hsv_copy, 
            (x_co, y_co), (x_co+rect_x, y_co+rect_y), (179,255,255), 1)

    cv2.putText(hsv_copy, 
                "See what happens if you pick up a highlighted book...",
                (50,500),
                cv2.FONT_HERSHEY_SIMPLEX, 1.1, (55,25,255), 2)
    image = cv2.cvtColor(hsv_copy, cv2.COLOR_HSV2BGR)
    cv2.imshow("cv", image)

    k = cv2.waitKey(10)
    if k != -1:
        last_seen = {}
        if k == 27:
            break
        elif k == ord('c'):
           hsv_samples.clear()
        elif k == ord('w'):
            rect_y = rect_y + 25
        elif k == ord('s'):
            rect_y = rect_y - 25
        elif k == ord('d'):
            rect_x = rect_x + 25
        elif k == ord('a'):
            rect_x = rect_x - 25
        elif k == ord('m'):
            mode += 1
            if mode >= len(modes):
                mode = 0
            camera.awb_mode = modes[mode]
        elif k == ord('z'):
            zoom = np.float16(zoom) - .2
            if zoom <= 0:
                zoom = 1
            print str(1-zoom) + ":" + str(zoom)
            camera.zoom = (.5 * (1-zoom), 0, zoom, zoom)
        else:
            calibrate_colors()
       
    lost_one = False
    for k, v in last_seen.iteritems():
        now = time.time() - start_time
        if now - v > lost_item_delay:
            print k + " has gone missing " + str(now - v) + " seconds"
            if vids[k]:
                if omx:
                    omx.stop()
                omx = OMXPlayer(vid_path + "/" + vids[k], start_playback=True)
                curr_vid_color = k
            lost_one = True
        else:
            if k == curr_vid_color and omx:
                omx.stop()
    if lost_one:
        last_seen = {}

if omx:
    omx.stop()

print "\nhsv_ranges ="
pp.pprint(hsv_ranges)
print "\nrects ="
pp.pprint(rects)

