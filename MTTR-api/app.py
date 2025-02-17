from flask import Flask, request, jsonify
from urllib.parse import urlparse
from modified_MTTR import fetch_mttr_gitapi
import tempfile

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
    method = data.get('method', 'git-api')  # Default to git-api

    try:
        if method == 'git-api':
            result = fetch_mttr_gitapi(repo_url)
        else:
            return jsonify({"error": "Invalid method. Use 'git-api' or 'online-mttr'"}), 400
        
        return jsonify({"MTTR": result})
    
    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            "method": method,
            "repo_url": repo_url
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)