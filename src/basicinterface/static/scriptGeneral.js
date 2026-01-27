// Create the chart
const ctx = document.getElementById('testChart').getContext('2d');

// Generate bell curve data
function generateBellCurve() {
    const data = [];
    const points = 50;
    for (let i = 0; i < points; i++) {
        const x = (i - points/2) / (points/6);
        const y = Math.exp(-0.5 * x * x);
        data.push({x: i, y: y});
    }
    return data;
}

const chart = new Chart(ctx, {
    type: 'line',
    data: {
        datasets: [{
            data: generateBellCurve(),
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
                    text: 'Turbidity (NTU)'
                },
                grid: {
                    display: true,
                    color: '#e0e0e0'
                }
            }
        }
    }
});