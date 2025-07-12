from flask import Flask, jsonify
import subprocess
from flask_cors import CORS #import CORS

app = Flask(__name__)

# Enable CORS for all routes.
CORS(app)

# Global variable to track script process
process = None

@app.route("/status", methods=["GET"])
def status():
    return "🟢 Running" if process else "⚪ Idle"

@app.route("/start", methods=["POST"])
def start():
    global process
    if process is None:
        process = subprocess.Popen(["python3", "/home/andhy2/ScoreboardProject/Detection/main.py"])  # Adjust path
        return jsonify({"message":"✅ Script Started"}), 200
    return josnify({"message":"⚠️ Already Running"}), 400

@app.route("/stop", methods=["POST"])
def stop():
    global process
    if process:
        process.terminate()
        process = None
        return jsonify({"message":"⛔ Script Stopped"}), 200
    return jsonify({"message":"⚠️ Not Running"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
