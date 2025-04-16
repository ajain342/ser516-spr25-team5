from datetime import datetime, timedelta
import requests
from flask import jsonify, make_response

GITHUB_API_URL = "https://api.github.com"


def defect_service(defect_request):
    print("Request: ", defect_request)

    repo_url = defect_request["repo_url"]
    repo_owner = repo_url.split("/")[-2]
    repo_name = repo_url.split("/")[-1]
    request_url = f"{GITHUB_API_URL}/repos/{repo_owner}/{repo_name}/issues"

    headers = {"Accept": "application/vnd.github.v3+json"}

    params = {"per_page": 100, "state": "all", "page": 1}

    defects = []
    url = request_url

    while url:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            try:
                error_response = response.json()

                if "message" in error_response and "API rate limit exceeded" in error_response["message"]:
                    return make_response(jsonify({"error": "rateLimit"}), 429)

                return make_response(jsonify({"error": "Failed to get defects from GitHub", "details": error_response}), 500)
            except Exception:
                return make_response(jsonify({"error": "Failed to get defects from GitHub", "details": response.text}), 500)

        issues = response.json()
        for issue in issues:
            if "pull_request" in issue:
                continue

            defects.append(
                {
                    "title": issue["title"],
                    "author": issue["user"]["login"],
                    "state": issue["state"],
                    "created_at": datetime.strptime(
                        issue["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    "updated_at": datetime.strptime(
                        issue["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    "closed_at": (
                        datetime.strptime(issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
                        if issue["state"] == "closed" and issue.get("closed_at")
                        else None
                    ),
                }
            )

        links = response.headers.get("Link", "")
        next_link = [
            link.split(";")[0][1:-1]
            for link in links.split(", ")
            if 'rel="next"' in link
        ]
        url = next_link[0] if next_link else None

    total_issues = len(defects)
    completed_issues = len(
        [defect for defect in defects if defect["state"] == "closed"]
    )
    open_issues = total_issues - completed_issues
    percent_completed = (
        (completed_issues / total_issues) * 100 if total_issues > 0 else 0
    )

    now = datetime.now()
    last_30_days = now - timedelta(days=30)

    created_last_30_days = [
        defect for defect in defects if defect["created_at"] >= last_30_days
    ]
    closed_last_30_days = [
        defect
        for defect in defects
        if defect["closed_at"] and defect["closed_at"] >= last_30_days
    ]

    discovery_rate_last_30_days = len(created_last_30_days) / 30
    closure_rate_last_30_days = len(closed_last_30_days) / 30

    time_to_close = [
        (defect["closed_at"] - defect["created_at"]).days
        for defect in defects
        if defect["closed_at"]
    ]
    avg_time_to_close = sum(time_to_close) / len(time_to_close) if time_to_close else 0

    summary = {
        "total_issues": total_issues,
        "completed_issues": completed_issues,
        "open_issues": open_issues,
        "percent_completed": round(percent_completed, 2),
        "defect_discovery_rate_last_30_days": round(discovery_rate_last_30_days, 2),
        "defect_closure_rate_last_30_days": round(closure_rate_last_30_days, 2),
        "average_time_to_close": round(avg_time_to_close, 2),
    }

    return make_response(jsonify({"data": summary, "timestamp": datetime.now().isoformat()}), 200)
