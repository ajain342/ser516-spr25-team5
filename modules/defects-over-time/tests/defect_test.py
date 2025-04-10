import pytest
import requests_mock
from flask import Flask
from datetime import datetime, timedelta, UTC
from app.services.defect_service import defect_service

app = Flask(__name__)


@pytest.fixture
def client():
    """Fixture to create a Flask test client and set up app context."""
    with app.test_client() as client, app.app_context():
        yield client


@pytest.fixture
def mock_github_response():
    """Simulates a GitHub API response with open and closed issues."""
    now = datetime.now(UTC)
    return [
        {
            "title": "Issue 1",
            "user": {"login": "user1"},
            "state": "open",
            "created_at": (now - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_at": (now - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        {
            "title": "Issue 2",
            "user": {"login": "user2"},
            "state": "closed",
            "created_at": (now - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_at": (now - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "closed_at": (now - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        {
            "title": "Issue 3",
            "user": {"login": "user3"},
            "state": "closed",
            "created_at": (now - timedelta(days=20)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_at": (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "closed_at": (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    ]


def test_defect_service_with_github_data(client, mock_github_response):
    """Test defect service using mock GitHub data."""
    defect_request = {"repo_url": "https://github.com/test-org/test-repo"}

    with requests_mock.Mocker() as m, app.app_context():
        m.get(
            "https://api.github.com/repos/test-org/test-repo/issues",
            json=mock_github_response,
        )

        response = defect_service(defect_request)
        data = response.get_json()

        assert data["summary"]["total_issues"] == 3
        assert data["summary"]["completed_issues"] == 2
        assert data["summary"]["open_issues"] == 1
        assert "defect_discovery_rate_last_30_days" in data["summary"]
        assert "defect_closure_rate_last_30_days" in data["summary"]
        assert "average_time_to_close" in data["summary"]


def test_defect_service_empty_github(client):
    """Test defect service when GitHub API returns an empty list."""
    defect_request = {"repo_url": "https://github.com/test-org/test-repo"}

    with requests_mock.Mocker() as m, app.app_context():
        m.get("https://api.github.com/repos/test-org/test-repo/issues", json=[])

        response = defect_service(defect_request)
        data = response.get_json()

        assert data["summary"]["total_issues"] == 0
        assert data["summary"]["completed_issues"] == 0
        assert data["summary"]["open_issues"] == 0
        assert data["summary"]["defect_discovery_rate_last_30_days"] == 0
        assert data["summary"]["defect_closure_rate_last_30_days"] == 0


def test_defect_service_github_failure(client):
    """Test defect service when GitHub API returns an error."""
    defect_request = {"repo_url": "https://github.com/test-org/test-repo"}

    with requests_mock.Mocker() as m, app.app_context():
        m.get("https://api.github.com/repos/test-org/test-repo/issues", status_code=500)

        response = defect_service(defect_request)
        data = response.get_json()
        status_code = response.status_code

        assert status_code == 500
        assert "error" in data
        assert data["error"] == "Failed to get defects from GitHub"
