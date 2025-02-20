function calculate() {
    const repoUrl = document.getElementById('githubLink').value;
    const metric = document.getElementById('metric').value;
    const resultDiv = document.getElementById('result');
    const calculateBtn = document.querySelector('.btn-primary');

    // Clear previous results
    resultDiv.style.display = 'none';
    resultDiv.innerHTML = '';

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

        if (data.metric === 'mttr') {
            // Display MTTR result as a simple JSON format
            resultContent += `<strong>Result:</strong> ${data.result.result || "N/A"}<br>`;
            //resultContent += `<strong>Result:</strong> ${JSON.stringify(data.result)}`;

        } else if (data.metric === 'code-churn' && typeof data.result === 'object') {
            resultContent += `<strong>Added Lines:</strong> ${data.result.added_lines || "N/A"}<br>`;
            resultContent += `<strong>Deleted Lines:</strong> ${data.result.deleted_lines || "N/A"}<br>`;
            resultContent += `<strong>Modified Lines:</strong> ${data.result.modified_lines || "N/A"}<br>`;
            resultContent += `<strong>Net Change (Churn):</strong> ${data.result["net_change or churn"] || "N/A"}<br>`;
            resultContent += `<strong>Total Commits:</strong> ${data.result.total_commits || "N/A"}<br>`;
            resultContent += `<strong>Commit Range:</strong> ${data.result.commit_range || "N/A"}`;
        } else if (data.metric === 'loc' && data.result !== undefined) {
            resultContent += `<strong>Lines of Code:</strong> ${data.result.result}`;
        } else {
            resultContent += `<strong>Result:</strong> ${JSON.stringify(data.result, null, 2)}`;
        }

        resultContent += `</div>`;
        resultDiv.innerHTML = resultContent;
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
}
