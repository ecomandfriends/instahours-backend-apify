
from flask import Flask, jsonify
from flask_cors import CORS
import requests
import time
import os
import json
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

CACHE_DIR = "instahours_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

APIFY_TASK_ID = "wldDVhk5IN3NKpUWR"
APIFY_TOKEN = "apify_api_kQrZb7l2RqdTg7aQCBTLc7WQZCt2VB3SqN8n"

def save_to_cache(username, data):
    cache_file = os.path.join(CACHE_DIR, f"{username}.json")
    with open(cache_file, "w") as f:
        json.dump({
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }, f)

def load_from_cache(username, max_age_minutes=360):
    cache_file = os.path.join(CACHE_DIR, f"{username}.json")
    if not os.path.exists(cache_file):
        return None
    with open(cache_file, "r") as f:
        content = json.load(f)
    timestamp = datetime.fromisoformat(content["timestamp"])
    if datetime.utcnow() - timestamp < timedelta(minutes=max_age_minutes):
        return content["data"]
    return None

@app.route("/analyze/<username>")
def analyze(username):
    cached_data = load_from_cache(username)
    if cached_data:
        return jsonify(cached_data)

    # Lanzar Task de Apify
    run_url = f"https://api.apify.com/v2/actor-tasks/{APIFY_TASK_ID}/runs?token={APIFY_TOKEN}"
    payload = {
        "username": username
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(run_url, json=payload, headers=headers)
    if response.status_code != 201:
        return jsonify({"error": "No se pudo lanzar el actor. Revisa el token o el actor."}), 500

    run_data = response.json().get("data", {})
    dataset_id = run_data.get("defaultDatasetId")
    if not dataset_id:
        return jsonify({"error": "No se obtuvo el datasetId."}), 500

    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}&clean=true"

    for _ in range(60):
        time.sleep(2)
        dataset_response = requests.get(dataset_url)
        if dataset_response.status_code == 200:
            items = dataset_response.json()
            if items:
                hour_counts = [0] * 24
                for post in items:
                    ts = post.get("timestamp")
                    if ts:
                        dt = datetime.fromtimestamp(ts)
                        hour_counts[dt.hour] += 1
                result = {
                    "labels": [f"{h}:00" for h in range(24)],
                    "values": hour_counts
                }
                save_to_cache(username, result)
                return jsonify(result)
    return jsonify({"error": "El scraping ha tardado demasiado. Inténtalo de nuevo más tarde."}), 504

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
