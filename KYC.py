from flask import Flask, request, jsonify;simulation_app=Flask(__name__)
from random import randrange, random;import json

def reading_from_json(file):
    with open(f'dummy/{file}', 'r') as openfile:
        json_object = json.load(openfile)
    return json_object

@simulation_app.route("/person", methods=["POST"])
def person():
    """
    {"government_id": "1xxxxxxxxx",
    "car_id":  xxxxxxxxxx}
    :return:
    """
    R = request.get_json(force=True)
    #if random() > 0.90: return jsonify({})
    return {"car": cars[f"{randrange(7)+1}"],
    "driver": drivers[f"{randrange(10)+1}"]}

@simulation_app.route("/hello", methods=["POST"])
def hi():
    return "HI Khalid"


if __name__ == '__main__':
    dummy = reading_from_json("dummy.json")
    cars = dummy["cars"]
    drivers = dummy["drivers"]
    del dummy
    simulation_app.run(port=4999 , host="127.0.0.1", debug=False)
