# State Machine Demo - RoboJar Automation
# Created By Evan Corwin
# Last Modified 1/13/2026

import time
from Valve_State_Machine import CreateValveStateMachine, ValveState
from Pump_State_Machine import CreatePumpStateMachine, PumpState

print("=== State Machine Demo ===\n")
valve_sm = CreateValveStateMachine('Valve 1')
pump_sm = CreatePumpStateMachine()
pump_sm.on_event(PumpState.IDLE)
valve_sm.on_event(ValveState.IDLE)
for i in range(15):  # Run for about 10 iterations
    valve_sm.run()
    pump_sm.run()
    if i == 2:
        valve_sm.on_event(ValveState.OPENING)
    elif i == 4:
        valve_sm.on_event(ValveState.OPEN)
    elif i == 6:
        pump_sm.on_event(PumpState.PRIMING)
    elif i == 8:
        pump_sm.on_event(PumpState.RUNNING)
    elif i == 10:
        pump_sm.on_event(PumpState.IDLE)
    elif i == 12:
        valve_sm.on_event(ValveState.CLOSING)
    elif i == 14:
        valve_sm.on_event(ValveState.CLOSED)
    time.sleep(1)  # Wait a second between updates
print("\n=== State Machine Demo Ended ===")