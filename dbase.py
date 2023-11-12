#from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
from passlib.context import CryptContext
from datetime import datetime, timedelta
from PIL import Image
from  fastapi import Depends, status , HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import schemas

  
  
  
  
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
    #self.medical_records = self.bot_db.Medical_Records
    self.crypto_cont = CryptContext(schemes = ["bcrypt"], deprecated = "auto")
  def inserting_documents(self, info):
    return True,info if self.pris.insert_one({ "Name" : info[0],"Surname": info[1], "details" : info[2]}) else False

  def insert_prisoner(self, info):
    return True if self.pris.insert_one({ "Name" : info[0],"Photo": info[6] , "Date of Birth" : info[1], "Prison ID" :info[2], "Village" :  info[3] ,"Sentence Length"  : info[4], "Release Date" : info[5], "Medical Details" : info[7] }) else False

  def find(self,chat_id = None):  
    hist = self.pris.find_one({"_id": ObjectId("654d5a263d98904788854490")},  projection = {"_id": 0} )
    if hist:
      return hist

  def update(self,info):
    #checking if the id is presnt in the database
    self.user = self.find(info[0])
    if self.user:
      return self.pris.update_one({"_id": ObjectId(info[3])}, {"$set": {"Name": info[0], "Surname" : info[1], "details" : info[2]}}), info  
    
  def create_user(self,details):
    return details if self.user.insert_one({"Name" : details[0], "Position" : details[1], "Password" : self.crypto_cont.hash(details[2])}) else "User Registration failed"

  def find_user(self, username):
    self.found = self.user.find_one({"Name" : username}) 
    return self.found["Name"],self.found["Password"], self.found["Position"] if self.found else None
    
    
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

  
#dbms = DataBase_Manager()
#print(type(dbms.find_user("defloat")["Password"]))
#cc= Access()
#print(acc.create_token({"username": "defloat", "Authority": "Chief Founder" }))