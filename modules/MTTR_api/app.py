from flask import Flask, request, jsonify
from modified_MTTR import fetch_mttr_gitapi
from online_tool_MTTR import fetch_mttr_online
from modules.fetch_repo import fetch_repo
import shutil

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
    method = data.get('method') 
    try:
        if method == 'modified':
            clone_result = fetch_repo(repo_url)
            if "error" in clone_result:
                return jsonify({"error": clone_result["error"], "repo_url": repo_url}), 400
            temp_dir = clone_result["temp_dir"]
            result = fetch_mttr_gitapi(repo_url)
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        elif method == 'online':
            result = fetch_mttr_online(repo_url)
        
        else:
            return jsonify({"error": "Invalid method. Use 'online' or 'modified'"}), 400
        
        if result.get("error"):
            return jsonify({"error": result["error"], "repo_url": repo_url}), 400
        
        return jsonify({
            "repo_url": repo_url,
            "result": round(result["mttr"], 2),
            "method": method
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            "method": method,
            "repo_url": repo_url
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)