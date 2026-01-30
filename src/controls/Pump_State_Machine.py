# Pump State Machine Module - RoboJar Automation
# Created By Evan Corwin
# Last Modified 1/13/2026

from abc import ABC, abstractmethod
from enum import Enum
import time
from typing import Optional
from Logging_System import append_row_csv, log_state_change, LoggingPath



class PumpState(Enum):
    IDLE = 'idle'
    PRIMING = 'priming'
    RUNNING = 'running'


class State(ABC):
    """Abstract base class for all states"""
    
    def __init__(self, name: str):
        self.name = name
        self.SystemPath = LoggingPath.SystemPath()
        self.PumpPath = LoggingPath.PumpPath()

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

class PrimingState(State):
    def __init__(self):
        super().__init__("PRIMING")
    
    def enter(self, context) -> None:
        print("Pump is now Priming.")
        append_row_csv(self.PumpPath, {'Time': time.strftime("%Y-%m-%d %H:%M:%S"), 'Name': context.name, 'Status': 'Priming', 'Notes': ''}, ['Time', 'Name', 'Status', 'Notes'])
        log_state_change(self.SystemPath, context.name, 'Priming', '')
       
    def exit(self, context) -> None:
        print("Exiting Priming state...")
    
    def handle_event(self, context, event: PumpState):
        if event == PumpState.RUNNING:
            context.state = RunningState()
            context.state.enter(context)
        elif event == PumpState.IDLE:
            context.state = IdleState()
            context.state.enter(context)
class RunningState(State):
    def __init__(self):
        super().__init__("RUNNING")
    
    def enter(self, context) -> None:
        print("Pump is now Running.")
        append_row_csv(self.PumpPath, {'Time': time.strftime("%Y-%m-%d %H:%M:%S"), 'Name': context.name, 'Status': 'Running', 'Notes': ''}, ['Time', 'Name', 'Status', 'Notes'])
        log_state_change(self.SystemPath, context.name, 'Running', '')

    def exit(self, context) -> None:
        print("Exiting Running state...")
    
    def handle_event(self, context, event: PumpState):
        if event == PumpState.PRIMING:
            context.state = PrimingState()
            context.state.enter(context)
        elif event == PumpState.IDLE:
            context.state = IdleState()
            context.state.enter(context)
class IdleState(State):
    def __init__(self):
        super().__init__("IDLE")
    
    def enter(self, context) -> None:
        print("Pump is now Idle.")
        append_row_csv(self.PumpPath, {'Time': time.strftime("%Y-%m-%d %H:%M:%S"), 'Name': context.name, 'Status': 'IDLE', 'Notes': ''}, ['Time', 'Name', 'Status', 'Notes'])
        log_state_change(self.SystemPath, context.name, 'IDLE', '')
       
    def exit(self, context) -> None:
        print("Exiting Idle state...")
    
    def handle_event(self, context, event: PumpState):
        if event == PumpState.PRIMING:
            context.state = PrimingState()
            context.state.enter(context)
        elif event == PumpState.RUNNING:
            context.state = RunningState()
            context.state.enter(context)
class PumpStateMachine:
    def __init__(self, name: str = "Default Pump"):
        self.name = name
        self.SystemPath = LoggingPath.SystemPath()
        self.PumpPath = LoggingPath.PumpPath()
        self.state: State = IdleState()  ## Initial state Change depending initial condition
        self.state.enter(self)

    
    def on_event(self, event: PumpState):
        self.state.handle_event(self, event)
    
    def run(self):
        print(f"Current Pump State: {self.state.name}")
        # central log only when status changes
        log_state_change(self.SystemPath, self.name, self.state.name, '')
        
        time.sleep(1)

def CreatePumpStateMachine(name: str = "Default Pump") -> PumpStateMachine:
    return PumpStateMachine(name)