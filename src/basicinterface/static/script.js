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
