import json
from json.decoder import JSONDecodeError


import os
import json

def get_all_conversions(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w") as fd:
            fd.write("[]")
    with open(file_path, "r") as fd:
        return json.load(fd)


def get_conversion(file_path: str, conversion_id: int):
    return get_all_conversions(file_path)[conversion_id]


def add_conversion(file_path: str, data: dict):
    conversions = get_all_conversions(file_path)
    if not conversions:
        conversions = []

    conversions.append(data)

    with open(file_path, "w") as fd:
        json.dump(conversions, fd, indent=4, ensure_ascii=False)
