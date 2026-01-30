from gpiozero import Servo

DIVERTER_VALVE_PIN = 18
INLET_VALVE_PIN = 24
DRAIN_VALVE_PIN = 22

def define_Valve(pin) -> Servo:

    valve = Servo(
    pin,
    min_pulse_width = 0.5/1000, #0 DEG
    max_pulse_width = 1.5/1000  #90 DEG
    )

    return valve


def open_Valve(valve):
    valve.max()

def close_Valve(valve):
    valve.min()


def what_valve(command):
    test = command.split()

    if test[0] == "VALVE1":
        define_Valve()