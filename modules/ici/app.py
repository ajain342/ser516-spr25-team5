from flask import Flask, request, jsonify
from ici import compute_ici
from modules.utilities.response_wrapper import wrap_with_timestamp

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify(message="Welcome to the Infrastructure Cost Index API. Use /ici to calculate ICI.")

@app.route('/ici', methods=['POST'])
def get_ici():
    data = request.get_json()
    if not data or 'repo_url' not in data:
        return jsonify({"error": "Missing repo_url in request"}), 400

    repo_url = data['repo_url']

    try:
        result = compute_ici(repo_url)
        return jsonify(wrap_with_timestamp(result)), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}", "repo_url": repo_url}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009)
