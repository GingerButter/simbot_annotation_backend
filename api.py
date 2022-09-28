from fastapi import FastAPI
from flask import jsonify
from flask import request
from __init__ import client

class FailedRequest(Exception):
    def __init__(self, message, status_code):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

app = FastAPI()

@app.get("/game-session/{id}")
async def getdata(id: int):
    # generate dialog id according to annotator id
    context = {}
    context["sentences"] = []
    col = client["game_session"]["dialogs"]
    dialog = col.find_one({"game_session_id":id})
    game_session_id = dialog["game_session_id"]
    for turn in dialog["turns"]:
        turn_id = turn["turn_id"]
        image = turn["image"]
        for sentence in turn["sentences"]:
            container = dict()
            container["game_session_id"] = game_session_id
            container["turn_id"] = turn_id
            container["image"] = image
            container["sentence_id"] = sentence["sentence_id"]
            container["content"] = sentence["content"]
            container["is_human"] = sentence["is_human"]
            context["sentences"].append(container)
    # return jsonify(**context), 200
    return context

@app.post("/annotation")
async def savedata():
    dialog = dict()

    dialog_id = request.json.get("dialog_id")
    if dialog_id is None or len(dialog_id) == 0:
        raise FailedRequest('Failed to request dialog_id', status_code=400)
    version = request.json.get("version")
    if version is None or len(version) == 0:
        raise FailedRequest('Failed to request version', status_code=400)
    status = request.json.get("status")
    if status is None or len(status) == 0:
        raise FailedRequest('Failed to request status', status_code=400)
    dialog_level_labels = request.json.get("dialog_level_labels")
    if dialog_level_labels is None or len(dialog_level_labels) == 0:
        raise FailedRequest('Failed to request dialog_level_labels', status_code=400)
    annotator_id = request.json.get("annotator_id")
    if annotator_id is None or len(annotator_id) == 0:
        raise FailedRequest('Failed to request annotator_id', status_code=400)
    sentences = request.json.get("sentences")
    if sentences is None or len(sentences) == 0:
        raise FailedRequest('Failed to request sentences', status_code=400)

    dialog["dialog_id"] = dialog_id
    dialog["version"] = version
    dialog["status"] = status
    dialog["dialog_level_labels"] = dialog_level_labels
    dialog["annotator_id"] = annotator_id
    dialog["turns"] = []
    for sentence in sentences:
        token = dict()
        token["sentence_id"] = sentence["sentence_id"]
        token["content"] = sentence["content"]
        token["sentence_level_labels"] = sentence["sentence_level_labels"]
        token["is_human"] = sentence["is_human"]
        if sentence["turn_id"] in dialog["turns"].keys():
            dialog["turn_id"].append(token)
        else:
            dialog["turn_id"] = [token]
    col = client["sample_annotated"]["dialogs"]
    col.insert_one(dialog)
    return 200

@app.get("/annotator-game-session-list/{id}")
async def get_dashboard(id:int):
    col = client["annotator_game_session"]["annotator"]
    context = {}
    annotator_game_session = col.find_one({"annotator_id": id})
    context["assigned_session_id"] = annotator_game_session["assigned_session_id"]
    return context