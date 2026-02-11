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
    sendCommand("/Sensor/On", "Sensor Code Running");

    // Lock ON button, unlock OFF button
    document.getElementById("sensor_on").disabled = true;
    document.getElementById("sensor_off").disabled = false;
}

function pressSensorOff() {
    sendCommand("/Sensor/Off", "Sensor Code Stopping");

    // Lock OFF button, unlock ON button
    document.getElementById("sensor_on").disabled = false;
    document.getElementById("sensor_off").disabled = true;
}

function updateStatusBox() {
    fetch('/status')
        .then(response => response.json())
        .then(data => {
            // Update pump status
            updateStatus('pump', data.pump.state);
            
            // Update sensor status
            updateStatus('sensor', data.sensor.state);
            
            // Update valve statuses
            updateStatus('valve1', data.valves['1'].state);
            updateStatus('valve2', data.valves['2'].state);
            updateStatus('valve3', data.valves['3'].state);

            // Update timestamp
            const now = new Date().toLocaleTimeString();
            document.getElementById('last-updated-time').textContent = now;
        })
        .catch(error => {
            console.error('Error fetching status:', error);
        });
}

function updateStatus(component, state) {
    const element = document.getElementById('status-' + component);
    if (element) {
        element.textContent = state;
        
        // Remove all status classes
        element.className = 'status-value';
        
        // Add appropriate class based on state
        const stateLower = state.toLowerCase();
        element.classList.add('status-' + stateLower);
    }
}

// Update status every 1 second
setInterval(updateStatusBox, 1000);

// Initial update when page loads
updateStatusBox();