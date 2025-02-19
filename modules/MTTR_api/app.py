from flask import Flask, request, jsonify
from urllib.parse import urlparse
from modified_MTTR import fetch_mttr_gitapi
from online_tool_MTTR import fetch_mttr_online

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
            result = fetch_mttr_gitapi(repo_url)
        elif method == 'online':
            result = fetch_mttr_online(repo_url)
        else:
            return jsonify({"error": "Invalid method. Use 'online' or 'modified'"}), 400
        if result["error"]:
            return jsonify({
                "error": result["error"],
                "repo_url": repo_url
            }), 400 if "No closed" in result["error"] else 500
    
        return jsonify({
            "repo_url": repo_url,
            "mttr_hours": round(result["mttr"], 2),
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