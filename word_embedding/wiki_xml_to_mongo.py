# -*- coding: utf-8 -*-
import pymongo
from pymongo import MongoClient
client = MongoClient()

client = MongoClient('mongodb://172.17.0.1:27017/')

db = client['local']

collection = db.test_collection
import datetime
post = {
    "author": "Mike",
    "text": "My first blog post!",
    "tags": ["mongodb", "python", "pymongo"],
    "date": datetime.datetime.utcnow()
}
# insert a document
posts = db.posts
post_id = posts.insert_one(post).inserted_id
# varify inserting
db.collection_names(include_system_collections=False)
# Getting a Single Document With find_one()
import pprint
pprint.pprint(posts.find_one())
# querying on specific elements that the resulting document must match
pprint.pprint(posts.find_one({"author": "Mike"}))
# Querying By ObjectId
pprint.pprint(posts.find_one({"_id": post_id}))
# Bulk Inserts
new_posts = [{
    "author": "Mike",
    "text": "Another post!",
    "tags": ["bulk", "insert"],
    "date": datetime.datetime(2009, 11, 12, 11, 14)
}, {
    "author": "Eliot",
    "title": "MongoDB is fun",
    "text": "and pretty easy too!",
    "date": datetime.datetime(2009, 11, 10, 10, 45)
}]
result = posts.insert_many(new_posts)
result.inserted_ids
# Querying for More Than One Document
for post in posts.find():
    pprint.pprint(post)
# Counting
posts.count()
# counting just of those documents that match a specific query
posts.find({"author": "Mike"}).count()
# Range Queries
d = datetime.datetime(2009, 11, 12, 12)
for post in posts.find({"date": {"$lt": d}}).sort("author"):
    pprint.pprint(post)
# Indexing
result = db.profiles.create_index([('user_id', pymongo.ASCENDING)], unique=True)
sorted(list(db.profiles.index_information()))
user_profiles = [{
    'user_id': 211,
    'name': 'Luke'
}, {
    'user_id': 212,
    'name': 'Ziltoid'
}]
result = db.profiles.insert_many(user_profiles)
new_profile = {'user_id': 213, 'name': 'Drew'}
duplicate_profile = {'user_id': 212, 'name': 'Tommy'}
result = db.profiles.insert_one(new_profile)  # This is fine.
result = db.profiles.insert_one(duplicate_profile)
