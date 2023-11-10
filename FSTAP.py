from fastapi import FastAPI,Path 
from pydantic import BaseModel 
from typing import Optional
import dbase
from bson.objectid import ObjectId


class Item(BaseModel):
    name : str
    Surname :str
    details : Optional[str]
    id : Optional[str]
    
app = FastAPI()
data = {}
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/data/{id}")
async def root():    
    return {"data": dbase.find()}

@app.post("/insert/{id}")
async def add_new(id : int,item : Item):
    dbase.inserting_documents([item.name, item.Surname, item.details])
    return item

@app.get("/all_data")
async def get_all_data():
    docs = []
    for doc in dbase.find_zose():
        docs.append(doc)
    return {"data": docs}

@app.post("/update")
async def update(item :Item):
    updated = dbase.update([item.name, item.Surname, item.details, item.id])
    return updated[1] if updated else "AN ERROR OCCURED WHILE TRYING TO UPDATE THE RECORDS"