# Valve State Machine Module - RoboJar Automation
# Created By Evan Corwin
# Last Modified 1/13/2026

from abc import ABC, abstractmethod
from enum import Enum
import time
from typing import Optional
from Logging_System import append_row_csv, log_state_change, LoggingPath


class ValveState(Enum):
    IDLE = 'idle'
    CLOSING = 'closing'
    OPENING = 'opening'
    OPEN = 'open'
    CLOSED = 'closed'


class State(ABC):
    """Abstract base class for all states"""
    
    def __init__(self, name: str):
        self.name = name
        self.SystemPath = LoggingPath.SystemPath()
        self.ValvePath = LoggingPath.ValvePath()
    @abstractmethod
    def enter(self, context) -> None:
        """Called when entering this state"""
        pass
    
    @abstractmethod
    def exit(self, context) -> None:
        """Called when exiting this state"""
        pass
    
    @abstractmethod
    def handle_event(self, context, event: ValveState):
        """Handle events in this state"""
        pass


class ClosingState(State):
    def __init__(self):
        super().__init__("CLOSING")
    
    def enter(self, context) -> None:
        
        append_row_csv(self.ValvePath, {'Time': time.strftime("%Y-%m-%d %H:%M:%S"), 'Name': context.name, 'Status': 'Closing', 'Notes': ''}, ['Time', 'Name', 'Status', 'Notes'])
        # central log (only records when state actually changes)
        log_state_change(self.SystemPath, context.name, 'Closing', '')
       
    def exit(self, context) -> None:
        print("Exiting Closing state...")
    
    def handle_event(self, context, event: ValveState):
        if event == ValveState.OPENING:
            context.state = OpeningState()
            context.state.enter(context)
        elif event == ValveState.CLOSED:
            context.state = ClosedState()
            context.state.enter(context)
        elif event == ValveState.OPEN:
            context.state = OpenState()
            context.state.enter(context)
class OpeningState(State):
    def __init__(self):
        super().__init__("OPENING")
    
    def enter(self, context) -> None:
        print("Valve is now Opening.")
        append_row_csv(self.ValvePath, {'Time': time.strftime("%Y-%m-%d %H:%M:%S"), 'Name': context.name, 'Status': 'Opening', 'Notes': ''}, ['Time', 'Name', 'Status', 'Notes'])
        # central log (only records when state actually changes)
        log_state_change(self.SystemPath, context.name, 'Opening', '')
       
    def exit(self, context) -> None:
        print("Exiting Opening  state...")
    
    def handle_event(self, context, event: ValveState):
        if event == ValveState.CLOSING:
            context.state = ClosingState()
            context.state.enter(context)
        elif event == ValveState.OPEN:
            context.state = OpenState()
            context.state.enter(context)
        elif event == ValveState.CLOSED:
            context.state = ClosedState()   
            context.state.enter(context)
class OpenState(State):
    def __init__(self):
        super().__init__("OPEN")
    
    def enter(self, context) -> None:
        print("Valve is now OPEN.")
        append_row_csv(self.ValvePath, {'Time': time.strftime("%Y-%m-%d %H:%M:%S"), 'Name': context.name, 'Status': 'OPEN', 'Notes': ''}, ['Time', 'Name', 'Status', 'Notes'])
        log_state_change(self.SystemPath, context.name, 'OPEN', '')
        

    def exit(self, context) -> None:
        print("Exiting OPEN state...")
    
    def handle_event(self, context, event: ValveState):
        if event == ValveState.CLOSED:
            context.state = ClosedState()
            context.state.enter(context)
        elif event == ValveState.OPENING:
            context.state = OpeningState()
            context.state.enter(context)
        elif event == ValveState.CLOSING:
            context.state = ClosingState()
            context.state.enter(context)
class ClosedState(State):
    def __init__(self):
        super().__init__("CLOSED")
    
    def enter(self, context) -> None:
        print("Valve is now CLOSED.")
        append_row_csv(self.ValvePath, {'Time': time.strftime("%Y-%m-%d %H:%M:%S"), 'Name': context.name, 'Status': 'CLOSED', 'Notes': ''}, ['Time', 'Name', 'Status', 'Notes'])
        log_state_change(self.SystemPath, context.name, 'CLOSED', '')

    def exit(self, context) -> None:
        print("Exiting CLOSED state...")
    
    def handle_event(self, context, event: ValveState):
        if event == ValveState.OPEN:
            context.state = OpenState()
            context.state.enter(context)
        elif event == ValveState.OPENING:
            context.state = OpeningState()
            context.state.enter(context)
        elif event == ValveState.CLOSING:
            context.state = ClosingState()
            context.state.enter(context)

class IdleState(State):
    def __init__(self):
        super().__init__("IDLE")
    
    def enter(self, context) -> None:
        print("Valve is in IDLE state.")
        append_row_csv(self.ValvePath, {'Time': time.strftime("%Y-%m-%d %H:%M:%S"), 'Name': context.name, 'Status': 'IDLE', 'Notes': ''}, ['Time', 'Name', 'Status', 'Notes'])
        log_state_change(self.SystemPath, context.name, 'IDLE', '')
    def exit(self, context) -> None:
        print("Exiting IDLE state...")
    
    def handle_event(self, context, event: ValveState):
        if event == ValveState.CLOSED:
            context.state = ClosedState()
            context.state.enter(context)
        elif event == ValveState.OPEN:
            context.state = OpenState()
            context.state.enter(context)
        elif event == ValveState.OPENING:
            context.state = OpeningState()
            context.state.enter(context)
        elif event == ValveState.CLOSING:
            context.state = ClosingState()
            context.state.enter(context)

class ValveStateMachine:
    def __init__(self, name: str = "Default Valve"):
        self.name = name
        self.SystemPath = LoggingPath.SystemPath()
        self.ValvePath = LoggingPath.ValvePath()
        self.state: State = IdleState() ## Initial state Change depending initial condition
        self.state.enter(self)
        

    
    def on_event(self, event: ValveState):
        self.state.handle_event(self, event)

        
    
    def run(self):
        print(f"Current Valve State: {self.state.name}")
        
        
        # central log only when status changes
        log_state_change(self.SystemPath, self.name, self.state.name, '')
        time.sleep(1)
        
def CreateValveStateMachine(name: str = "Default Valve") -> ValveStateMachine:
    return ValveStateMachine(name)

