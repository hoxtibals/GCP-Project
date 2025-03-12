from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/realtime")
def get_realtime_data():
    sample_data = {
        "time": "2025-03-12 14:30:45",
        "cpu": "5.2%",
        "memory": "1024/4096 MB (25.00%)",
        "io": "1.2",
        "filesystem": "65%",
        "power": "75%"
    }
    return jsonify(sample_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
