from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

import controls.Controller as SystemController
from controls.Valve_State_Machine import ValveStateMachine, CreateValveStateMachine, ValveState
from controls.Pump_State_Machine import PumpState, PumpStateMachine, CreatePumpStateMachine


system = SystemController.SystemController(num_valves=3)

app = FastAPI()

# Get the current directory
BASE_DIR = Path(__file__).resolve().parent

# Mount static files directory
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

def send_command(cmd):
    print("in send_command")
    print(cmd)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "window": "Test Window"})

@app.get("/generalInterface", response_class=HTMLResponse)
async def general(request: Request):
    return templates.TemplateResponse("general.html", {"request": request, "window": "Interface Window"})

@app.post("/{control}/{action}")
async def control(action: str, control: str):
    if control not in ["Pump", "Sensor"]:
        raise HTTPException(status_code=400, detail="Invalid control object")
    
    if action not in ["On", "Off"]:
        raise HTTPException(status_code=400, detail="Invalid sensor action")
    
    if control == "Pump":
        if action == "On":
            system.get_pump().on_event(PumpState.RUNNING)
            message = "Pump turned on (RUNNING)"
        else:
            system.get_pump().on_event(PumpState.IDLE)
            message = "Pump turned off (IDLE)"
        command = f"pump{action}"
        send_command(command)
        return {"message": message, "state": system.get_pump().state.name}
    elif control == "Sensor":
        system.sensor_active = (action == "On")

        command = f"sensor{action}"
        send_command(command)

        return {"message": f"Sensor turned {action.lower()}", "state": "ON" if system.sensor_active else "OFF"}


@app.post("/valve/{valve_number}/{action}")
async def valve(valve_number: int, action: str):
    
    if action not in ["Open", "Close"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    if valve_number < 1 or valve_number > 3:
        raise HTTPException(status_code=400, detail="Invalid Valve Number")
    
    valve_sm = system.get_valve(valve_number)

    if not valve_sm:
        raise HTTPException(status_code= 404, detail =f"Valve {valve_number} not found")

    if action == "Open":
        valve_sm.on_event(ValveState.OPENING)
        valve_sm.on_event(ValveState.OPEN)
        message = f"Valve {valve_number} opened"
    else:
        valve_sm.on_event(ValveState.CLOSING)
        valve_sm.on_event(ValveState.CLOSED)
        message = f"Valve {valve_number} closed"
    
    command = f"valve{valve_number}{action.capitalize()}"
    send_command(command)
    
    return {"message": message, "state": valve_sm.state.name, "valve_number": valve_number}

@app.post("/runTest")
async def fullTest():
    #this function should first reset all controls then run all controls.
    reset_result = system.reset_all()
    test_results ={"reset": reset_result, "test_sequence": []}
    
    for valve_num in range(1,4):
        valve_sm = system.get_valve(valve_num)
        valve_sm.on_event(ValveState.OPENING)
        test_results["test_sequence"].append({"action": f"Valve {valve_num} OPENING", "state": valve_sm.state.name})

        send_command(f"valve{valve_num}Opening")

        valve_sm.on_event(ValveState.OPEN)
        test_results["test_sequence"].append({"action": f"Valve {valve_num} OPEN", "state": valve_sm.state.name})
        send_command(f"valve{valve_num}Open")

    system.get_pump().on_event(PumpState.PRIMING)
    test_results["test_sequence"].append({"action": "Pump PRIMING", "state": system.get_pump().state.name})
    send_command("pumpPriming")

    system.get_pump().on_event(PumpState.RUNNING)
    test_results["test_sequence"].append({"action": "Pump RUNNING", "state": system.get_pump().state.name})
    send_command("pumpRunning")
    
    system.sensor_active = True
    test_results["test_sequence"].append({"action": "Sensor ON", "state": "ON"})
    send_command("sensorOn")

    for valve_num in range(1,4):
        valve_sm = system.get_valve(valve_num)
        valve_sm.on_event(ValveState.CLOSING)
        test_results["test_sequence"].append({"action": f"Valve {valve_num} CLOSING", "state": valve_sm.state.name})
        send_command(f"valve{valve_num}Closing")

        valve_sm.on_event(ValveState.CLOSED)
        test_results["test_sequence"].append({"action": f"Valve {valve_num} CLOSED", "state": valve_sm.state.name})
        send_command(f"valve{valve_num}Closed")
    
    system.get_pump().on_event(PumpState.IDLE)
    test_results["test_sequence"].append({"action": "Pump IDLE", "state": system.get_pump().state.name})
    send_command("pumpIdle")

    system.sensor_active = False
    test_results["test_sequence"].append({"action": "Sensor OFF", "state": "OFF"})
    send_command("sensorOff")

    return {"message": "Full test sequence completed", "results": test_results}

@app.get("/metrics")
async def metrics():
    # Does nothing here to make sure no errors happen
    return{"message": "CS checking script"}

@app.post("/reset")
async def reset_system():
    result = system.reset_all()
    send_command("resetAll")
    return {"message": "System reset completed", "results": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
