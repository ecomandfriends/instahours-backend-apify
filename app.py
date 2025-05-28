from flask import Flask, jsonify
import requests
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

APIFY_TOKEN = 'apify_api_kQrZb7l2RqdTg7aQCBTLc7WQZCt2VB3SqN8n'
TASK_ID = 'ecomandfriends~toni-instagram-scraper'

@app.route("/analyze/<username>")
def analyze(username):
    try:
        run_url = f"https://api.apify.com/v2/actor-tasks/{TASK_ID}/runs?token={APIFY_TOKEN}"
        input_data = {
            "usernames": [username],
            "resultsLimit": 30,
            "includePosts": True
        }

        run = requests.post(run_url, json=input_data, timeout=20).json()
        print("🔍 RESPUESTA DEL RUN:", run)

        if "data" not in run or "id" not in run["data"]:
            return jsonify({"error": "No se pudo lanzar el task. Revisa el task ID o el token.", "raw": run}), 400

        run_id = run["data"]["id"]

        for _ in range(30):
            time.sleep(2)
            status_resp = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}", timeout=10)
            status = status_resp.json()
            if status.get("data", {}).get("status") == "SUCCEEDED":
                break
        else:
            return jsonify({"error": "El scraping ha tardado demasiado. Inténtalo de nuevo más tarde."}), 408

        dataset_id = status["data"].get("defaultDatasetId")
        if not dataset_id:
            return jsonify({"error": "No se pudo obtener el dataset de resultados."}), 500

        items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?format=json"
        items_resp = requests.get(items_url, timeout=15)
        items = items_resp.json()
        posts = items[0].get("posts", [])

        hours = [int(post["takenAtLocal"].split("T")[1].split(":")[0]) for post in posts if "takenAtLocal" in post]
        result = {f"{h}:00": hours.count(h) for h in range(24)}

        return jsonify({"labels": list(result.keys()), "values": list(result.values())})

    except requests.exceptions.RequestException as re:
        print("❌ Error de red:", re)
        return jsonify({"error": "Problema de conexión con Apify", "details": str(re)}), 502
    except Exception as e:
        print("❌ Error inesperado:", e)
        return jsonify({"error": "Fallo interno del servidor", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
