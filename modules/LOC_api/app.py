from flask import Flask, request, jsonify
from urllib.parse import urlparse
from modules.LOC_api.online_Tool import fetch_loc_codetabs
from modules.utilities.fetch_repo import fetch_repo
from modules.utilities.cache import MetricCache
from modules.LOC_api.modified_LOC import run_cloc, compute_modified_loc

loc_cache = MetricCache()
app = Flask(__name__)

def parse_url(repo_url):
    parsed_url = urlparse(repo_url)
    repo_path = parsed_url.path.strip("/")
    if repo_path.endswith(".git"):
        repo_path = repo_path[:-4]
    if repo_path.count('/') != 1:
        return None
    return repo_path

@app.route('/')
def home():
    return jsonify(message="Visit /loc to calculate LOC")

@app.route('/loc', methods=['POST'])
def get_loc():
    data = request.get_json()
    
    if not data or 'repo_url' not in data:
        return jsonify({"error": "Missing repo_url in request"}), 400

    repo_url = data['repo_url']
    method = data.get('method', 'modified')

    repo_path = parse_url(repo_url)
    if not repo_path:
        return jsonify({"error": "Invalid GitHub repository URL"}), 400

    try:
        if method == 'modified':
            fetch_result = fetch_repo(repo_url)
            if isinstance(fetch_result, dict) and "error" in fetch_result:
                return jsonify({"error": fetch_result["error"]}), 400

            head_sha, cloned_path = fetch_result
            cache_key = f"{repo_url}|{head_sha}"

            if loc_cache.contains(cache_key):
                result = loc_cache.get(cache_key)
            else:
                cloc_json = run_cloc(cloned_path)
                result = compute_modified_loc(cloc_json)
                loc_cache.add(cache_key, result)

        elif method == 'online':
            fetch_result = fetch_repo(repo_url)
            if isinstance(fetch_result, dict) and "error" in fetch_result:
                return jsonify({"error": fetch_result["error"]}), 400

            head_sha, _ = fetch_result
            cache_key = f"{repo_url}|{head_sha}|online"

            if loc_cache.contains(cache_key):
                result = loc_cache.get(cache_key)
            else:
                result = fetch_loc_codetabs(repo_path).get("total_lines", 0)
                loc_cache.add(cache_key, result)
        else:
            return jsonify({"error": "Invalid method. Use 'online' or 'modified'"}), 400

        return jsonify({"method": method, "result": result})

    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            "method": method,
            "repo_url": repo_url
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
