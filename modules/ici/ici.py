import shutil
import json
from pathlib import Path


# 1. Improved repo size calculation with symlink protection and rounding

def get_repo_size(repo_dir):
    # total_size = sum(f.stat().st_size for f in Path(repo_dir).rglob('*') if not f.is_dir())
    # return total_size / (1024 * 1024)
    
    total_size = sum(f.stat().st_size for f in Path(repo_dir).rglob('*') if not f.is_dir() and not f.is_symlink())  # Avoid symlinks
    return round(total_size / (1024 * 1024), 2)  # Round for readability


# 2. Improved file extension matching logic

def count_files_by_extension(repo_dir):
    extensions = {
        "python": [".py"],
        "javascript": [".js", ".jsx", ".ts", ".tsx"],
        "docker": ["Dockerfile"],
        "kubernetes": [".yaml", ".yml"],
        "terraform": [".tf"],
        "cloudformation": [".json", ".yaml"],
    }
    file_counts = {key: 0 for key in extensions}

    for file in Path(repo_dir).rglob("*"):
        if file.is_file():
            suffixes = "".join(file.suffixes)  # handles .test.js, .config.yaml, etc.
            for key, ext_list in extensions.items():
                # if file.suffix in ext_list or file.name in ext_list:
                if any(file.name == ext or suffixes.endswith(ext) for ext in ext_list):  # More accurate check
                    file_counts[key] += 1

    return file_counts


# 3. Avoid overwriting dependencies from multiple files
# 4. Add error handling for file read

def detect_dependencies(repo_dir):
    dependencies = {}
    package_files = {
        "python": ["requirements.txt", "Pipfile"],
        "nodejs": ["package.json"],
    }

    for key, files in package_files.items():
        for file in files:
            file_path = Path(repo_dir) / file
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if key not in dependencies:
                            dependencies[key] = 0
                        if key == "python":
                            dependencies[key] += content.count("\n")
                        elif key == "nodejs":
                            try:
                                json_data = json.loads(content)
                                dependencies[key] += len(json_data.get("dependencies", {}))
                            except json.JSONDecodeError:
                                dependencies[key] += 0
                except (OSError, UnicodeDecodeError):
                    continue
    return dependencies


# 5. Recursive detection of CI/CD files

def check_ci_cd_files(repo_dir):
    ci_cd_tools = ["github_actions", "jenkins", "circleci"]
    ci_cd_files = {
        "github_actions": ".github/workflows/",
        "jenkins": "Jenkinsfile",
        "circleci": ".circleci/config.yml",
    }
    ci_cd_detected = {tool: False for tool in ci_cd_tools}

    for tool, path in ci_cd_files.items():
        # if (Path(repo_dir) / path).exists():
        if any(Path(repo_dir).rglob(path)):  # Support for nested/recursive paths
            ci_cd_detected[tool] = True

    return ci_cd_detected


# 6. Configurable weights

WEIGHTS = {
    "repo_size": 1.5,
    "file_types": 2,
    "dependencies": 3,
    "ci_cd": 5,
}


# 7. Final ICI computation with better modularity and readability

def compute_ici(repo_dir):
    repo_size = get_repo_size(repo_dir)
    file_types = count_files_by_extension(repo_dir)
    dependencies = detect_dependencies(repo_dir)
    ci_cd_usage = check_ci_cd_files(repo_dir)

    # ici_score = (
    #     repo_size * 1.5 +
    #     sum(file_types.values()) * 2 +
    #     sum(dependencies.values()) * 3 +
    #     sum(ci_cd_usage.values()) * 5
    # )

    ici_score = (
        repo_size * WEIGHTS["repo_size"] +
        sum(file_types.values()) * WEIGHTS["file_types"] +
        sum(dependencies.values()) * WEIGHTS["dependencies"] +
        sum(ci_cd_usage.values()) * WEIGHTS["ci_cd"]
    )

    return {
        "repo_size_mb": repo_size,
        "file_types": file_types,
        "dependencies": dependencies,
        "ci_cd_usage": ci_cd_usage,
        "ici_score": round(ici_score, 2),
    }
