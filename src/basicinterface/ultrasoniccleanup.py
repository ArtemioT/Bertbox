import RPi.GPIO as GPIO
import time

# Pin definitions (BCM mode recommended)
TRIG_PIN = 9
ECHO_PIN = 10
RELAY_PIN = 7

MAX_LEVEL = 0.08          # Max water level in meters
SENSOR_TO_BOTTOM = 0.18   # Distance from sensor to bottom in meters

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setup(RELAY_PIN, GPIO.OUT)

GPIO.output(RELAY_PIN, GPIO.HIGH)  # Relay off initially
GPIO.output(TRIG_PIN, GPIO.LOW)


GPIO.cleanup