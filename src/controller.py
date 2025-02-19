from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

MICROSERVICES = {
    'code-churn': {
        'url': 'http://cc_api:5001/code-churn',
        'method': 'POST',
        'params': ['repo_url', 'method', 'num_commits_before_latest']
    },
    'loc': {
        'url': 'http://loc_api:5002/loc',
        'method': 'POST',
        'params': ['repo_url', 'method']  
    },
    'mttr': {
        'url': 'http://mttr_api:5003/mttr',
        'method': 'POST',
        'params': ['repo_url', 'method']
    }
}

@app.route('/')
def index():
    return render_template('./UI_Dashboard/index.html')  

@app.route('/analyze', methods=['POST'])
def analyze_repo():
    try:
        data = request.get_json()
        if not data or 'metric' not in data or 'repo_url' not in data:
            return jsonify({"error": "Missing required parameters: metric and repo_url"}), 400

        metric = data['metric']
        if metric not in MICROSERVICES:
            return jsonify({"error": f"Invalid metric. Choose from: {', '.join(MICROSERVICES.keys())}"}), 400

        service = MICROSERVICES[metric]
        payload = {param: data.get(param) for param in service['params']}
        payload['repo_url'] = data['repo_url']  
        response = requests.request(
            method=service['method'],
            url=service['url'],
            json=payload,
            timeout=30 
        )

        if response.status_code != 200:
            return jsonify({
                "error": f"Microservice error ({metric})",
                "details": response.json()
            }), response.status_code

        return jsonify({
            "metric": metric,
            "repo_url": data['repo_url'],
            "result": response.json()
        }), 200

    except requests.exceptions.Timeout:
        return jsonify({"error": "Microservice timeout"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Microservice communication failed: {str(e)}"}), 502
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)