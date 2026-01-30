import RPi.GPIO as GPIO
import time


LED = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)

try:
    while(True):
        GPIO.output(LED, 1)
        time.sleep(1)
finally:
    GPIO.cleanup()