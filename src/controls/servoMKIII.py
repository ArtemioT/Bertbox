#3 servo control, start mode and fill mode 

from gpiozero import Servo
from time import sleep

DIVERTER_VALVE_PIN = 18
INLET_VALVE_PIN = 24
DRAIN_VALVE_PIN = 22

diverter_valve = Servo(
    DIVERTER_VALVE_PIN,
    min_pulse_width = 0.5/1000, #0 DEG
    max_pulse_width = 1.5/1000  #90 DEG
)

inlet_valve = Servo(
    INLET_VALVE_PIN,
    min_pulse_width = 0.5/1000, #0 DEG
    max_pulse_width = 1.5/1000  #90 DEG
)

drain_valve = Servo(
    DRAIN_VALVE_PIN,
    min_pulse_width = 0.5/1000, #0 DEG
    max_pulse_width = 1.5/1000  #90 DEG
)

def set_fill_mode():
    diverter_valve.max()
    inlet_valve.max()
    drain_valve.max()

def set_start_mode():
    diverter_valve.min()
    inlet_valve.min()
    drain_valve.min()
    
def simple_drain():
    drain_valve.min()
    


try:
    
    sleep(2)
    
    
    set_fill_mode()
    
    sleep(2) 
    
    set_start_mode()
    
    sleep(1)
    
finally:
    diverter_valve.detach()
    inlet_valve.detach()
