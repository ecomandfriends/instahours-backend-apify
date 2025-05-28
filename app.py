from flask import Flask, jsonify
import requests
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

APIFY_TOKEN = 'apify_api_kQrZb7l2RqdTg7aQCBTLc7WQZCt2VB3SqN8n'
ACTOR_TASK_ID = 'drobnikj~instagram-profile-scraper'

@app.route("/analyze/<username>")
def analyze(username):
    try:
        # Lanzar el scraper
        run_url = f"https://api.apify.com/v2/actor-tasks/{ACTOR_TASK_ID}/runs?token={APIFY_TOKEN}"
        input_data = {
            "usernames": [username],
            "resultsLimit": 30,
            "includePosts": True
        }
        run = requests.post(run_url, json=input_data).json()
        run_id = run["data"]["id"]

        # Esperar a que termine
        for _ in range(30):
            time.sleep(2)
            status = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}").json()
            if status["data"]["status"] == "SUCCEEDED":
                break

        # Obtener resultados
        dataset_id = status["data"]["defaultDatasetId"]
        items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?format=json"
        posts = requests.get(items_url).json()[0]["posts"]

        # Extraer horas de publicación
        hours = [int(post["takenAtLocal"].split("T")[1].split(":")[0]) for post in posts if "takenAtLocal" in post]

        result = {f"{h}:00": hours.count(h) for h in range(24)}
        labels = list(result.keys())
        values = list(result.values())

        return jsonify({"labels": labels, "values": values})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
