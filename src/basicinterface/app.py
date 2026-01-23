from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
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

@app.post("/sensor")
async def sensor():
    send_command("blank")
    return {"message": "Sensor command sent"}

@app.post("/start_pump")
async def start_pump():
    send_command("START_PUMP")
    return {"message": "Pump started"}

@app.post("/valve")
async def valve():
    send_command("blank")
    return {"message": "Valve command sent"}

@app.post("/sensoroff")
async def offsensor():
    send_command("blank")
    return {"message": "Sensor Command Send"}

@app.get("/metrics")
async def metrics():
    return{"message": "CS checking script"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
