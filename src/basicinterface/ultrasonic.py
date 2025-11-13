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

print("Ultrasonic pump control started...")

def get_distance():
    """Measure distance in meters using ultrasonic sensor."""
    # Send a 10µs pulse to trigger
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    # Wait for echo start
    start_time = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()

    # Wait for echo end
    stop_time = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        stop_time = time.time()
        # Add timeout protection
        if stop_time - start_time > 0.03:  # 30 ms timeout
            return None

    # Calculate distance (speed of sound = 343 m/s)
    elapsed = stop_time - start_time
    distance = (elapsed * 343.0) / 2.0
    return distance

try:
    while True:
        distance = get_distance()
        if distance is None:
            print("Timeout: No echo received.")
            time.sleep(0.5)
            continue

        water_height = SENSOR_TO_BOTTOM - distance
        if water_height < 0:
            water_height = 0

        print(f"Water height (m): {water_height:.3f}")

        # Control relay based on level
        if water_height < MAX_LEVEL - 0.01:
            GPIO.output(RELAY_PIN, GPIO.HIGH)  # Pump ON
        elif water_height >= MAX_LEVEL:
            GPIO.output(RELAY_PIN, GPIO.LOW)   # Pump OFF

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Exiting program...")

finally:
    GPIO.cleanup()
