from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/sensor", methods=["POST"])
def sensor():
    print("Sensor Code Restarting... Running")
    
    return "Sensor action complete"

@app.route("/pump", methods=["POST"])
def pump():
    print("Pump Code Restarting... Running")

    return "Pump action complete"

@app.route("/valve", methods=["POST"])
def valve():
    print("Valve Code Restarting... Running")

    return "Valve action complete"

@app.route("/fulltest", methods=["POST"])
def fulltest():
    print("Full Test Restarting... Running")

    return "Full Test action complete"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
