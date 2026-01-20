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

def send_to_cpp(command):
    HOST = "127.0.0.1"  # since FastAPI and C++ run on same Pi
    PORT = 6000
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(command.encode())
    except ConnectionRefusedError:
        print("C++ listener not active")

def send_command(cmd):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 6000))
        s.sendall(cmd.encode())

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/general", response_class=HTMLResponse)
async def general(request: Request):
    return templates.TemplateResponse("general.html", {"request": request})

@app.post("/sensor")
async def sensor():
    send_to_cpp("sensor")
    return {"message": "Sensor command sent"}

@app.post("/start_pump")
async def start_pump():
    send_command("START_PUMP")
    return {"message": "Pump started"}

@app.post("/valve")
async def valve():
    send_to_cpp("valve")
    return {"message": "Valve command sent"}

@app.post("/sensoroff")
async def offsensor():
    send_to_cpp("sensor OFF")
    return {"message": "Sensor Command Send"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)