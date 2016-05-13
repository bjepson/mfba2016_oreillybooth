import time
from pyomxplayer import OMXPlayer

# Attract mode should be an RSTP of the CV processed image

# requires https://github.com/jbaiter/pyomxplayer with some modifications because it doesn't quite work
omx = OMXPlayer('/home/pi/Desktop/raspi.mp4', start_playback=True)
#time.sleep(3)
#omx.stop()
#omx = OMXPlayer('/home/pi/Desktop/margolis.mp4', start_playback=True)
#time.sleep(3)
#omx.stop()

