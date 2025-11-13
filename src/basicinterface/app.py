from flask import Flask, render_template
import socket

app = Flask(__name__)

def send_to_cpp(command):
    HOST = "127.0.0.1"  # since Flask and C++ run on same Pi
    PORT = 6000
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(command.encode())
    except ConnectionRefusedError:
        print("C++ listener not active")
import socket

def send_command(cmd):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 6000))
        s.sendall(cmd.encode())

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/sensor", methods=["POST"])
def sensor():
    send_to_cpp("sensor")
    return "Sensor command sent"

@app.route("/start_pump", methods=["POST"])
def start_pump():
    send_command("START_PUMP")
    return "Pump started"


@app.route("/valve", methods=["POST"])
def valve():
    send_to_cpp("valve")
    return "Valve command sent"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
