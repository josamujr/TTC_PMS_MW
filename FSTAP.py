from fastapi import FastAPI, File, UploadFile, Depends, status, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import Optional, Annotated, Dict, List,Any
from bson.objectid import ObjectId
from datetime import datetime,timedelta
import dbase as db, codecs,schemas, pendulum, uvicorn
from dataclasses import dataclass
from passlib.context import CryptContext
from datetime import date, datetime


router = APIRouter(tags=['Authentication'])
app = FastAPI()
authenticator = db.Authentication()
dbase = db.DataBase_Manager()
acc = db.Access()

class tsiku(BaseModel):
    day : date
    
class medic_details(BaseModel):
    HIV : str
    Malaria  : str
    Height : int
    Other : str
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
    

class visiting_data(BaseModel):
    Name : str
    ID : int
    Visitors_Name : str
    Visitors_Number : int
    Relatopnship : str
    Items : List[str] = Field(default_factory=list)

class PrisonerDetails(BaseModel):
    name : str 
    dateOfBrth : str 
    Gender : str
    #Date_of_admission : date 
    #Date_Released : date
    prisonID : int 
    village : str
    sentenceLength : str 
    releaseDate : date
    Case_file_number : int
    #medical_details : List[str] = Field(default_factory=list)
    medical_details: Any = Field(default_factory=Dict)
    
class CaseMgmt_data(BaseModel):
    FileNumber : int
    involved_inmates : dict
    Offense_details : str
    Risk_assessment : str
    Case_mngr : dict
 
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

@app.post("/")
async def root():
    return "Takulanndilan kuno"

@app.get("/all_prisoners")
async def all_prisoners(get_user : int = Depends(acc.get_current_user)):
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
    if get_user == "admin":
        New_user = dbase.create_user([data.username, data.position, data.password])  
        return New_user if new_user else None
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='USER IS NOT AUTHORISED TO PROCEED WITH THIS OPERATION')



@app.post("/new_case/")
async def insert_case(file : CaseMgmt_data,get_user : int = Depends(acc.get_current_user)):
    dbase.new_case([file.FileNumber, file.involved_inmates, file.Offense_details, file.Risk_assessment, file.Case_mngr])
    return file 


@app.post("/new_guard")
async def new_guard(file : Guards_data, get_user : int = Depends(acc.get_current_user)):
    dbase.new_guard([file.name, file.contact, file.employee_id,file.village])
    
@app.post("/new_prisoner/", response_model= None)
def new_prisoner( photo: UploadFile, file : PrisonerDetails = Depends() , user_id : int = Depends(acc.get_current_user) ):
    
    addmission_date = pendulum.now("Africa/Maputo").to_formatted_date_string()
    release_d = pendulum.instance(file.releaseDate).to_formatted_date_string()
    dbase.insert_prisoner([file.name,  file.dateOfBrth, file.prisonID , file.village, file.sentenceLength ,addmission_date, photo.file.read(),file.medical_details, file.Case_file_number, file.Gender, release_d])
    #prisoner_info = codecs.decode(file.file.read(), "latin-1")   
    return file

@app.post("/edit_medical_report")
async def edit_medical_report(file: MedicReport, user_id : int = Depends(acc.get_current_user)):
    return dbase.update_prisoner_medical_records([file.prisoner_id, file.report])
    

@app.post("/new_dbs")
async def create_dbs(get_user : int = Depends(acc.get_current_user)):
    dbase.create_dbs()
    
@app.post("/find/release")
async def find_by_date_of_release(file : tsiku, get_user : int = Depends(acc.get_current_user)):
    date = pendulum.instance(file.day).to_formatted_date_string()
    prisoners, results =[],dbase.find_by_date(["Release Date", date])
    
    if results:
        for pris in results:
            prisoners.append(pris)
            
    return prisoners


@app.post("/find/admission")
async def find_by_admission_date(file : tsiku, get_user : int = Depends(acc.get_current_user)):
    
    date = pendulum.instance(file.day).to_formatted_date_string()
    prisoners, results =[], dbase.find_by_date(["Date of admission", date])
    if results:
        for pris in results:
            prisoners.append(pris)
            
    return prisoners if prisoners != [] else "No prisoner was registered on that day" 

@app.post("/visitings")
async def visitings(details : visiting_data, get_user : int = Depends(acc.get_current_user)):
    try:
        Date = pendulum.now("Africa/Maputo").to_formatted_date_string()
        return True if dbase.visitings([details.Name, str(details.ID) ,Date, details.Visitors_Name ,  str(details.Visitors_Number) , details.Relatopnship, details.Items]) else False

    except HTTPException as http_exception:
        if http_exception.status_code == 422:
            return 'Mbola a braz'
        

@app.post("/login/")
def login(user_credentials:  USer_data= Depends() ):
    user_logged_in = dbase.find_user(user_credentials.username)
    if user_logged_in != None:
        #AUTHENTICATING THE PASSWORD
        crypto_cont = CryptContext(schemes = ["bcrypt"], deprecated = "auto")
        if  not crypto_cont.verify(user_credentials.password, user_logged_in[1]):
            #raise HTTPException(status_code=status.HTTP_200_OK, detail =  "PASSWORD VERIFIED SUCCESSFULLY")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='INVALID CREDENTIALS')
        
        acccess_Token = acc.create_token({"username": user_logged_in[0], "Authority": user_logged_in[2] })
        
        return {"TOKEN"  : acccess_Token, "Token Type" : "bearer", "User" :user_logged_in}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='INVALID CREDENTIALS')
    
