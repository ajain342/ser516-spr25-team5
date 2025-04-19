import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from flask import Flask, request, jsonify
from modules.ici import ici
from modules.utilities.response_wrapper import wrap_with_timestamp
from modules.utilities.fetch_repo import fetch_repo
from modules.utilities.cache import MetricCache

app = Flask(__name__)
cache = MetricCache()

@app.route('/')
def home():
    return jsonify(message="Welcome to the Infrastructure Cost Index API. Use /ici to calculate ICI.")

@app.route('/ici', methods=['POST'])
def get_ici():
    try:
        data = request.get_json()
        repo_url = data.get("repo_url")
        if not repo_url:
            return jsonify({"error": "Missing 'repo_url'"}), 400

        fetch_result = fetch_repo(repo_url)
        if isinstance(fetch_result, dict) and "error" in fetch_result:
            return jsonify({"error": fetch_result["error"]}), 400

        head_sha, repo_dir = fetch_result
        cache_key = f"{repo_url}|{head_sha}"

        if cache.contains(cache_key):
            return jsonify({"cached": True, "results": wrap_with_timestamp(cache.get(cache_key))}), 200
        
        result = ici.compute_ici(repo_dir)
        cache.add(cache_key, result)
        return jsonify(wrap_with_timestamp(result)), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}", "repo_url": repo_url}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009)
