#!/usr/bin/env python2.7

import sys, argparse
import RPi.GPIO as GPIO
import signal
import ConfigParser
from pyomxplayer import OMXPlayer
from logbook import Logger
from logbook import SyslogHandler

log = Logger('Door Logger')
error_handler = SyslogHandler('videodoor', level='DEBUG')

omx_nachspann = None
omx_nachspann_status = False

with error_handler.applicationbound():

    Config = ConfigParser.ConfigParser()
    Config.read('/etc/videodoor/videodoor.ini')

    def videoplayer_stopped():
        global omx, omx_nachspann, omx_nachspann_status, Config, omx_status
        if not omx_status or omx_nachspann_status:
            return
        log.debug('Setting up the omxplayer instance...')
        File2 = Config.get('video','File2')
        Options2 = Config.get('video','Options2')
        log.info('initializing videoplayer with file %s and options %s' % (File2, Options2))
        log.debug('Playing File2.')
        omx_nachspann_status = True
        omx_nachspann = OMXPlayer(File2, Options2, start_playback=True)

    def kill_nachspann():
        global omx_nachspann, omx_nachspann_status
        omx_nachspann.stop()
        omx_nachspann_status = False
        initialize_video(play=True)


    def initialize_video(play=False):
        global omx, Config, omx_status
        log.debug('Setting up the omxplayer instance...')
        File = Config.get('video','File')
        Options = Config.get('video','Options')
        omx_status = False
        log.info('initializing videoplayer with file %s and options %s' % (File, Options))
        omx = OMXPlayer(File, Options, start_playback=True, stop_callback=videoplayer_stopped)
        if not play:
            omx.toggle_pause()
        log.debug('done.')

    def initialize_hardware():
        global Config
        SensorPin = Config.getint('hardware','SensorPin')
        Bouncetime = Config.getint('hardware','Bouncetime')
        log.debug('setting up GPIO pin %i...' % SensorPin)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SensorPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) #note: keep this PUD_UP
        log.debug('done.')
        GPIO.add_event_detect(SensorPin, GPIO.BOTH, callback=door_callback, bouncetime=Bouncetime)

    def start_video():
        global omx_nachspann, omx, omx_status
        if(omx_status):
            log.warn('video already running')
        else:
            log.debug('start videoplayer')
            omx.toggle_pause()
            omx_status = True

    def stop_video():
        global omx, omx_nachspann, omx_status
        if(omx_status):
            if omx_nachspann_status:
                log.debug('File2 playing, killing it.')
                kill_nachspann()
            log.debug('pause videoplayer')
            omx.toggle_pause()
            log.debug('jump back to beginning')
            omx.previous_chapter()
            omx_status = False
        else:
            log.warn('video not running')

    def door_callback(channel):
        global Config
        log.debug('interrupt detected')
        inverse = Config.getboolean('hardware','Inverse')
        if GPIO.input(channel) > 0:
            if(inverse):
                log.info('door closed')
                stop_video()
            else:
                log.info('door opened')
                start_video()
        else:
            if(inverse):
                log.info('door opened')
                start_video()
            else:
                log.info('door closed')
                stop_video()


    def cleanup():
        if omx:
            omx.stop()
        if omx_nachspann:
            omx_nachspann.stop()
        GPIO.cleanup()

    try:
        initialize_video()
        initialize_hardware()
        log.info('Pausing and waiting for interrupt...')
        signal.pause()
        log.debug('Something went wrong...')


    except KeyboardInterrupt:
        cleanup()
        sys.exit(0)

cleanup()
sys.exit(0)
