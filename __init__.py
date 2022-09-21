from http import client
import flask

import datetime  
import os

from dotenv import load_dotenv
from pymongo import MongoClient

app = flask.Flask(__name__)

metadata = dict() #just in case

load_dotenv()
MONGODB_URI = os.environ['MONGODB_URI']
client = MongoClient(MONGODB_URI)



if __name__ == "__main__":
    app.run()