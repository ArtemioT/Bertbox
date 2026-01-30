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
    output = {"message": "Full test command sent"}
    print(await valve(1, "Open"))
    
    send_command("runTest")
    return output

@app.get("/metrics")
async def metrics():
    # Does nothing here to make sure no errors happen
    return{"message": "CS checking script"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
