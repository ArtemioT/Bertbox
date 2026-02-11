# Sensor  State Machine Module - RoboJar Automation
# Created By Evan Corwin
# Last Modified 2/10/2026

from abc import ABC, abstractmethod
from enum import Enum
import time
from typing import Optional
from Logging_System import append_row_csv, log_state_change, LoggingPath
import gpiozero



class SensorState(Enum):
    IDLE = 'idle'
    ACTIVE = 'active'


class State(ABC):
    """Abstract base class for all states"""
    
    def __init__(self, name: str):
        self.name = name
        self.SystemPath = LoggingPath.SystemPath()

    @abstractmethod
    def enter(self, context) -> None:
        """Called when entering this state"""
        pass
    
    @abstractmethod
    def exit(self, context) -> None:
        """Called when exiting this state"""
        pass
    
    @abstractmethod
    def handle_event(self, context, event: PumpState):
        """Handle events in this state"""
        pass
class IdleState(State):
    def __init__(self):
        super().__init__("IDLE")
    
    def enter(self, context) -> None:
        print("Sensor is Idle")
        append_row_csv(self.SystemPath, {'Time': time.strftime("%Y-%m-%d %H:%M:%S"), 'Name': context.name, 'Status': 'IDLE', 'Notes': ''}, ['Time', 'Name', 'Status', 'Notes'])
        log_state_change(self.SystemPath, context.name, 'IDLE', '')
    def exit(self, context) -> None:
        print("Exiting IDLE state...")
    
    def handle_event(self, context, event: ValveState):
        if event == SensorState.ACTIVE:
            context.state = ActiveState()
            context.state.enter(context)

class ActiveState(State):
    def __init__(self):
        super().__init__("ACTIVE")
    
    def enter(self, context) -> None:
        print("Sensor is Active")
        append_row_csv(self.SystemPath, {'Time': time.strftime("%Y-%m-%d %H:%M:%S"), 'Name': context.name, 'Status': 'Active', 'Notes': ''}, ['Time', 'Name', 'Status', 'Notes'])
        log_state_change(self.SystemPath, context.name, 'Active', '')
    def exit(self, context) -> None:
        print("Exiting IDLE state...")
    
    def handle_event(self, context, event: ValveState):
        if event == SensorState.IDLE:
            context.state = IdleState()
            context.state.enter(context)


class SensorStateMachine:
    def __init__(self, name: str = "Sensor"):
        self.name = name
        self.SystemPath = LoggingPath.SystemPath()
        self.state: State = IdleState()  ## Initial state Change depending initial condition
        self.state.enter(self)

    
    def on_event(self, event: PumpState):
        self.state.handle_event(self, event)
    
    def run(self):
        print(f"Current Sensor State: {self.state.name}")
        # central log only when status changes
        log_state_change(self.SystemPath, self.name, self.state.name, '')
        
        time.sleep(1)

def CreateSensorStateMachine(name: str = "Sensor") -> SensorStateMachine:
    return SensorStateMachine(name)