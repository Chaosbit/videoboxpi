#!/usr/bin/env python2.7  

import RPi.GPIO as GPIO
import signal
from pyomxplayer import OMXPlayer

GPIO.setmode(GPIO.BCM)  
  
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)  

omx_status = False 
omx = OMXPlayer('/videos/dgzrs.mp4', '-o both -rb')

def start_video():
    global omx, omx_status
    if(omx_status):
	print "video already running"
    else:
	omx.toggle_pause()
	omx_status = True

def stop_video():
    global omx, omx_status
    if(omx_status):
    	#omx.stop()
    	#omx = OMXPlayer('/videos/dgzrs.mp4', '-o local -rb')
	omx.toggle_pause()
	omx.previous_chapter()
	omx_status = False
    else:
	print "video not running"
  
def my_callback2(channel):
    if GPIO.input(channel) > 0:
    	print "stopping video"
	stop_video()
    else:
        print "starting video"
	start_video()
  
GPIO.add_event_detect(23, GPIO.BOTH, callback=my_callback2, bouncetime=100)  
  
try:  
    print "Pausing and waiting for interrupt..."
    signal.pause()
    print "Something went wrong..."  
  
except KeyboardInterrupt:  
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    omx.stop()
GPIO.cleanup()           # clean up GPIO on normal exit  
omx.stop()
