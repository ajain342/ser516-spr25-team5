let resultChart; // Variable to hold the chart instance

function calculate() {
    const repoUrl = document.getElementById('githubLink').value;
    const metric = document.getElementById('metric').value;
    const resultDiv = document.getElementById('result');
    const calculateBtn = document.querySelector('.btn-primary');
    const chartCanvas = document.getElementById('resultChart');

    // Clear previous results
    resultDiv.style.display = 'none';
    resultDiv.innerHTML = '';

    // Clear the chart if it exists
    if (resultChart) {
        resultChart.destroy(); // Destroy the existing chart instance
    }
    
    // Basic validation
    if (!repoUrl) {
        alert('Please enter a GitHub repository URL');
        return;
    }

    // Disable button and show loading state
    calculateBtn.innerText = 'Loading...';
    calculateBtn.disabled = true;

    // Prepare payload
    const payload = {
        metric: metric,
        repo_url: repoUrl,
        method: "modified"
    };

    if (metric === 'code-churn') {
        payload.num_commits_before_latest = 10;
    }

    // Send request to backend
    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        resultDiv.style.display = 'block';

        if (data.error) {
            resultDiv.innerHTML = `<div class="result-box error"><strong>Error:</strong> ${data.error}</div>`;
            return;
        }

        let resultContent = `<div class="result-box">`;

        // Ensure data.repo_url exists before using it
        const repoUrl = data.repo_url ? `<a href="${data.repo_url}" target="_blank">${data.repo_url}</a>` : "N/A";

        resultContent += `<strong>Metric:</strong> ${data.metric || "N/A"}<br>`;
        resultContent += `<strong>Repo:</strong> ${repoUrl}<br>`;

        // Prepare data for the chart
        let chartData = {
            labels: [],
            data: []
        };

        if (data.metric === 'mttr') {
            resultContent += `<strong>MTTR Hours:</strong> ${data.result.result || "N/A"}<br>`;
            chartData.labels = ['MTTR'];
            chartData.data = [data.result.result];
        } else if (data.metric === 'code-churn' && typeof data.result === 'object') {
            resultContent += `<strong>Added Lines:</strong> ${data.result.added_lines || "N/A"}<br>`;
            resultContent += `<strong>Deleted Lines:</strong> ${data.result.deleted_lines || "N/A"}<br>`;
            resultContent += `<strong>Modified Lines:</strong> ${data.result.modified_lines || "N/A"}<br>`;
            resultContent += `<strong>Net Change (Churn):</strong> ${data.result["net_change or churn"] || "N/A"}<br>`;
            resultContent += `<strong>Total Commits:</strong> ${data.result.total_commits || "N/A"}<br>`;
            resultContent += `<strong>Commit Range:</strong> ${data.result.commit_range || "N/A"}`;
            chartData.labels = ['Added Lines', 'Deleted Lines', 'Modified Lines'];
            chartData.data = [data.result.added_lines, data.result.deleted_lines, data.result.modified_lines];
        } else if (data.metric === 'loc' && data.result !== undefined) {
            resultContent += `<strong>Lines of Code:</strong> ${data.result.result}`;
            chartData.labels = ['Lines of Code'];
            chartData.data = [data.result.result];
        }

        resultContent += `</div>`;
        resultDiv.innerHTML = resultContent;

        // Display the chart
        chartCanvas.style.display = 'block';
        const chartType = (data.metric === 'mttr' || data.metric === 'loc') ? 'bar' : 'pie'; // Bar for LOC and MTTR, pie for Code Churn

        resultChart = new Chart(chartCanvas, {
            type: chartType,
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Metric Values',
                    data: chartData.data,
                    backgroundColor: chartType === 'bar' ? '#36A2EB' : ['#36A2EB', '#FF6384', '#FFCE56'],
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Metric Visualization'
                    }
                }
            }
        });
    })
    .catch(error => {
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = `<div class="result-box error"><strong>Error:</strong> ${error.message}</div>`;
    })
    .finally(() => {
        // Re-enable button after fetch completes
        calculateBtn.innerText = 'Calculate';
        calculateBtn.disabled = false;
    });
}

function resetFields() {
    document.getElementById('githubLink').value = '';
    document.getElementById('metric').selectedIndex = 0;
    document.getElementById('result').style.display = 'none';
    
    // Hide the chart and destroy it if it exists
    const chartCanvas = document.getElementById('resultChart');
    if (resultChart) {
        resultChart.destroy(); // Destroy the existing chart instance
        resultChart = null; // Reset the chart instance variable
    }
    chartCanvas.style.display = 'none'; // Hide the chart canvas
}
