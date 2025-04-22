from flask import Flask, request, jsonify
from modules.mttr.modified_MTTR import fetch_mttr_gitapi
# from modules.mttr.online_tool_MTTR import fetch_mttr_online
from modules.utilities.fetch_repo import fetch_repo
from modules.utilities.cache import MetricCache
from modules.utilities.response_wrapper import wrap_with_timestamp

cache = MetricCache()

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify(message="Visit /mttr to calculate mttr")

@app.route('/mttr', methods=['POST'])
def get_mttr():
    data = request.get_json()
    
    if not data or 'repo_url' not in data:
        return jsonify({"error": "Missing repo_url in request"}), 400
    
    repo_url = data['repo_url']
    # method = data.get('method') 
    try:
        # if method == 'modified':
        fetch_result = fetch_repo(repo_url)
        if isinstance(fetch_result, dict) and "error" in fetch_result:
            return jsonify({"error": fetch_result["error"]}), 400

        head_sha, _ = fetch_result
        cache_key = f"{repo_url}|{head_sha}"

        if cache.contains(cache_key):
            result = cache.get(cache_key)
        else:
            result = fetch_mttr_gitapi(repo_url)
            cache.add(cache_key, result)

        # elif method == 'online':
        #     result = fetch_mttr_online(repo_url)
        
        # else:
        #     return jsonify({"error": "Invalid method. Use 'online' or 'modified'"}), 400
        
        if result.get("error"):
            return jsonify({"error": result["error"], "repo_url": repo_url}), 400
        
        return jsonify(wrap_with_timestamp(result)), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            # "method": method,
            "repo_url": repo_url
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)