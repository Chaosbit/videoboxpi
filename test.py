#!/usr/bin/env python2.7  

import RPi.GPIO as GPIO
import signal
from pyomxplayer import OMXPlayer

GPIO.setmode(GPIO.BCM)  
  
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
  
omx = OMXPlayer('/videos/dgzrs.mp4', '-o local -rb')
  
def my_callback2(channel):
    global omx
    if GPIO.input(channel) > 0:
    	print "stopping video"
	# omx.toggle_pause() 
    else:
        print "starting video"
	# omx.stop()
	# omx = OMXPlayer('/videos/dgzrs.mp4', '-o local -rb')
  
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
