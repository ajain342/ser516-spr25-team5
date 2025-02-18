function calculate() {
    let githubLink = document.getElementById('githubLink').value;
    let metric = document.getElementById('metric').value;
    let resultDiv = document.getElementById('result');

    if (githubLink.trim() === "") {
        alert("Please enter a GitHub repository URL.");
        return;
    }

    let metricName = metric === "loc" ? "Line of Code" : metric === "churn" ? "Code Churn" : "MTTR";
    resultDiv.innerHTML = `<strong>Metric:</strong> ${metricName} <br> <strong>Value:</strong> Calculated value here`;
    resultDiv.style.display = "block";
}

function resetFields() {
    document.getElementById('githubLink').value = "";
    document.getElementById('metric').value = "loc";
    document.getElementById('result').style.display = "none";
}
