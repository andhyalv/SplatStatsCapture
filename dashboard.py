from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# List of Raspberry Pis and their IPs
PIS = {
    "Station 1": "192.168.1.158",
    "Station 2": "192.168.1.157",
    "Station 3": "192.168.1.155",
    "Station 4": "192.168.1.153",
    "Station 5": "192.168.1.154"
}

@app.route("/")
def home():
    statuses = {}
    for name, ip in PIS.items():
        try:
            res = requests.get(f"http://{ip}:5000/status", timeout=2)
            statuses[name] = res.text
        except:
            statuses[name] = "❌ Offline"
    return render_template("dashboard.html", statuses=statuses, pis=PIS)

@app.route("/control", methods=["POST"])
def control():
    """Handles start/stop commands for a selected Pi."""
    station = request.form["station"]
    action = request.form["action"]  # "start" or "stop"
    
    if station not in PIS:
        return "Invalid station", 400

    ip = PIS[station]
    try:
        res = requests.post(f"http://{ip}:5000/{action}", timeout=2)  # Use POST
        return res.text
    except:
        return "Failed to connect", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
