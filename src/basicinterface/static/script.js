function sendCommand(endpoint, message) {
    document.getElementById("output").innerText = message;

    fetch(endpoint, {
        method: "POST"
    })
    .then(response => response.text())
    .then(data => {
        console.log("Server response:", data);
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function pressSensorOn() {
    sendCommand("/sensor", "Sensor Code Running");

    // Lock ON button, unlock OFF button
    document.getElementById("sensor_on").disabled = true;
    document.getElementById("sensor_off").disabled = false;
}

function pressSensorOff() {
    sendCommand("/sensoroff", "Sensor Code Stopping");

    // Lock OFF button, unlock ON button
    document.getElementById("sensor_on").disabled = false;
    document.getElementById("sensor_off").disabled = true;
}