import json


def save_embeddings(path, message):
    with open(path, "w") as f:
        json.dump({"message": message}, f)
