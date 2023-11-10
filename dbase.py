#from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
import os, json
from itertools import islice
from bson.objectid import ObjectId
#load_dotenv()
#password = os.getenv("MONGO_PASSWORD")
uri = f"mongodb+srv://ndeineyo:mongoacc@limbika.brqsfst.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)
bot_db = client.Bot_db
collection = bot_db.history
library = bot_db.libray
pris = bot_db.Prisoners
# 6490804f8a5af9aee42c4f31 

def inserting_documents(info):
  return True,info if pris.insert_one({ "Name" : info[0],"Surname": info[1], "details" : info[2]}) else False

def find( chat_id = None):  
  hist = pris.find_one({"_id": ObjectId("654d5a263d98904788854490")},  projection = {"_id": 0} )
  if hist:
    return hist

def update(info):
  #checking if the id is presnt in the database
  user = find(info[0])
  if user:
    return pris.update_one({"_id": ObjectId(info[3])}, {"$set": {"Name": info[0], "Surname" : info[1], "details" : info[2]}}), info  
  


def find_zose():
    hist = pris.find({},  projection = {"_id": 0})
    if hist:
        #datas = []
        #for doc in find_zose():
        #    datas.append(doc)
        return hist

        