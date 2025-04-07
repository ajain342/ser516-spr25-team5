import json
import os
import subprocess
from src.fetch_repo import fetch_repo

def run_cloc(temp_dir):
    output_file = os.path.join(temp_dir, "cloc_output.json")
    try:
        subprocess.run(["cloc", temp_dir, "--json", f"--out={output_file}"], check=True)
    except subprocess.CalledProcessError:
        raise Exception("Failed to run cloc.")
    return output_file

def compute_modified_loc(json_file):
    with open(json_file, "r") as file:
        data = json.load(file)
    
    modified_loc = 0
    for lang, stats in data.items():
        if lang in ["header", "SUM"]:
            continue
        if isinstance(stats, dict):
            code = stats.get("code", 0)
            comments = stats.get("comment", 0)
            modified_loc += code + (comments / 2)
    
    return modified_loc

def main(repo_url):
    fetch_result = fetch_repo(repo_url) 
    repo_path = fetch_result["temp_dir"]  

    cloc_json_file = run_cloc(repo_path)
    modified_loc = compute_modified_loc(cloc_json_file)
    return modified_loc