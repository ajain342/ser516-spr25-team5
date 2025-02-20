function calculate() {
    const repoUrl = document.getElementById('githubLink').value;
    const metric = document.getElementById('metric').value;
    const resultDiv = document.getElementById('result');
    const calculateBtn = document.querySelector('.btn-primary');

    resultDiv.style.display = 'none';
    resultDiv.innerHTML = '';

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
        })
        .finally(() => {
            // Re-enable button after fetch completes
            calculateBtn.innerText = 'Calculate';
            calculateBtn.disabled = false;
        });
}