from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set. Add it as an environment variable in Render.")

# Mongo client with proper TLS & CA bundle
client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=10000,
)

db = client["euron"]
euron_data = db["euron_coll"]

app = FastAPI()


class EuronData(BaseModel):
    name: str
    phone: int
    city: str
    course: str


@app.post("/euron/insert")
async def insert_euron_data(data: EuronData):
    result = await euron_data.insert_one(data.dict())
    return {
        "message": "Data inserted successfully",
        "id": str(result.inserted_id)
    }


@app.get("/euron/getdata")
async def get_euron_data():
    items = []
    cursor = euron_data.find({})
    async for document in cursor:
        document["_id"] = str(document["_id"])
        items.append(document)
    return items
