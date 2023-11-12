from fastapi import FastAPI, File, UploadFile, Depends, status, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel 
from typing import Optional, Annotated, List
from bson.objectid import ObjectId
from datetime import datetime,timedelta
import dbase as db, codecs,schemas
from dataclasses import dataclass
from passlib.context import CryptContext


router = APIRouter(tags=['Authentication'])
app = FastAPI()
authenticator = db.Authentication()
dbase = db.DataBase_Manager()
acc = db.Access()
class Item(BaseModel):
    name : str
    Surname :str
    details : Optional[str]
    id : Optional[str]
class Token(BaseModel):
    access_token : str
    token_type : str
    User : list

class USer_data(BaseModel):
    username : str
    position : str
    password : str
    

class PrisonerDetails(BaseModel):
    name : str 
    dateOfBrth : str 
    prisonID : int 
    village : str
    sentenceLength : str 
    releaseDate : str
    Case_file_number : int
    medical_details : list[str]
    
class CaseMgmt_data(BaseModel):
    FileNumber : int
    involved_inmates : list
    Offense_details : str
    Risk_assessment : str
    Case_mngr : Optional[str]
 
class Guards_data(BaseModel):
    name : str
    contact : int
    employee_id : int
    village : Optional[str]   

class MedicReport(BaseModel):
    prisoner_id : int
    report : list[str]
class response(BaseModel):
    prisoner_id : int
    report : list[str]
    
class credentials(BaseModel):
    username : str
    password : str
    
data = {}
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/data/{id}")
async def root():    
    return {"data": dbase.find()}

@app.post("/insert/{id}")
async def add_new(id : int,item : Item, get_user : int = Depends(acc.get_current_user)):
    dbase.inserting_documents([item.name, item.Surname, item.details])
    return item

@app.get("/all_data")
async def get_all_data(get_user : int = Depends(acc.get_current_user)):
    docs = []
    for doc in dbase.find_zose():
        docs.append(doc)
    return {"data": docs}

@app.post("/update")
async def update(item :Item, get_user : int = Depends(acc.get_current_user)):
    updated = dbase.update([item.name, item.Surname, item.details, item.id])
    return updated[1] if updated else "AN ERROR OCCURED WHILE TRYING TO UPDATE THE RECORDS"



@app.post("/new_user/" )
async def new_user(data : USer_data,get_user : int = Depends(acc.get_current_user)):
    print(get_user)
    if get_user == "admin":
        New_user = dbase.create_user([data.username, data.position, data.password])  
        return New_user if new_user else None
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='USER IS NOT AUTHORISED TO PROCEED WITH THIS OPERATION')

@app.post("/new_prisoner/")
async def insert_prisoner( file: PrisonerDetails, get_user : int = Depends(acc.get_current_user)):
    dbase.insert_prisoner([file.name,  file.dateOfBrth, file.prisonID , file.village, file.sentenceLength ,file.releaseDate, file.medical_details])
    return file


@app.post("/new_case/")
async def insert_case(file : CaseMgmt_data,get_user : int = Depends(acc.get_current_user)):
    dbase.new_case([file.FileNumber, file.involved_inmates, file.Offense_details, file.Risk_assessment, file.Case_mngr])
    return file 


@app.post("/new_guard")
async def new_guard(file : Guards_data, get_user : int = Depends(acc.get_current_user)):
    dbase.new_guard([file.name, file.contact, file.employee_id,file.village])
    
@app.post("/add_picture/", response_model= None)
def new_prisoner_picture( photo: UploadFile, file : PrisonerDetails = Depends() , user_id : int = Depends(acc.get_current_user) ):
    dbase.insert_prisoner([file.name,  file.dateOfBrth, file.prisonID , file.village, file.sentenceLength ,file.releaseDate, photo.file.read(),file.medical_details])
    #prisoner_info = codecs.decode(file.file.read(), "latin-1")   
    return file

@app.post("/edit_medical_report")
async def edit_medical_report(file: MedicReport):
    return dbase.update_prisoner_medical_records([file.prisoner_id, file.report])
    

@app.post("/login/")
def login(user_credentials:  USer_data= Depends() ):
    user_logged_in = dbase.find_user(user_credentials.username)
    print(user_logged_in[2])

    if user_logged_in:
        #AUTHENTICATING THE PASSWORD
        crypto_cont = CryptContext(schemes = ["bcrypt"], deprecated = "auto")
        if  not crypto_cont.verify(user_credentials.password, user_logged_in[1]):
            #raise HTTPException(status_code=status.HTTP_200_OK, detail =  "PASSWORD VERIFIED SUCCESSFULLY")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='INVALID CREDENTIALS')
        
        acccess_Token = acc.create_token({"username": user_logged_in[0], "Authority": user_logged_in[2] })
        
        return {"TOKEN"  : acccess_Token, "Token Type" : "bearer", "User" :user_logged_in}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='INVALID CREDENTIALS')