#!/usr/bin/env python2.7  

import RPi.GPIO as GPIO
import signal
from pyomxplayer import OMXPlayer
from logbook import Logger
from logbook import SyslogHandler

log = Logger('Door Logger')
error_handler = SyslogHandler('logbook example', level='DEBUG')

log.debug('setting up GPIO pin 23...')  
GPIO.setmode(GPIO.BCM)  
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
log.debug('done.')

log.debug('Setting up the omxplayer instance...')
omx_status = False 
omx = OMXPlayer('/videos/dgzrs.mp4', '-o both -rb')
log.debug('done.')

def start_video():
    global omx, omx_status
    if(omx_status):
	log.warn('video already running')
    else:
	omx.toggle_pause()
	omx_status = True
	log.info('door opened')

def stop_video():
    global omx, omx_status
    if(omx_status):
	omx.toggle_pause()
	omx.previous_chapter()
	omx_status = False
	log.info('door closed')
    else:
	log.warn('video not running')
  
def my_callback2(channel):
    if GPIO.input(channel) > 0:
	stop_video()
    else:
	start_video()
  
GPIO.add_event_detect(23, GPIO.BOTH, callback=my_callback2, bouncetime=100)  
  
try:  
    log.info('Pausing and waiting for interrupt...')
    signal.pause()
    log.debug('Something went wrong...')  
  
except KeyboardInterrupt:  
    GPIO.cleanup()
    omx.stop()
GPIO.cleanup()
omx.stop()
