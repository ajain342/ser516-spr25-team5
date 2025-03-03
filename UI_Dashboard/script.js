let resultChart;  // For the first chart instance
let resultChart2; // For the second chart instance

async function calculate() {
    const repoUrlInput = document.getElementById('githubLink').value;
    const metric = document.getElementById('metric').value;
    const resultDiv = document.getElementById('result');
    const calculateBtn = document.querySelector('.btn-primary');

    // Clear previous results
    resultDiv.style.display = 'none';
    resultDiv.innerHTML = '';

    // Destroy any existing charts
    if (resultChart) {
        resultChart.destroy();
        resultChart = null;
    }
    if (resultChart2) {
        resultChart2.destroy();
        resultChart2 = null;
    }

    // Basic input check
    if (!repoUrlInput) {
        alert('Please enter a GitHub repository URL');
        return;
    }

    // Validate that the URL looks like a GitHub repository link.
    const githubUrlPattern = /^https?:\/\/(www\.)?github\.com\/[^/]+\/[^/]+/i;
    if (!githubUrlPattern.test(repoUrlInput)) {
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = `
            <div class="result-box error">
                <strong>Error:</strong> Please provide a valid public GitHub repository URL.
                <br>Example: https://github.com/username/reponame
            </div>`;
        return;
    }

    calculateBtn.innerText = 'Loading...';
    calculateBtn.disabled = true;

    // Prepare payloads for both API calls (modified & online)
    const payload = {
        metric: metric,
        repo_url: repoUrlInput,
        method: "modified"
    };
    const payloadOnline = {
        metric: metric,
        repo_url: repoUrlInput,
        method: "online"
    };

    // If code-churn is selected, set additional parameter and adjust layout.
    if (metric === 'code-churn') {
        payload.num_commits_before_latest = 10;
        document.querySelector('.charts-container > *').style.maxWidth = '100%';
    } else {
        document.querySelector('.charts-container > *').style.maxWidth = '50%';
    }

    const chartCanvas1 = document.getElementById('resultChart');
    const chartCanvas2 = document.getElementById('resultChart2');

    // --- 1) "modified" API call ---
    await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(async response => {
        if (!response.ok) {
            const errorBody = await response.json();
            throw new Error(errorBody.error || response.statusText);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            resultDiv.style.display = 'block';
            resultDiv.innerHTML += `<div class="result-box error">
                <strong>Error (modified):</strong> ${data.error}
            </div>`;
        } else {
            // Append successful result content
            resultDiv.style.display = 'block';
            let resultContent = `<div class="result-box">`;
            const repoUrl = data.repo_url 
                ? `<a href="${data.repo_url}" target="_blank">${data.repo_url}</a>` 
                : "N/A";
            resultContent += `<strong>Metric:</strong> ${data.metric || "N/A"}<br>`;
            resultContent += `<strong>Repo:</strong> ${repoUrl}<br>`;

            let chartData = { labels: [], data: [] };
            let chartType = 'bar';
            let serviceResult = data.result;
            if (data.metric === 'mttr') {
                resultContent += `<strong>MTTR Hours:</strong> ${serviceResult.result || "N/A"}<br>`;
                chartData.labels = ['MTTR'];
                chartData.data = [serviceResult.result];
            } else if (data.metric === 'code-churn' && typeof serviceResult === 'object') {
                resultContent += `<strong>Added Lines:</strong> ${serviceResult.added_lines || "N/A"}<br>`;
                resultContent += `<strong>Deleted Lines:</strong> ${serviceResult.deleted_lines || "N/A"}<br>`;
                resultContent += `<strong>Modified Lines:</strong> ${serviceResult.modified_lines || "N/A"}<br>`;
                resultContent += `<strong>Net Change (Churn):</strong> ${serviceResult.result || "N/A"}<br>`;
                resultContent += `<strong>Total Commits:</strong> ${serviceResult.total_commits || "N/A"}<br>`;
                resultContent += `<strong>Commit Range:</strong> ${serviceResult.commit_range || "N/A"}`;
                chartData.labels = ['Added Lines', 'Deleted Lines', 'Modified Lines'];
                chartData.data = [serviceResult.added_lines, serviceResult.deleted_lines, serviceResult.modified_lines];
                chartType = 'pie';
            } else if (data.metric === 'loc' && serviceResult !== undefined) {
                resultContent += `<strong>Lines of Code:</strong> ${serviceResult.result}`;
                chartData.labels = ['Lines of Code'];
                chartData.data = [serviceResult.result];
            }
            resultContent += `</div>`;
            resultDiv.innerHTML += resultContent;

            chartCanvas1.style.display = 'block';
            resultChart = new Chart(chartCanvas1, {
                type: chartType,
                data: {
                    labels: chartData.labels,
                    datasets: [{
                        label: 'Metric Values (Modified)',
                        data: chartData.data
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' },
                        title: { display: true, text: 'Metric Visualization (Modified)' },
                        animation: false
                    }
                }
            });
        }
    })
    .catch(error => {
        resultDiv.style.display = 'block';
        resultDiv.innerHTML += `<div class="result-box error">
            <strong>Error (modified):</strong> ${error.message}
        </div>`;
    })
    .finally(() => {
        calculateBtn.innerText = 'Calculate';
        calculateBtn.disabled = false;
    });

    // --- 2) "online" API call ---
    await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payloadOnline)
    })
    .then(async response => {
        if (!response.ok) {
            const errorBody = await response.json();
            throw new Error(errorBody.error || response.statusText);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            resultDiv.style.display = 'block';
            resultDiv.innerHTML += `<div class="result-box error">
                <strong>Error (online):</strong> ${data.error}
            </div>`;
        } else {
            resultDiv.style.display = 'block';
            let resultContent = `<div class="result-box">`;
            const repoUrl = data.repo_url
                ? `<a href="${data.repo_url}" target="_blank">${data.repo_url}</a>`
                : "N/A";
            resultContent += `<strong>Metric:</strong> ${data.metric || "N/A"}<br>`;
            resultContent += `<strong>Repo:</strong> ${repoUrl}<br>`;
            
            let chartData = { labels: [], data: [] };
            let chartType = 'bar';
            let serviceResult = data.result;
            if (data.metric === 'mttr') {
                resultContent += `<strong>MTTR Hours:</strong> ${serviceResult.result || "N/A"}<br>`;
                chartData.labels = ['MTTR'];
                chartData.data = [serviceResult.result];
            } else if (data.metric === 'code-churn' && typeof serviceResult === 'object') {
                resultContent += `<strong>Added Lines:</strong> ${serviceResult.added_lines || "N/A"}<br>`;
                resultContent += `<strong>Deleted Lines:</strong> ${serviceResult.deleted_lines || "N/A"}<br>`;
                resultContent += `<strong>Modified Lines:</strong> ${serviceResult.modified_lines || "N/A"}<br>`;
                resultContent += `<strong>Net Change (Churn):</strong> ${serviceResult["net_change or churn"] || "N/A"}<br>`;
                resultContent += `<strong>Total Commits:</strong> ${serviceResult.total_commits || "N/A"}<br>`;
                resultContent += `<strong>Commit Range:</strong> ${serviceResult.commit_range || "N/A"}`;
                chartData.labels = ['Added Lines', 'Deleted Lines', 'Modified Lines'];
                chartData.data = [
                    serviceResult.added_lines,
                    serviceResult.deleted_lines,
                    serviceResult.modified_lines
                ];
                chartType = 'pie';
            } else if (data.metric === 'loc' && serviceResult !== undefined) {
                resultContent += `<strong>Lines of Code:</strong> ${serviceResult.result}`;
                chartData.labels = ['Lines of Code'];
                chartData.data = [serviceResult.result];
            }
            resultContent += `</div>`;
            resultDiv.innerHTML += resultContent;

            chartCanvas2.style.display = 'block';
            resultChart2 = new Chart(chartCanvas2, {
                type: chartType,
                data: {
                    labels: chartData.labels,
                    datasets: [{
                        label: 'Metric Values (Online)',
                        data: chartData.data
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' },
                        title: { display: true, text: 'Metric Visualization (Online)' },
                        animation: false
                    }
                }
            });
        }
    })
    .catch(error => {
        resultDiv.style.display = 'block';
        resultDiv.innerHTML += `<div class="result-box error">
            <strong>Error (online):</strong> ${error.message}
        </div>`;
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

    if (resultChart) {
        resultChart.destroy();
        resultChart = null;
    }
    if (resultChart2) {
        resultChart2.destroy();
        resultChart2 = null;
    }
    document.getElementById('resultChart').style.display = 'none';
    document.getElementById('resultChart2').style.display = 'none';
}
