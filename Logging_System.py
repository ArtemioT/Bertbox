# Logging System Module - RoboJar Automation
# Created By Evan Corwin
# Last Modified 1/13/2026

import csv
from pathlib import Path
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod

# Paths


class LoggingPath:
    def __init__(self):
            pass
    def SystemPath():
        LogPath = 'Logs\SystemLog.csv'
        return LogPath
    def ValvePath():
        LogPath = 'Logs\ValveLog.csv'
        return LogPath
    def PumpPath():
        LogPath = 'Logs\PumpLog.csv'
        return LogPath

    
# CSV file    
        
def append_row_csv(path: str, row: dict, fieldnames: list):
    p = Path(path)
    file_has_data = p.exists() and p.stat().st_size > 0

    with p.open('a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_has_data:
            writer.writeheader()
        writer.writerow(row)


def log_state_change(path: str, name: str, status: str, notes: str = '', fieldnames: list | None = None) -> bool:
    """Append a state change to `path` only if the last recorded status for `name` is different.

    Returns True if a new row was appended, False if no change was recorded.
    """
    if fieldnames is None:
        fieldnames = ['Time', 'Name', 'Status', 'Notes']

    p = Path(path)
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    last_status = None
    if p.exists() and p.stat().st_size > 0:
        with p.open('r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            # find last entry for this name
            for row in reversed(rows):
                if row.get('Name') == name:
                    last_status = row.get('Status')
                    break

    if last_status == status:
        return False

    append_row_csv(path, {'Time': time_str, 'Name': name, 'Status': status, 'Notes': notes}, fieldnames)
    return True

# Modes
class ModeState(Enum):
    ERROR = 'Error Log'
    ALL = 'All'
    NONE = 'None'

class Mode(ABC):
    """Abstract base class for all states"""
    
    def __init__(self, name: str):
        self.name = name
    @abstractmethod
    def enter(self, context) -> None:
        """Called when entering this state"""
        pass
    
    @abstractmethod
    def exit(self, context) -> None:
        """Called when exiting this state"""
        pass
    
    @abstractmethod
    def handle_event(self, context, event: ModeState):
        """Handle events in this state"""
        pass


class ErrorLog(Mode):
    def __init__(self):
        super().__init__('ERROR')

    def enter(self, context) -> None:
        print('%s Mode',self.name)

    def handle_event(self, context, event: ModeState):
        if event == ModeState.ALL:
            context.Mode = AllLog()
        elif event == ModeState.NONE:
            context.Mode = NoneLog()

class AllLog(Mode):
    def __init__(self):
        super().__init__('ALL')

    def enter(self, context) -> None:
        print('%s Mode',self.name)

    def handle_event(self, context, event: ModeState):
        if event == ModeState.ERROR:
            context.Mode = ErrorLog()
        elif event == ModeState.NONE:
            context.Mode = NoneLog()

class NoneLog(Mode):
    def __init__(self):
        super().__init__('ALL')

    def enter(self, context) -> None:
        print('%s Mode',self.name)

    def handle_event(self, context, event: ModeState):
        if event == ModeState.ERROR:
            context.Mode = ErrorLog()
        elif event == ModeState.ALL:
            context.Mode = AllLog()

        
class ModeStateMachine:
    def __init__(self):
        ## make it so it will save the last mode used
        self.Mode: Mode = AllLog()
    
    def on_event(self, event: ModeState):
        self.Mode.handle_event(self, event)


class LoggingMode:
    def __init__(self, Mode: str):
        
        pass
#append_row_csv('Log.csv', {'time': '2025-12-29 12:00', 'Status': 'Started'}, ['Time', 'Status'])
