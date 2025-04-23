from flask import Flask, request, jsonify, render_template
import requests
import os

if os.environ.get('DOCKER_ENV'):
    ui_dir = '/app/UI_Dashboard'
else:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ui_dir = os.path.join(base_dir, 'UI_Dashboard')

app = Flask(__name__,
           template_folder=ui_dir,
           static_folder=ui_dir,
           static_url_path='')

MICROSERVICES = {
    'code-churn': {
        'url': 'http://cc_api:5001/code-churn',
        'method': 'POST',
        'params': ['repo_url', 'num_commits_before_latest']
    },
    'loc': {
        'url': 'http://loc_api:5002/loc',
        'method': 'POST',
        'params': ['repo_url']  
    },
    'mttr': {
        'url': 'http://mttr_api:5003/mttr',
        'method': 'POST',
        'params': ['repo_url']
    },
    'cc': {
        'url': 'http://CYCLO_api:5005/cc',
        'method': 'POST',
        'params': ['repo_url']
    },
    'hm': {
        'url': 'http://HAL_api:5006/hm',
        'method': 'POST',
        'params': ['repo_url']
    },
    'dt': {
        'url': 'http://defects-over-time:5004/dt',
        'method': 'POST',
        'params': ['repo_url']
    }
}

@app.route('/home')
def index():
        try:
            print(f"Attempting to load template from: {app.template_folder}")
            return render_template('index.html')
        except Exception as e:
            print(f"Template loading error: {str(e)}")
            return str(e), 500

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
            # method=service['method'],
            url=service['url'],
            json=payload,
            timeout=30 
        )

        if response.status_code != 200:
            return jsonify(response.json()), response.status_code
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
    print(f"DOCKER_ENV: {os.environ.get('DOCKER_ENV', 'False')}")
    print(f"Template directory: {ui_dir}")
    print(f"Template exists: {os.path.exists(os.path.join(ui_dir, 'index.html'))}") 
    app.run(host='0.0.0.0', port=5000, debug=False)