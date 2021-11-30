from app import *
from pprint import pprint
import json

def reading_from_json(file):
    with open(f'dummy/{file}', 'r') as openfile:
        json_object = json.load(openfile)
    return json_object

