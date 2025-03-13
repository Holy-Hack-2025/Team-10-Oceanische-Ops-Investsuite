from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder=".", static_url_path="")

# Serve index.html
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# Serve heatmap data
@app.route("/get_heatmap_data")
def get_heatmap_data():
    # Example heatmap data (you can replace this with real data from AI)
    heatmap_data = {
        "max": 10,
        "data": [
            {"x": 100, "y": 150, "value": 8},
            {"x": 200, "y": 250, "value": 6},
            {"x": 300, "y": 350, "value": 9},
            {"x": 100, "y": 400, "value": 9},
            {"x": 400, "y": 350, "value": 9},
        ],
    }
    return jsonify(heatmap_data)

if __name__ == "__main__":
    app.run(debug=True)