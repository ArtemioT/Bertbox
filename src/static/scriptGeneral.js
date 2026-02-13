// Global variables for chart and data
let chart;
let csvData = [];
let protocolInfo = {};

// Load CSV from file input
function loadUploadedFile() {
    const fileInput = document.getElementById('csvFileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        document.getElementById('fileStatus').textContent = 'Please select a file';
        return;
    }
    
    document.getElementById('fileStatus').textContent = 'Loading...';
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const csvText = e.target.result;
        Papa.parse(csvText, {
            complete: function(results) {
                processCSVData(results.data);
                document.getElementById('fileStatus').textContent = 'Loaded successfully';
            },
            skipEmptyLines: true
        });
    };
    reader.readAsText(file);
}

// Function to parse CSV and load data from URL
async function loadCSVData(csvPath) {
    try {
        const response = await fetch(csvPath);
        const csvText = await response.text();
        
        Papa.parse(csvText, {
            complete: function(results) {
                processCSVData(results.data);
            },
            skipEmptyLines: true
        });
    } catch (error) {
        console.error('Error loading CSV:', error);
        // Fall back to demo data if CSV cannot be loaded
        loadDemoData();
    }
}

// Process the parsed CSV data
function processCSVData(data) {
    console.log('Processing CSV data, rows:', data.length);
    console.log('First few rows:', data.slice(0, 5));
    
    // Extract protocol information from row 3 (index 2)
    if (data.length > 2) {
        console.log('Row 3 data:', data[1]);
        const protocolRow = data[1][1] || '';
        console.log('Protocol row content:', protocolRow);
        parseProtocolInfo(protocolRow);
    }
    
    // Skip header rows (0-4) and extract measurement data
    csvData = [];
    for (let i = 5; i < data.length; i++) {
        if (data[i].length > 10) {
            csvData.push({
                date: data[i][1],
                time: data[i][2],
                elapsedTime: parseFloat(data[i][3]) || 0,
                flocCount: parseFloat(data[i][4]) || 0,
                meanDiameter: parseFloat(data[i][5]) || 0,
                meanVolume: parseFloat(data[i][6]) || 0,
                volConcentration: parseFloat(data[i][7]) || 0,
                rpm: parseFloat(data[i][8]) || 0,
                gValue: parseFloat(data[i][9]) || 0,
            });
        }
    }
    
    console.log('Processed data points:', csvData.length);
    
    // Update the UI with loaded data
    updateChart();
    updateDoseInfo();
    updateSensorReadings();
    updateTestInfo();
}

// Parse protocol information
function parseProtocolInfo(protocolString) {
    console.log('Parsing protocol string:', protocolString);
    
    // Example: "Protocol Title: Standard Protocol | Run Chemistry: Alum/PolyDADMAC | Run Dosage: 25.5/0.95 ppm | Comments: Demo C Alum Dose Increase"
    const parts = protocolString.split('|');
    console.log('Split into parts:', parts);
    console.log(parts)
    protocolInfo.title = extractValue(parts[0], 'Protocol Title:');
    protocolInfo.chemistry = extractValue(parts[1], 'Run Chemistry:');
    protocolInfo.dosage = extractValue(parts[2], 'Run Dosage:');
    protocolInfo.comments = extractValue(parts[3], 'Comments:');
    
    console.log('Extracted dosage string:', protocolInfo.dosage);
    
    // Parse dosage values (e.g., "25.5/0.95 ppm")
    if (protocolInfo.dosage) {
        const dosageMatch = protocolInfo.dosage.match(/([\d.]+)\/([\d.]+)/);
        console.log('Dosage regex match:', dosageMatch);
        if (dosageMatch) {
            protocolInfo.coagulant = parseFloat(dosageMatch[1]);
            protocolInfo.polymer = parseFloat(dosageMatch[2]);
            console.log('Parsed coagulant:', protocolInfo.coagulant);
            console.log('Parsed polymer:', protocolInfo.polymer);
        }
    }
    
    console.log('Final protocol info:', protocolInfo);
}

// Helper function to extract value from key-value pair
function extractValue(str, key) {
    if (!str) return '';
    const index = str.indexOf(key);
    if (index === -1) return '';
    return str.substring(index + key.length).trim();
}

// Update the chart with CSV data
function updateChart() {
    const ctx = document.getElementById('testChart').getContext('2d');
    
    // Prepare data for the chart - using Volume Concentration as the Y-axis
    const chartData = csvData.map(row => ({
        x: row.elapsedTime,
        y: row.volConcentration
    }));
    
    console.log('Chart data points:', chartData.length);
    
    // Destroy existing chart if it exists
    if (chart) {
        chart.destroy();
    }
    
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Volume Concentration',
                data: chartData,
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Vol. Conc: ' + context.parsed.y.toFixed(4) + ' mm³/L';
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    display: true,
                    title: {
                        display: true,
                        text: 'Time (s)'
                    },
                    grid: {
                        display: true,
                        color: '#e0e0e0'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Vol. Concentration (mm3/L)'
                    },
                    grid: {
                        display: true,
                        color: '#e0e0e0'
                    }
                }
            }
        }
    });
}

// Initialize empty chart
function initializeEmptyChart() {
    const ctx = document.getElementById('testChart').getContext('2d');
    
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Volume Concentration',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    display: true,
                    title: {
                        display: true,
                        text: 'Time (s)'
                    },
                    grid: {
                        display: true,
                        color: '#e0e0e0'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Vol. Concentration (mm3/L)'
                    },
                    grid: {
                        display: true,
                        color: '#e0e0e0'
                    }
                }
            }
        }
    });
}

// Update dose information
function updateDoseInfo() {
    console.log('updateDoseInfo called');
    console.log('Coagulant value:', protocolInfo.coagulant);
    console.log('Polymer value:', protocolInfo.polymer);
    
    if (protocolInfo.coagulant !== undefined) {
        const coagText = `Coagulant: ${protocolInfo.coagulant} mg/L`;
        console.log('Setting coagulant text to:', coagText);
        document.getElementById('coagulantDose').textContent = coagText;
        document.getElementById('coagulantRec').textContent = coagText;
    }
    
    if (protocolInfo.polymer !== undefined) {
        const polyText = `Polymer: ${protocolInfo.polymer} mg/L`;
        console.log('Setting polymer text to:', polyText);
        document.getElementById('polymerDose').textContent = polyText;
        document.getElementById('polymerRec').textContent = polyText;
    }
}

// Update sensor readings with latest data
function updateSensorReadings() {
    if (csvData.length > 0) {
        const latestData = csvData[csvData.length - 1];
        
        // For volume, we'll use a placeholder since it's not directly in the CSV
        document.getElementById('volumeReading').textContent = 
            `Volume: N/A L`;
    }
}

// Update test information
function updateTestInfo() {
    if (csvData.length > 0) {
        const firstData = csvData[0];
        const lastData = csvData[csvData.length - 1];
        
        const testDuration = Math.floor(lastData.elapsedTime / 60);
        const testDate = firstData.date;
        
        document.getElementById('testInfo').textContent = 
            `Test Date: ${testDate} | Duration: ${testDuration} min | Samples: ${csvData.length}`;
    }
}

// Load demo data as fallback
function loadDemoData() {
    // Generate bell curve data for demonstration
    csvData = [];
    const points = 50;
    for (let i = 0; i < points; i++) {
        const x = (i - points/2) / (points/6);
        const y = Math.exp(-0.5 * x * x) * 0.05; // Scale to reasonable values
        csvData.push({
            elapsedTime: i * 10,
            volConcentration: y,
            rpm: 200,
            gValue: 345
        });
    }
    
    protocolInfo = {
        coagulant: 25.5,
        polymer: 0.95
    };
    
    updateChart();
    updateDoseInfo();
    updateSensorReadings();
    document.getElementById('testInfo').textContent = 
        'Demo Data | Duration: 8 min | Samples: 50';
}

// Initialize when the page loads
window.addEventListener('DOMContentLoaded', function() {
    // Initialize with empty chart
    initializeEmptyChart();
    
    // Don't load anything automatically - wait for user to upload CSV
    // Or uncomment the line below if you want to auto-load from a URL
    // loadCSVData('/static/converted.csv');
});