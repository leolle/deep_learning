# -*- coding: utf-8 -*-
import pymongo
import pandas as pd
from pymongo import MongoClient
import datetime
client = MongoClient()

client = MongoClient('mongodb://192.168.1.73:27017/')

db = client['local']

collection = db.wiki
