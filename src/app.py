from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import requests
import logging
import time
import pandas as pd

import controls.Controller as SystemController
from controls.Valve_State_Machine import ValveStateMachine, CreateValveStateMachine, ValveState
from controls.Pump_State_Machine import PumpState, PumpStateMachine, CreatePumpStateMachine


system = SystemController.SystemController(num_valves=3)

logging.basicConfig(
    filename='robojar.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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

@app.get("/status")
async def get_status():
    return system.get_system_status()

@app.post("/download")
async def download_report():
    url = "http://192.168.137.201/rj/reportgenrunbase.php"

    run_ids = [30, 24, 22, 20, 17]

    for ids in run_ids:

        payload = {str(ids): "1"}

        response = requests.post(url, data=payload)

        xls_path = f"data/run_{ids}.xls"
        
        with open(xls_path, "wb") as f:
            f.write(response.content)

        print(f"downloaded run {ids}")
        
    
    print(f"converting run {17}")
    xls_path = f"data/run_{17}.xls"
    csv_path = f"data/run_{17}.csv"
    
    df = pd.read_excel(xls_path)
    df.to_csv(csv_path, index=False)


    return {"message": f"downloaded {run_ids}"}

# @app.post("/RobojarTest")
# async def robojarTest():
#     print("im in here")

#     session = requests.Session()
#     base_url = 'http://192.168.137.201/rj'

#     try:
#         print("before protocol data")
#         # Get protocol data
#         response = session.get(f'{base_url}/protocol_mgr.php', params={
#             'func': 'printproto',
#             'format': 'js'
#         })
#         proto_data = response.json()
        
#         print("before find new")
#         # Find "new" protocol
#         new_protocol = next((p for p in proto_data if p['title'].lower() == 'new'), None)
#         if not new_protocol:
#             raise HTTPException(status_code=404, detail="Protocol not found")
        
#         stage_data = new_protocol['stagedata']
#         total_duration = sum(int(stage['duration']) for stage in stage_data)
#         current_time = int(time.time())
        
#         print("before run record")
#         # Create run record
#         session.get(f'{base_url}/run_mgr.php', params={
#             'func': 'newrun',
#             'protocol_id': new_protocol['id'],
#             'title': 'Artemio Test',
#             'dose': '',
#             'chem': '',
#             'comment': '',
#             'start': current_time,
#             'end': current_time + total_duration
#         })
        
#         print("before RPM init")
#         # Set initial RPM
#         first_rpm = stage_data[0]['rpm']
#         session.get(f'{base_url}/setrpm.php', params={'rpm': first_rpm})
        
#         print("before start motor")
#         # Start the motor
#         session.get(f'{base_url}/floc_control.php', params={'command': 'run_floc'})
        
#         print("Motor started, waiting 5 seconds...")
#         # WAIT 5 SECONDS
#         time.sleep(5)
        
#         print("Stopping motor...")
#         # STOP THE TEST
#         session.get(f'{base_url}/floc_control.php', params={'command': 'stop_floc'})
#         session.get(f'{base_url}/setrpm.php', params={'rpm': 0})
#         session.get(f'{base_url}/setgval.php', params={'gval': 0})
        
#         print("Motor stopped")
        
#         return {
#             "status": "success",
#             "message": "Test completed - ran for 5 seconds and stopped",
#             "protocol": new_protocol['title']
#         }  
#     except Exception as e:
#         print(f"ERROR: {e}")
#         # Emergency stop on error
#         try:
#             session.get(f'{base_url}/floc_control.php', params={'command': 'stop_floc'})
#             session.get(f'{base_url}/setrpm.php', params={'rpm': 0})
#         except:
#             pass
#         raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
