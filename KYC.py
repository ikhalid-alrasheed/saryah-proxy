from flask import Flask, request, jsonify;simulation_app=Flask(__name__)
from database_builder import reading_from_json
from random import randrange, random

cars = reading_from_json("cars.json")
drivers = reading_from_json("drivers.json")

@simulation_app.route("/person", methods=["POST"])
def person():
    """
    {"person_id": "1xxxxxxxxx",
    "car_id":  xxxxxxxxxx}
    :return:
    """

    R = request.get_json(force=True)
    if random() > 0.90: return jsonify({})
    return {"car": cars[f"{randrange(7)+1}"],
    "owner": drivers[f"{randrange(10)+1}"]}

@simulation_app.route("/hello", methods=["POST"])
def hi():
    return "HI Khalid"


if __name__ == '__main__':
    simulation_app.run(port=4999 , host="127.0.0.1", debug=False)
