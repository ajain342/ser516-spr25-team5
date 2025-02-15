import requests

url = "http://127.0.0.1:5000/code-churn"
data = {
    "repo_url": "https://github.com/mikaelvesavuori/github-dora-metrics.git",
    "num_commits_before_latest": 5
}

response = requests.post(url, json=data)
print(response.json())
