import tempfile
import subprocess
from urllib.parse import urlparse
import re

def fetch_repo(repo_url):
    if not repo_url:
        return {"error": "No repository URL provided. Please enter a valid GitHub repository URL."}

    parsed = urlparse(repo_url)
    if parsed.netloc.lower() != "github.com" or parsed.path.count("/") < 2:
        return {"error": "Invalid GitHub repository URL. Ensure it follows the format 'https://github.com/owner/repo'."}

    repo_path = parsed.path.strip("/")
    if repo_path.endswith(".git"):
        repo_path = repo_path[:-4]
    if not re.match(r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$", repo_path):
        return {"error": "Malformed repository URL. Ensure the URL points to a valid GitHub repository (e.g., 'https://github.com/owner/repo')."}

    temp_dir = tempfile.mkdtemp()
    try:
        subprocess.run(
            ["git", "clone", repo_url, temp_dir],
            capture_output=True,
            text=True,
            check=True
        )
        return {"temp_dir": temp_dir}
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.lower() if e.stderr else ""
        if "not found" in error_output:
            return {"error": "Repository not found. Please check the URL."}
        elif "authentication" in error_output or "permission denied" in error_output:
            return {"error": "Private repository or insufficient permissions. Please check your access."}
        else:
            return {"error": "Failed to clone repository. Please try again."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}
