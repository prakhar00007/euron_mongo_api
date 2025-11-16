from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db=client['euron']
euron_data=db['euron_coll']

app = FastAPI()

class euronData(BaseModel):
    name: str
    phone: int
    city: str
    course: str

@app.post("/euron/insert")
async def euron_data_insert_helper(data: euronData):
    result = await euron_data.insert_one(data.dict())
    return {"message": "data inserted successfully", "id": str(result.inserted_id)}

@app.get("/euron/getdata")
async def get_euron_data():
    items=[]
    cursor= euron_data.find({})
    async for document in cursor:
        document['_id']=str(document['_id'])
        items.append(document)  

    return items


