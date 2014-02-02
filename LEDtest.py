import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.output(11, True)
GPIO.setup(13, GPIO.OUT)
GPIO.output(13, True)
GPIO.setup(15, GPIO.OUT)
GPIO.output(15, True)
time.sleep(2)

GPIO.cleanup()
