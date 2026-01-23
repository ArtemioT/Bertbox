from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import socket
from pathlib import Path

app = FastAPI()

# Get the current directory
BASE_DIR = Path(__file__).resolve().parent

# Mount static files directory
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

def send_command(cmd):
    print("in send_command")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/generalInterface", response_class=HTMLResponse)
async def general(request: Request):
    return templates.TemplateResponse("general.html", {"request": request})

@app.post("/sensor/{action}")
async def sensor(action: str):
    if action not in ["on", "off"]:
        raise HTTPException(status_code=400, detail="Invalid sensor action")

    return {"message": "Sensor command sent"}

@app.post("/pump/{action}")
async def start_pump(action: str):
    if action not in ["on", "off"]:
        raise HTTPException(status_code=400, detail="Invalid pump action")
    
    return {"message": "Pump started"}

@app.post("/valve/{valve_number}/{action}")
async def valve(valve_number: int, action: str):
    
    if action not in ["Open", "Close"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    if valve_number < 1 or valve_number > 3:
        raise HTTPException(status_code=400, detail="Invalid Valve Number")
    
    command = f"valve{valve_number}{action.capitalize()}"
    send_command(command)
    return {"message": "Valve command sent"}


@app.get("/metrics")
async def metrics():
    return{"message": "CS checking script"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
