# cleanup.py
import RPi.GPIO as GPIO
LED = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)
GPIO.cleanup()
