import os
import shutil
import subprocess
import tempfile
import json
import re
from pathlib import Path

def clone_repo(repo_url, temp_dir):
    """Clones the repository into a temporary directory."""
    try:
        subprocess.run(["git", "clone", "--depth", "1", repo_url, temp_dir], check=True, stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        print("Error: Failed to clone repository.")
        return False

def get_repo_size(temp_dir):
    """Calculates the total size of the repository (excluding .git)."""
    total_size = sum(f.stat().st_size for f in Path(temp_dir).rglob('*') if not f.is_dir())
    return total_size / (1024 * 1024)  # Convert to MB

def count_files_by_extension(temp_dir):
    """Counts files by extension to analyze the tech stack."""
    extensions = {
        "python": [".py"],
        "javascript": [".js", ".jsx", ".ts", ".tsx"],
        "docker": ["Dockerfile"],
        "kubernetes": [".yaml", ".yml"],
        "terraform": [".tf"],
        "cloudformation": [".json", ".yaml"],
    }
    file_counts = {key: 0 for key in extensions}

    for file in Path(temp_dir).rglob("*"):
        if file.is_file():
            for key, ext_list in extensions.items():
                if file.suffix in ext_list or file.name in ext_list:
                    file_counts[key] += 1

    return file_counts

def detect_dependencies(temp_dir):
    """Extracts dependencies from package managers."""
    dependencies = {}
    package_files = {
        "python": ["requirements.txt", "Pipfile"],
        "nodejs": ["package.json"],
    }

    for key, files in package_files.items():
        for file in files:
            file_path = Path(temp_dir) / file
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if key == "python":
                        dependencies[key] = content.count("\n")
                    elif key == "nodejs":
                        try:
                            json_data = json.loads(content)
                            dependencies[key] = len(json_data.get("dependencies", {}))
                        except json.JSONDecodeError:
                            dependencies[key] = 0
    return dependencies

def check_ci_cd_files(temp_dir):
    """Checks for CI/CD pipelines and automation tools."""
    ci_cd_tools = ["github_actions", "jenkins", "circleci"]
    ci_cd_files = {
        "github_actions": ".github/workflows/",
        "jenkins": "Jenkinsfile",
        "circleci": ".circleci/config.yml",
    }
    ci_cd_detected = {tool: False for tool in ci_cd_tools}

    for tool, path in ci_cd_files.items():
        if (Path(temp_dir) / path).exists():
            ci_cd_detected[tool] = True

    return ci_cd_detected

def compute_ici(repo_url):
    """Computes the Infrastructure Cost Index (ICI)."""
    temp_dir = tempfile.mkdtemp()

    if not clone_repo(repo_url, temp_dir):
        return None

    repo_size = get_repo_size(temp_dir)
    file_types = count_files_by_extension(temp_dir)
    dependencies = detect_dependencies(temp_dir)
    ci_cd_usage = check_ci_cd_files(temp_dir)

    # compute ICI Score (random Weighted Sum)
    ici_score = (
        repo_size * 1.5 +
        sum(file_types.values()) * 2 +
        sum(dependencies.values()) * 3 +
        sum(ci_cd_usage.values()) * 5
    )

    # clean up temporary directory
    shutil.rmtree(temp_dir)

    return {
        "repo_url": repo_url,
        "repo_size_mb": repo_size,
        "file_types": file_types,
        "dependencies": dependencies,
        "ci_cd_usage": ci_cd_usage,
        "ici_score": round(ici_score, 2),
    }

# Usage
repo_link = "https://github.com/ajain342/ser516-spr25-team5"
result = compute_ici(repo_link)
print(result)
