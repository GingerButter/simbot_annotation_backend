from crypt import methods
from tkinter import dialog
import flask
from flask import Flask,render_template,Response
import threading
from __init__ import app
from __init__ import client


class FailedRequest(Exception):
    def __init__(self, message, status_code):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code


@app.route("/getdata", methods=["GET"])
def getdata(id):
    # generate dialog id according to annotator id
    id = 0
    context = {}
    context["sentences"] = []
    col = client["sample_raw"]["dialogs"]
    dialog = col.find_one({"dialog_id":id})
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
    return flask.jsonify(**context), 200

@app.route("/savedata", methods=["POST"])
def savedata():
    dialog = dict()

    dialog_id = flask.request.json.get("dialog_id")
    if dialog_id is None or len(dialog_id) == 0:
        raise FailedRequest('Failed to request dialog_id', status_code=400)
    version = flask.request.json.get("version")
    if version is None or len(version) == 0:
        raise FailedRequest('Failed to request version', status_code=400)
    dialog_level_labels = flask.request.json.get("dialog_level_labels")
    if dialog_level_labels is None or len(dialog_level_labels) == 0:
        raise FailedRequest('Failed to request dialog_level_labels', status_code=400)
    annotator_id = flask.request.json.get("annotator_id")
    if annotator_id is None or len(annotator_id) == 0:
        raise FailedRequest('Failed to request annotator_id', status_code=400)
    sentences = flask.request.json.get("sentences")
    if sentences is None or len(sentences) == 0:
        raise FailedRequest('Failed to request sentences', status_code=400)

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
        if sentence["turn_id"] in dialog["turns"].keys():
            dialog["turn_id"].append(token)
        else:
            dialog["turn_id"] = [token]
    col = client["sample_annotated"]["dialogs"]
    col.insert_one(dialog)
    return 200
            
@app.route('/index/<id>', methods=["GET"]) 
def show(id):
    context = {"id": id}
    return flask.render_template("index.html", **context)