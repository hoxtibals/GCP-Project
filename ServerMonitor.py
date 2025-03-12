from flask import Flask, jsonify
import psutil
import time
import json
import os

app = Flask(__name__)

data_log = "server_data.log"
pipe_path = "/tmp/server_pipe"

# Ensure named pipe exists
if not os.path.exists(pipe_path):
    os.mkfifo(pipe_path)

# Function to get system metrics
def get_system_metrics():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "network": psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
    }

# Background process to write data to the named pipe
def write_to_pipe():
    while True:
        with open(pipe_path, "w") as pipe:
            data = get_system_metrics()
            pipe.write(json.dumps(data) + "\n")
        time.sleep(10)

# API Endpoint for real-time data
@app.route("/realtime")
def get_realtime_data():
    return jsonify(get_system_metrics())

# API Endpoint for historical data
@app.route("/history")
def get_history():
    try:
        with open(data_log, "r") as f:
            return jsonify([json.loads(line) for line in f.readlines()])
    except FileNotFoundError:
        return jsonify([])

if __name__ == "__main__":
    import threading
    threading.Thread(target=write_to_pipe, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
