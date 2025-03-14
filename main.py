import os
from flask import Flask, jsonify, send_from_directory, request
import sys

from app import *

app = Flask(__name__, static_folder=".", static_url_path="")

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/get_heatmap_data")
def get_heatmap_data():
    heatmap_data = {
        "max": 10,
"data": [
    {"x": 451, "y": 794, "value": 0, "name": "Mercedes"},
    {"x": 425, "y": 298, "value": 0, "name": "Chevrolet"},
    {"x": 1104, "y": 181, "value": 2, "name": "Volvo"},
    {"x": 1338, "y": 788, "value": 3, "name": "Volkswagen"},
    {"x": 963, "y": 810, "value": 4, "name": "Ford"},
    {"x": 1348, "y": 491, "value": 4, "name": "Ferrari"},
    {"x": 539, "y": 646, "value": 6, "name": "Audi"},
    {"x": 869, "y": 259, "value": 7, "name": "Jaguar"},
    {"x": 1379, "y": 162, "value": 8, "name": "Land Rover"},
    {"x": 880, "y": 661, "value": 9, "name": "Kia"},
    {"x": 582, "y": 704, "value": 0, "name": "Nissan"},
    {"x": 824, "y": 338, "value": 2, "name": "Tesla"},
    {"x": 628, "y": 436, "value": 3, "name": "Toyota"},
    {"x": 1188, "y": 642, "value": 3, "name": "Porsche"},
    {"x": 250, "y": 809, "value": 4, "name": "Mazda"},
    {"x": 1482, "y": 282, "value": 6, "name": "Honda"},
    {"x": 982, "y": 185, "value": 6, "name": "Subaru"},
    {"x": 844, "y": 592, "value": 8, "name": "BMW"},
    {"x": 999, "y": 480, "value": 9, "name": "Hyundai"},
    {"x": 1750, "y": 391, "value": 9, "name": "Lamborghini"}
]    }

    data = getDataHeatmap('Volkswagen, Pirelli, Mercedes')
    print(data)

    return jsonify(heatmap_data)

if __name__ == "__main__":
    app.run(debug=True)