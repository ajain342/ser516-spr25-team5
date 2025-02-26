let resultChart; // Variable to hold the first chart instance
let resultChart2; // Variable to hold the second chart instance

function calculate() {
    const repoUrlInput = document.getElementById('githubLink').value;
    const metric = document.getElementById('metric').value;
    const resultDiv = document.getElementById('result');
    const calculateBtn = document.querySelector('.btn-primary');

    // Clear previous results and charts
    resultDiv.style.display = 'none';
    resultDiv.innerHTML = '';

    if (resultChart) {
        resultChart.destroy();
        resultChart = null;
    }
    if (resultChart2) {
        resultChart2.destroy();
        resultChart2 = null;
    }

    // Basic validation
    if (!repoUrlInput) {
        alert('Please enter a GitHub repository URL');
        return;
    }

    // Disable button and show loading state
    calculateBtn.innerText = 'Loading...';
    calculateBtn.disabled = true;

    // Prepare payloads for both API calls
    const payload = {
        metric: metric,
        repo_url: repoUrlInput,
        method: "modified"
    };

    const payload_online = {
        metric: metric,
        repo_url: repoUrlInput,
        method: "online"
    };

    if (metric === 'code-churn') {
        payload.num_commits_before_latest = 10;
    }

    // Get canvas elements for each chart
    const chartCanvas1 = document.getElementById('resultChart');
    const chartCanvas2 = document.getElementById('resultChart2');

    // First API call (modified method)
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
            const repoUrl = data.repo_url ? `<a href="${data.repo_url}" target="_blank">${data.repo_url}</a>` : "N/A";
            resultContent += `<strong>Metric:</strong> ${data.metric || "N/A"}<br>`;
            resultContent += `<strong>Repo:</strong> ${repoUrl}<br>`;

            // Prepare chart data
            let chartData = {
                labels: [],
                data: []
            };

            let chartType = 'bar'; // default

            if (data.metric === 'mttr') {
                resultContent += `<strong>MTTR Hours:</strong> ${data.result.result || "N/A"}<br>`;
                chartData.labels = ['MTTR'];
                chartData.data = [data.result.result];
            } else if (data.metric === 'code-churn' && typeof data.result === 'object') {
                resultContent += `<strong>Added Lines:</strong> ${data.result.added_lines || "N/A"}<br>`;
                resultContent += `<strong>Deleted Lines:</strong> ${data.result.deleted_lines || "N/A"}<br>`;
                resultContent += `<strong>Modified Lines:</strong> ${data.result.modified_lines || "N/A"}<br>`;
                resultContent += `<strong>Net Change (Churn):</strong> ${data.result.result || "N/A"}<br>`;
                resultContent += `<strong>Total Commits:</strong> ${data.result.total_commits || "N/A"}<br>`;
                resultContent += `<strong>Commit Range:</strong> ${data.result.commit_range || "N/A"}`;
                chartData.labels = ['Added Lines', 'Deleted Lines', 'Modified Lines'];
                chartData.data = [data.result.added_lines, data.result.deleted_lines, data.result.modified_lines];
                chartType = 'pie';
            } else if (data.metric === 'loc' && data.result !== undefined) {
                resultContent += `<strong>Lines of Code:</strong> ${data.result.result}`;
                chartData.labels = ['Lines of Code'];
                chartData.data = [data.result.result];
            }

            resultContent += `</div>`;
            resultDiv.innerHTML = resultContent;

            // Display the first chart using chartCanvas1
            chartCanvas1.style.display = 'block';
            resultChart = new Chart(chartCanvas1, {
                type: chartType,
                data: {
                    labels: chartData.labels,
                    datasets: [{
                        label: 'Metric Values (Modified)',
                        data: chartData.data,
                        backgroundColor: chartType === 'bar' ? '#36A2EB' : ['#36A2EB', '#FF6384', '#FFCE56'],
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' },
                        title: { display: true, text: 'Metric Visualization (Modified)' }
                    }
                }
            });
        })
        .catch(error => {
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `<div class="result-box error"><strong>Error:</strong> ${error.message}</div>`;
        })
        .finally(() => {
            calculateBtn.innerText = 'Calculate';
            calculateBtn.disabled = false;
        });

    // Second API call (online method)
    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload_online)
    })
        .then(response => response.json())
        .then(data => {
            // Reuse the resultDiv if necessary, or adjust as needed
            resultDiv.style.display = 'block';
            if (data.error) {
                resultDiv.innerHTML = `<div class="result-box error"><strong>Error:</strong> ${data.error}</div>`;
                return;
            }

            let resultContent = `<div class="result-box">`;
            const repoUrl = data.repo_url ? `<a href="${data.repo_url}" target="_blank">${data.repo_url}</a>` : "N/A";
            resultContent += `<strong>Metric:</strong> ${data.metric || "N/A"}<br>`;
            resultContent += `<strong>Repo:</strong> ${repoUrl}<br>`;

            // Prepare chart data
            let chartData = {
                labels: [],
                data: []
            };

            let chartType = 'bar'; // default

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
                chartType = 'pie';
            } else if (data.metric === 'loc' && data.result !== undefined) {
                resultContent += `<strong>Lines of Code:</strong> ${data.result.result}`;
                chartData.labels = ['Lines of Code'];
                chartData.data = [data.result.result];
            }

            resultContent += `</div>`;
            resultDiv.innerHTML = resultContent;

            // Display the second chart using chartCanvas2
            chartCanvas2.style.display = 'block';
            resultChart2 = new Chart(chartCanvas2, {
                type: chartType,
                data: {
                    labels: chartData.labels,
                    datasets: [{
                        label: 'Metric Values (Online)',
                        data: chartData.data,
                        backgroundColor: chartType === 'bar' ? '#4CAF50' : ['#4CAF50', '#FF5733', '#FFC300'],
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' },
                        title: { display: true, text: 'Metric Visualization (Online)' }
                    }
                }
            });
        })
        .catch(error => {
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `<div class="result-box error"><strong>Error:</strong> ${error.message}</div>`;
        })
        .finally(() => {
            calculateBtn.innerText = 'Calculate';
            calculateBtn.disabled = false;
        });
}

function resetFields() {
    document.getElementById('githubLink').value = '';
    document.getElementById('metric').selectedIndex = 0;
    document.getElementById('result').style.display = 'none';

    // Hide the charts and destroy them if they exist
    const chartCanvas1 = document.getElementById('resultChart');
    const chartCanvas2 = document.getElementById('resultChart2');
    if (resultChart) {
        resultChart.destroy();
        resultChart = null;
    }
    if (resultChart2) {
        resultChart2.destroy();
        resultChart2 = null;
    }
    chartCanvas1.style.display = 'none';
    chartCanvas2.style.display = 'none';
}