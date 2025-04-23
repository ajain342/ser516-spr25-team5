import os
from clone_repo import clone_repo
import config
from flask import Flask, request, jsonify
import requests


app = Flask(__name__)

def load_service_config():
    services = config.services_list
    service_mapping = {}
    for service in services:
        service_mapping[os.getenv(f"{service}_PORT")] = os.getenv(f"{service}_NAME")
    return service_mapping

@app.route("/metrics", methods=["POST"])
def get_metrics():
    try:
        # Clone repository
        data = request.get_json()
        repo_url = data["repo_url"]
        head_sha, repo_dir = clone_repo(repo_url)

        # Get metrics data
        services = load_service_config()
        payload = {config.payload_key: repo_url}
        results = {}
        for port, name in services.items():
            metrics = requests.post(f"{config.endpoint_prefix}{name}_api:{port}/{name}", json=payload)
            results[name] = metrics.json()
        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"message": f"Error occured while cloning repositoy: {e}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)