function calculate() {
    const repoUrl = document.getElementById('githubLink').value;
    const metric = document.getElementById('metric').value;
    const resultDiv = document.getElementById('result');

    // Clear previous results
    resultDiv.style.display = 'none';
    resultDiv.innerHTML = '';

    // Basic validation
    if (!repoUrl) {
        alert('Please enter a GitHub repository URL');
        return;
    }

    // Prepare payload
    const payload = {
        metric: metric,
        repo_url: repoUrl,
        method: "modified"
    };

    // Add metric-specific parameters (e.g., for code-churn)
    if (metric === 'code-churn') {
        payload.num_commits_before_latest = 10; // Default value or add UI input
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
                resultDiv.innerHTML = `<strong>Error:</strong> ${data.error}`;
            } else {
                resultDiv.innerHTML = `
                <strong>Metric:</strong> ${data.metric}<br>
                <strong>Repo:</strong> ${data.repo_url}<br>
                <strong>Result:</strong> ${JSON.stringify(data.result)}
            `;
            }
        })
        .catch(error => {
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `<strong>Error:</strong> ${error.message}`;
        });
}

function resetFields() {
    document.getElementById('githubLink').value = '';
    document.getElementById('metric').selectedIndex = 0;
    document.getElementById('result').style.display = 'none';
}