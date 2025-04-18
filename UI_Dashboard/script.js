let resultChart; // Variable to hold the first chart instance
let resultChart2; // Variable to hold the second chart instance

// NEW: Helper function to map generic API error messages to user-friendly errors.
function mapErrorMessage(err) {
    if (err.includes("Failed to clone repository")) {
        return "Unable to clone repository. Please ensure the repository is public or valid.";
    }
    if (err.includes("exceeds the available commits")) {
        return "The number of commits specified exceeds the available commits in the repository.";
    }
    // Add additional mappings if needed.
    return err;
}

// Function to display error messages in the result container
function showError(errorMsg) {
    const resultDiv = document.getElementById('result');
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = `<div class="result-box error"><strong>Error:</strong> ${errorMsg}</div>`;
    // Hide both chart canvases
    document.getElementById('resultChart').style.display = 'none';
    document.getElementById('resultChart2').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function () {
    const metricDropdown = document.getElementById('metric');
    metricDropdown.addEventListener('change', function () {
        const numCommitsContainer = document.getElementById('numCommitsContainer');
        if (this.value === 'code-churn') {
            numCommitsContainer.style.display = 'block';
        } else {
            numCommitsContainer.style.display = 'none';
        }
    });
});

async function calculate() {
    const repoUrlInput = document.getElementById('githubLink').value.trim();
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


    // Basic validation for empty input
    if (!repoUrlInput) {
        alert('Please enter a GitHub repository URL');
        return;
    }

    // Validate GitHub link format (must start with "https://github.com/" and have at least two segments)
    const githubLinkRegex = /^https:\/\/github\.com\/[^\/]+\/[^\/]+(\/)?$/;
    if (!githubLinkRegex.test(repoUrlInput)) {
        showError("Please enter a valid GitHub repository link (e.g., https://github.com/user/repo).");
        return;
    }

    // For code-churn, validate that the commits input is a valid number
    let numCommitsValue = 0;
    if (metric === 'code-churn') {
        const numCommitsInput = document.getElementById('numCommits').value.trim();
        if (numCommitsInput === "" || isNaN(numCommitsInput)) {
            showError("Please enter a valid number for commits.");
            return;
        }
        numCommitsValue = Number(numCommitsInput);
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
        payload.num_commits_before_latest = numCommitsValue;
        payload_online.num_commits_before_latest = numCommitsValue;
        document.querySelector('.charts-container > *').style.maxWidth = '100%';
    } else {
        document.querySelector('.charts-container > *').style.maxWidth = '50%';
    }


    // Get canvas elements for charts
    const chartCanvas1 = document.getElementById('resultChart');
    const chartCanvas2 = document.getElementById('resultChart2');


    let apiError = null;
    let modifiedData = null;
    let onlineData = null;
    // Variables to store text output for each method
    let modifiedOutputHTML = "";
    let onlineOutputHTML = "";

    // First API call (Modified method)
    await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                apiError = mapErrorMessage(data.error);
                throw new Error(apiError);
            }
            // NEW: Check for too large repo (< 1000 commits) using nested total_commits
            if (metric === 'code-churn' && data.result.total_commits >= 1000) { // MODIFIED
                apiError = "Too large repo, please enter a repo with less than 1000 commits.";
                throw new Error(apiError);
            }
            // NEW: Check if entered commit count exceeds available commits using nested total_commits
            if (metric === 'code-churn' && numCommitsValue >= data.result.total_commits) { // MODIFIED
                apiError = "The number of commits specified exceeds the available commits in the repository.";
                throw new Error(apiError);
            }
            modifiedData = data;
        })
        .catch(error => {
            if (!apiError) {
                apiError = error.message;
            }
            showError(apiError);
        })
        .finally(() => {
            calculateBtn.innerText = 'Calculate';
            calculateBtn.disabled = false;
        });
    if (apiError) return;

    let combinedHTML = '';

    // Build Modified method text output
    modifiedOutputHTML = `<div class="result-box">
        <h3>Modified Output</h3>
        <strong>Metric:</strong> ${modifiedData.metric || "N/A"}<br>
        <strong>Repo:</strong> ${modifiedData.repo_url ? `<a href="${modifiedData.repo_url}" target="_blank">${modifiedData.repo_url}</a>` : "N/A"}<br>`;
    if (modifiedData.metric === 'mttr') {
        modifiedOutputHTML += `<strong>MTTR Hours:</strong> ${modifiedData.result.result || "N/A"}<br>`;
    } else if (modifiedData.metric === 'code-churn' && typeof modifiedData.result === 'object') {
        modifiedOutputHTML += `<strong>Added Lines:</strong> ${modifiedData.result.added_lines || "N/A"}<br>
        <strong>Deleted Lines:</strong> ${modifiedData.result.deleted_lines || "N/A"}<br>
        <strong>Modified Lines:</strong> ${modifiedData.result.modified_lines || "N/A"}<br>
        <strong>Net Change (Churn):</strong> ${modifiedData.result.result || "N/A"}<br>
        <strong>Total Commits:</strong> ${modifiedData.result.total_commits || "N/A"}<br> <!-- MODIFIED -->
        <strong>Commit Range:</strong> ${modifiedData.result.commit_range || "N/A"}`;
    } else if (metric === 'cc') {
        const avgCC = modifiedData.result.results.find(item => item["average cyclomatic complexity"] !== undefined);
        const averageCC = avgCC ? avgCC["average cyclomatic complexity"] : "N/A";

        const totCC = modifiedData.result.results.find(item => item["total cyclomatic complexity"] !== undefined);
        const totalCC = totCC ? totCC["total cyclomatic complexity"] : "N/A";

        const functionEntries = modifiedData.result.results.filter(item =>
            item["Cyclomatic complexity"] !== undefined && item["Function name"]
        );
        let maxCC = { "Cyclomatic complexity": 0, "Function name": "N/A" };

        functionEntries.forEach(func => {
            if (func["Cyclomatic complexity"] > maxCC["Cyclomatic complexity"]) {
                maxCC = func;
            }
        });

        modifiedOutputHTML += `<strong>Cyclomatic Complexity Average:</strong> ${averageCC}<br>`;
        modifiedOutputHTML += `<strong>Max Cyclomatic Complexity  Value:</strong> ${maxCC["Cyclomatic complexity"]}<br>`
        modifiedOutputHTML += `<strong>Function</strong>: ${maxCC["Function name"]}<br>`
        modifiedOutputHTML += `<strong>Total Cyclomatic Complexity</strong>: ${totalCC}<br>`
    } else if (metric === 'hm') {
        const summary = modifiedData.result.file_metrics.find(item => item.Summary !== undefined);
        const sum = summary ? summary.Summary : {};

        const totalDifficulty = sum["Total Difficulty"];
        const totalEffort = sum["Total Efforts"];
        const totalLength = sum["Total Program Length"];
        const totalVocab = sum["Total Program Vocabulary"];
        const totalVolume = sum["Total Program Volume"];

        modifiedOutputHTML += `<strong>Total Difficulty:</strong> ${totalDifficulty}<br>`;
        modifiedOutputHTML += `<strong>Total Efforts:</strong> ${totalEffort}<br>`;
        modifiedOutputHTML += `<strong>Total Program Length:</strong> ${totalLength}<br>`;
        modifiedOutputHTML += `<strong>Total Program Vocabulary:</strong> ${totalVocab}<br>`;
        modifiedOutputHTML += `<strong>Total Program Volume:</strong> ${totalVolume}<br>`;


    } else if (metric === 'dt') {

        const sum = modifiedData.result.summary || {};

        const avg = sum["average_time_to_close"];
        const completed_issues = sum["completed_issues"];
        const defect_closure_30 = sum["defect_closure_rate_last_30_days"];
        const defect_discover_30 = sum["defect_discovery_rate_last_30_days"];
        const open_issue = sum["open_issues"];
        const percent = sum["percent_completed"];
        const total_issue = sum["total_issues"];

        modifiedOutputHTML += `<strong>Average Time To Close:</strong> ${avg}<br>`;
        modifiedOutputHTML += `<strong>Completed Issues:</strong> ${completed_issues}<br>`;
        modifiedOutputHTML += `<strong>Defect Closure Rate In The Last 30 Days:</strong> ${defect_closure_30}<br>`;
        modifiedOutputHTML += `<strong>Defect Closure Discovery Rate In Last 30 Days:</strong> ${defect_discover_30}<br>`;
        modifiedOutputHTML += `<strong>Open Issues:</strong> ${open_issue}<br>`;
        modifiedOutputHTML += `<strong>Percent Completed:</strong> ${percent}<br>`;
        modifiedOutputHTML += `<strong>Total Issues:</strong> ${total_issue}<br>`;
    } else if (modifiedData.metric === 'loc' && modifiedData.result !== undefined) {
        modifiedOutputHTML += `<strong>Lines of Code:</strong> ${modifiedData.result.result}`;
    }
    modifiedOutputHTML += `</div>`;
    combinedHTML += modifiedOutputHTML;

    // Second API call (Online method)
    await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload_online)
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                apiError = mapErrorMessage(data.error);
                throw new Error(apiError);
            }
            onlineData = data;
        })
        .catch(error => {
            if (!apiError) {
                showError(error.message);
            }
        })
        .finally(() => {
            calculateBtn.innerText = 'Calculate';
            calculateBtn.disabled = false;
        });
    if (apiError) return;


    if (onlineData.metric === "mttr" || onlineData.metric === "loc" || onlineData.metric === "code-churn") {
        // Build Online method text output
        onlineOutputHTML = `<div class="result-box">
            <h3>Online Output</h3>
            <strong>Metric:</strong> ${onlineData.metric || "N/A"}<br>
            <strong>Repo:</strong> ${onlineData.repo_url ? `<a href="${onlineData.repo_url}" target="_blank">${onlineData.repo_url}</a>` : "N/A"}<br>`;
        if (onlineData.metric === 'mttr') {
            onlineOutputHTML += `<strong>MTTR Hours:</strong> ${onlineData.result.result || "N/A"}<br>`;
        } else if (onlineData.metric === 'code-churn' && typeof onlineData.result === 'object') {
            onlineOutputHTML += `<strong>Added Lines:</strong> ${onlineData.result.added_lines || "N/A"}<br>
            <strong>Deleted Lines:</strong> ${onlineData.result.deleted_lines || "N/A"}<br>
            <strong>Modified Lines:</strong> ${onlineData.result.modified_lines || "N/A"}<br>
            <strong>Net Change (Churn):</strong> ${onlineData.result.result || "N/A"}<br>
            <strong>Total Commits:</strong> ${onlineData.result.total_commits || "N/A"}<br> <!-- MODIFIED -->
            <strong>Commit Range:</strong> ${onlineData.result.commit_range || "N/A"}`;
        } else if (onlineData.metric === 'loc' && onlineData.result !== undefined) {
            onlineOutputHTML += `<strong>Lines of Code:</strong> ${onlineData.result.result}`;
        }
        onlineOutputHTML += `</div>`;

        combinedHTML += onlineOutputHTML;

    }

    resultDiv.style.display = 'block';


    resultDiv.innerHTML = `<div class="result-container" style="display: flex; gap:20px;">${combinedHTML}</div>`;
    resultDiv.style.display = 'block';





    chartCanvas1.style.display = 'block';

    let chartData = { labels: [], data: [] };
    let chartType = 'bar';

    if (modifiedData.metric === 'mttr') {
        chartData.labels = ['MTTR'];
        chartData.data = [modifiedData.result.result];
    } else if (modifiedData.metric === 'code-churn' && typeof modifiedData.result === 'object') {
        chartData.labels = ['Added Lines', 'Deleted Lines', 'Modified Lines'];
        chartData.data = [modifiedData.result.added_lines, modifiedData.result.deleted_lines, modifiedData.result.modified_lines];
        chartType = 'pie';
    } else if (modifiedData.metric === 'loc') {
        chartData.labels = ['Lines of Code'];
        chartData.data = [modifiedData.result.result];
    } else if (modifiedData.metric === 'cc' && Array.isArray(modifiedData.result.results)) {
        document.getElementById('resultChart2').style.display = 'none';
        chartData.labels = [];
        chartData.data = [];
        modifiedData.result.results.forEach(item => {
            if (item["Function name"] && item["Cyclomatic complexity"] !== undefined) {
                chartData.labels.push(item["Function name"]);
                chartData.data.push(item["Cyclomatic complexity"]);
            }
        });
    } else if (modifiedData.metric === 'hm') {
        document.getElementById('resultChart2').style.display = 'none';
        const summary = modifiedData.result.file_metrics.find(item => item.Summary !== undefined);
        const sum = summary ? summary.Summary : {};
        const totalDifficulty = sum["Total Difficulty"];
        chartData.labels = ['Total Difficulty'];
        chartData.data = [totalDifficulty];
    } else if (modifiedData.metric === 'dt') {
        document.getElementById('resultChart2').style.display = 'none';
        const sum = modifiedData.result.summary || {};
        const percent = sum["percent_completed"];
        chartData.labels = ['Completed', 'Incomplete'];
        chartData.data = [percent, 100 - percent];
        chartType = 'pie';
    }
    chartCanvas1.style.display = 'block';
    resultChart = new Chart(chartCanvas1, {
        type: chartType,
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Metric Values (Modified)',
                data: chartData.data,
                backgroundColor: chartType === 'bar'
                    ? '#36A2EB'
                    : ['#36A2EB', '#FF6384', '#FFCE56'],
            }]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                title: { display: true, text: 'Metric Visualization (Modified)' },
                animation: false
            }
        }
    });


    // Render Online chart

    if (onlineData.metric !== "cc" && onlineData.metric !== "hm" && onlineData.metric !== "dt") {

        chartData = { labels: [], data: [] };
        chartType = 'bar';
        if (onlineData.metric === 'mttr') {
            chartData.labels = ['MTTR'];
            chartData.data = [onlineData.result.result];
        } else if (onlineData.metric === 'code-churn' && typeof onlineData.result === 'object') {
            chartData.labels = ['Added Lines', 'Deleted Lines', 'Modified Lines'];
            chartData.data = [onlineData.result.added_lines, onlineData.result.deleted_lines, onlineData.result.modified_lines];
            chartType = 'pie';
        } else if (onlineData.metric === 'loc') {
            chartData.labels = ['Lines of Code'];
            chartData.data = [onlineData.result.result];
        }
        chartCanvas2.style.display = 'block';
        resultChart2 = new Chart(chartCanvas2, {
            type: chartType,
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Metric Values (Online)',
                    data: chartData.data,
                    backgroundColor: chartType === 'bar'
                        ? '#4CAF50'
                        : ['#4CAF50', '#FF5733', '#FFC300'],
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: 'Metric Visualization (Online)' },
                    animation: false
                }
            }
        });

    }

}

function resetFields() {
    document.getElementById('githubLink').value = '';
    document.getElementById('metric').selectedIndex = 0;
    document.getElementById('result').style.display = 'none';
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
