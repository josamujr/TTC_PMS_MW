#from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
from passlib.context import CryptContext
from datetime import datetime, timedelta
from PIL import Image
from  fastapi import Depends, status , HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import schemas, ast
from enum import Enum


def exception_handler(func):
  def main(*args,**kwargs):
    try:
      func(*args,**kwargs)
      
    except Exception as e:
      raise e
    
  return main
  
class Authentication():
  def __init__(self):
    self.crypto_cont = CryptContext(schemes = ["bcrypt"], deprecated = "auto")
    #oauth_scheme = OAuth2PasswordBearer(tokenUrl= "token")
    
    def verify(self,plain, hashed ):
        return self.crypto_cont.verify(plain, hashed)
    
    def get_pass_hash(self,password):
        return self.crypto_cont.hash(password)
      
      
class DataBase_Manager:
  def __init__(self):
    self.uri = f"mongodb+srv://ndeineyo:mongoacc@limbika.brqsfst.mongodb.net/?retryWrites=true&w=majority"
    self.client = MongoClient(self.uri)
    self.bot_db = self.client.Bot_db
    self.user = self.bot_db.Users
    self.pris = self.bot_db.Prisoners
    self.cases = self.bot_db.Court_Cases
    self.guard = self.bot_db.Guards
    self.vds = self.bot_db.Visitings
    #self.medical_records = self.bot_db.Medical_Records
    self.crypto_cont = CryptContext(schemes = ["bcrypt"], deprecated = "auto")
  
  def create_dbs(self):
    #db.runCommand( { collMod: "users", validator: {}})
    self.validators = {
      "Prisoners" :{
        "$jsonSchema": {
            "bsonType": "object",
            "additionalProperties": True,
            "required": ["Name", "Photo", "Date of Birth", "Prisoner ID", "Village","Sentence Length", "Date of admission" , "Medical Details","Case file number","Gender",'Release Date'],
            "properties": { "Name": {"bsonType": "string"}, "Photo": {"bsonType": "binData"},"Date of Birth": {"bsonType": "string"},"Release Date" : {"bsonType": "string"},
              "Prisoner ID": {"bsonType": "int"},"Village": {"bsonType": "string"},"Sentence Length": {"bsonType": "string"},"Gender" : { "enum": ["Male", "Female"]},
              "Date of admission": {"bsonType": "string"},"Date Released": {"bsonType": ["null", "string"]},"Case file number" : {"bsonType": "int"},
              'Release Date' : {"bsonType": "string"},"Medical Details": {"bsonType": "object","items": {"bsonType": "string"}}  }  }  },
                  
      "Cases" :{
                "$jsonSchema": {
                  "bsonType": "object",
                  "required": ["Case File Number","Associated Inmates","Offense Details","Risk Assessment", "Case Manager"],
                  "properties": {
                    "Case File Number": {"bsonType": "int","description": "Case file number"},
                    "Associated Inmates": {"bsonType": "object" },
                    "Offense Details": {"bsonType": "string","description": "User Password"},
                    "Risk Assessment": {"bsonType": "string","description": "User Password"},
                    "Case Manager": {"bsonType": "object","items": {"bsonType": "string"}}}     }  
                },
      
      "Users": {
                "$jsonSchema": {
                  "bsonType": "object",
                  "required": ["Name","Position","Password"],
                  "properties": {
                    "Name": {
                      "bsonType": "string",
                      "description": "Name of the user"
                    },
                    "Position": {
                      "bsonType": "string",
                      "description": "Another field of string type"
                    },
                    "Password": {
                      "bsonType": "string",
                      "description": "User Password"
                    }
                  }
                }
                },
      
      "Visitings": {
        "$jsonSchema": {
                  "bsonType": "object",
                  "required": ["Name","Prisoner ID","Dates"],
                  "properties": {
                    "Name": {
                      "bsonType": "string",
                      "description": "Name of the user"
                    },
                    "Prisoner ID": {
                      "bsonType": "string",
                      
                    },
                    "Dates": { "bsonType": "object",
                              "required": ["Visitor's Name","Visitor's Number","Relatopnship","Items brought"],
                              "properties": {
                                  "Date" : {"bsonType": "string"},
                                  "Visitor's Name": {"bsonType": "string"},
                                  "Visitor's Number" :{"bsonType": "string"},
                                  "Relatopnship" : {"bsonType": "string"},
                                  "Items brought" : {"bsonType": "array",  "items": {"bsonType": "string","description": "Each item in the array must be a string"}}
                              }  }
                      }
                    }
                  }
      
      }
    
    self.bot_db.create_collection("Visitings",validator= self.validators["Visitings"],validationLevel="strict")
    #self.bot_db.create_collection("Prisoners",validator= self.validators["Prisoners"],validationLevel="strict",) 
    #self.bot_db.create_collection("Court_Casesz",validator= self.validators["Cases"],validationLevel="strict",validationAction = "error" )
  
  def find_by_date(self, info):
    person = self.pris.find({info[0]: info[1]},  projection = {"_id": 0, "Photo" : 0} )
    return person if person else None

  @exception_handler
  def visitings(self,info):
    return self.vds.insert_one({"Name" : info[0],"Prisoner ID" : info[1],"Dates" : {"Date" : info[2], "Visitor's Name": info[3], "Visitor's Number" : info[4], "Relatopnship" : info[5], "Items brought" : info[6]}} )
    
  def insert_prisoner(self, info):
    return True if self.pris.insert_one({ "Name" : info[0],"Photo": info[6] , "Date of Birth" : info[1], "Prisoner ID" :info[2],  "Case file number" : info[8] ,"Gender": info[9] , "Village" :  info[3] ,"Sentence Length"  : info[4], "Date of admission" : info[5], "Medical Details" : ast.literal_eval(info[7]), 'Release Date' : info[10] }) else False
    pass

  def find(self, info):  
    if info[0] == "_id":
      person = self.pris.find_one({"_id": ObjectId(info[1])},  projection = {"_id": 0} )
      
      return person if person else None

    
  def update(self,info):
    #checking if the id is presnt in the database
    self.user = self.find(info[0])
    if self.user:
      return self.pris.update_one({"_id": ObjectId(info[3])}, {"$set": {"Name": info[0], "Surname" : info[1], "details" : info[2]}}), info  
    
  def create_user(self,details):
    return details if self.user.insert_one({"Name" : details[0], "Position" : details[1], "Password" : self.crypto_cont.hash(details[2])}) else "User Registration failed"

  #@exception_handler
  def find_user(self, username):
    self.found = self.user.find_one({"Name" : username}) 
    if self.found:
      return self.found["Name"],self.found["Password"], self.found["Position"]  
    else:
      return None
    
    
  def find_zose(self):
      self.hist = self.pris.find({},  projection = {"_id": 0, "Photo" : 0})
      if self.hist:
          self.datas = []
          for doc in self.hist:
            self.datas.append(doc)
          self.dictionary = self.datas
          #self.dictionary[-1]["Photo"]   image
          return self.dictionary

  def new_case(self, data):
    self.cases.insert_one({"Case File Number" : data[0], "Associated Inmates" : data[1],"Offense Details" : data[2], "Risk Assessment" : data[3], "Case Manager" : data[4]  })
    return data
  def new_guard(self, data):
    
    self.guard.insert_one({"Name" : data[0], "Contact" : data[1], "Employee Id" : data[2], "Village" : data[3]})
    return data
  def update_prisoner_medical_records(self,data):
    self.user = self.pris.find_one( {"Prison ID":int(data[0])})
    if self.user:
      self.prisoner = self.pris.find_one({"Prison ID" : data[0]})
      self.medical_records = self.prisoner["Medical Details"]
      self.pris.update_one({"Prison ID": int(data[0]) }, {"$set": {"Medical Details" :   self.medical_records + data[1]}})
      return data[1]
    return "Prisoner not found" 
  
  

class Access(DataBase_Manager):
  def __init__(self):
    self.secrete_key = "dfjfhdweiou438923ygdhwbaskllw12398ue"
    self.ALGORITHM = "HS256"
    #ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

  def create_token(self, data : dict):
    self.to_encode = data.copy()
    self.expire = datetime.utcnow() + timedelta(minutes= 20)
    print(self.expire)
    self.to_encode.update({"exp" :self.expire})
    self.encoded_jwt = jwt.encode(self.to_encode, self.secrete_key, algorithm= self.ALGORITHM)
    return self.encoded_jwt
  def verify_access_token(self, token : str, credentials_exception):
    try:
      self.payload = jwt.decode(token, self.secrete_key, algorithms= [self.ALGORITHM])
      self.id : str = self.payload.get("username")
      if self.id is None:
          raise credentials_exception

      #self.token_data = schemas.TokenData(id = id)  # validating the token
    except JWTError:
      raise credentials_exception
    return self.payload.get("Authority")

  def get_current_user(self, token : str = Depends(OAuth2PasswordBearer(tokenUrl= "login"))):
      self.credential_exceptopn = HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail='UN AUTHORISED ACESS', headers={"WWW--AUTHENTICATE" : "Bearer"})
      self.TOKEN = self.verify_access_token(token, self.credential_exceptopn)
      #self.user = self.find_user(self.TOKEN.id)
      return self.TOKEN
