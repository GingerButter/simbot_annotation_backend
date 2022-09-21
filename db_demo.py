import datetime  
import os

from dotenv import load_dotenv
from pymongo import MongoClient

from __init__ import client

raw_sample = {
    "dialog_id": 0,
    "turns": [
        {
            "turn_id": 0,
            "timestamp": 0, #should be the corresponding name of the image
            "sentences": [
                {
                    "sentence_id": 0,
                    "content": "This is robot.",
                    "is_human": False,
                },
                {
                    "sentence_id": 1,
                    "content": "This is human.",
                    "is_human": True
                }
            ]
        },
        {
            "turn_id": 1,
            "timestamp": 5,
            "sentences": [
                {
                    "sentence_id": 0,
                    "content": "Welcome",
                    "is_human": False
                }
            ]
        }
    ]
}

annotated_sample = {
    "dialog_id": 0,
    "version": 0,
    "annotator_id": 0,
    "dialog_level_labels": [],
    "turns": [
        {
            "turn_id": 0,
            "sentences": [
                {
                    "sentence_id": 0,
                    "content": "This is robot.",
                    "is_human": False,
                    "sentence_level_labels": []
                },
                {
                    "sentence_id": 1,
                    "content": "This is human.",
                    "is_human": True,
                    "sentence_level_labels": []
                }
            ]
        },
        {
            "turn_id": 1,
            "sentences": [
                {
                    "sentence_id": 0,
                    "content": "Welcome",
                    "is_human": False,
                    "sentence_level_labels": []
                }
            ]
        }
    ]
}

def get_demo():
        # generate dialog id according to annotator id
    id = 0
    context = {}
    context["sentences"] = []
    col = client["sample_raw"]["dialogs"]
    dialog = col.find_one({"dialog_id": id})
    dialog_id = dialog["dialog_id"]
    for turn in dialog["turns"]:
        turn_id = turn["turn_id"]
        timestamp = turn["timestamp"]
        for sentence in turn["sentences"]:
            container = dict()
            container["dialog_id"] = dialog_id
            container["turn_id"] = turn_id
            container["timestamp"] = timestamp
            container["sentence_id"] = sentence["sentence_id"]
            container["content"] = sentence["content"]
            container["is_human"] = sentence["is_human"]
            context["sentences"].append(container)
    print(context)

def save_demo():
    dialog = dict()

    dialog_id = annotated_sample["dialog_id"]
    version = annotated_sample["version"]
    dialog_level_labels = annotated_sample["dialog_level_labels"]
    annotator_id = annotated_sample["annotator_id"]
    sentences = []
    for i in annotated_sample["turns"]:
        tid = i["turn_id"]
        for j in i["sentences"]:
            s = dict()
            s["turn_id"] = tid
            s["sentence_id"] = j["sentence_id"]
            s["content"] = j["content"]
            s["is_human"] = j["is_human"]
            s["sentence_level_labels"] = j["sentence_level_labels"]
            sentences.append(s)

    dialog["dialog_id"] = dialog_id
    dialog["version"] = version
    dialog["dialog_level_labels"] = dialog_level_labels
    dialog["annotator_id"] = annotator_id
    dialog["turns"] = []
    for sentence in sentences:
        token = dict()
        token["sentence_id"] = sentence["sentence_id"]
        token["content"] = sentence["content"]
        token["sentence_level_labels"] = sentence["sentence_level_labels"]
        token["is_human"] = sentence["is_human"]
        if sentence["turn_id"] <= len(dialog["turns"])-1:
            dialog["turns"][sentence["turn_id"]]["sentences"].append(token)
        else:
            dialog["turns"].append(dict())
            dialog["turns"][-1]["turn_id"] = sentence["turn_id"]
            dialog["turns"][-1]["sentences"] = [token]
    col = client["sample_annotated"]["dialogs"]
    col.insert_one(dialog)
    return 200

save_demo()