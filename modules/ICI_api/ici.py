import os
import shutil
import json
from pathlib import Path
from modules.utilities.fetch_repo import fetch_repo

def get_repo_size(temp_dir):
    total_size = sum(f.stat().st_size for f in Path(temp_dir).rglob('*') if not f.is_dir())
    return total_size / (1024 * 1024) 

def count_files_by_extension(temp_dir):
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
    repo_data = fetch_repo(repo_url)
    if "error" in repo_data:
        return repo_data

    temp_dir = repo_data["temp_dir"]

    repo_size = get_repo_size(temp_dir)
    file_types = count_files_by_extension(temp_dir)
    dependencies = detect_dependencies(temp_dir)
    ci_cd_usage = check_ci_cd_files(temp_dir)

    ici_score = (
        repo_size * 1.5 +
        sum(file_types.values()) * 2 +
        sum(dependencies.values()) * 3 +
        sum(ci_cd_usage.values()) * 5
    )

    shutil.rmtree(temp_dir)

    return {
        "repo_url": repo_url,
        "repo_size_mb": repo_size,
        "file_types": file_types,
        "dependencies": dependencies,
        "ci_cd_usage": ci_cd_usage,
        "ici_score": round(ici_score, 2),
    }
