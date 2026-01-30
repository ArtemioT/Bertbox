from typing import Dict

from .Valve_State_Machine import ValveStateMachine, CreateValveStateMachine, ValveState
from .Pump_State_Machine import PumpStateMachine, CreatePumpStateMachine, PumpState


class SystemController:
    """Controller to manage all state machines in the system"""
    
    def __init__(self, num_valves: int = 3):
        # Create valve state machines
        self.valves: Dict[int, ValveStateMachine] = {}
        for i in range(1, num_valves + 1):
            self.valves[i] = CreateValveStateMachine(f"Valve {i}")
        
        # Create pump state machine
        self.pump = CreatePumpStateMachine("Main Pump")
        
        # Sensor state (simple boolean for now)
        self.sensor_active = False
    
    def get_valve(self, valve_number: int) -> ValveStateMachine:
        """Get a valve state machine by number"""
        return self.valves.get(valve_number)
    
    def get_pump(self) -> PumpStateMachine:
        """Get the pump state machine"""
        return self.pump
    
    def get_valve_status(self, valve_number: int) -> dict:
        """Get current status of a valve"""
        valve = self.get_valve(valve_number)
        if not valve:
            return None
        return {
            "valve_number": valve_number,
            "name": valve.name,
            "state": valve.state.name
        }
    
    def get_pump_status(self) -> dict:
        """Get current status of the pump"""
        return {
            "name": self.pump.name,
            "state": self.pump.state.name
        }
    
    def get_sensor_status(self) -> dict:
        """Get current sensor status"""
        return {
            "active": self.sensor_active,
            "state": "ON" if self.sensor_active else "OFF"
        }
    
    def get_system_status(self) -> dict:
        """Get status of all components"""
        return {
            "pump": self.get_pump_status(),
            "valves": {num: self.get_valve_status(num) for num in self.valves.keys()},
            "sensor": self.get_sensor_status()
        }
    
    def reset_all(self) -> dict:
        """Reset all components to idle state"""
        results = {"valves": {}, "pump": {}, "sensor": {}}
        
        # Reset all valves to IDLE
        for valve_num, valve in self.valves.items():
            valve.on_event(ValveState.IDLE)
            results["valves"][valve_num] = {
                "name": valve.name,
                "state": valve.state.name
            }
        
        # Reset pump to IDLE
        self.pump.on_event(PumpState.IDLE)
        results["pump"] = {
            "name": self.pump.name,
            "state": self.pump.state.name
        }
        
        # Turn off sensor
        self.sensor_active = False
        results["sensor"] = {"active": False}
        
        return results
