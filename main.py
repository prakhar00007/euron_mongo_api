from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import certifi
from bson import ObjectId
from typing import Optional



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


@app.get("/euron/getdata")
async def get_euron_data():
    items = []
    cursor = euron_data.find({})
    async for document in cursor:
        document["_id"] = str(document["_id"])
        items.append(document)
    return items


@app.post("/euron/insert")
async def insert_euron_data(data: EuronData):
    result = await euron_data.insert_one(data.dict())
    inserted_doc = await euron_data.find_one({"_id": result.inserted_id})
    inserted_doc["_id"] = str(inserted_doc["_id"])
    inserted_doc["message"] = "Data inserted successfully"
    return inserted_doc


@app.delete("/euron/delete/{item_id}")
async def delete_euron_data(item_id: str):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    doc = await euron_data.find_one({"_id": ObjectId(item_id)})

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    await euron_data.delete_one({"_id": ObjectId(item_id)})
    doc["_id"] = str(doc["_id"])
    doc["message"] = "Document deleted successfully"
    return doc

@app.put("/euron/full_update/{item_id}")
async def update_euron_full(item_id: str, data: EuronData):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    existing = await euron_data.find_one({"_id": ObjectId(item_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Document not found")

    await euron_data.replace_one(
        {"_id": ObjectId(item_id)},
        data.dict()
    )

    updated = await euron_data.find_one({"_id": ObjectId(item_id)})
    updated["_id"] = str(updated["_id"])
    updated["message"] = "Full update successful"
    return updated



class EuronPartialUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[int] = None
    city: Optional[str] = None
    course: Optional[str] = None


@app.patch("/euron/partial_update/{item_id}")
async def update_euron_partial(item_id: str, data: EuronPartialUpdate):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    update_data = data.dict(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    existing = await euron_data.find_one({"_id": ObjectId(item_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Document not found")

    await euron_data.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": update_data}
    )

    updated = await euron_data.find_one({"_id": ObjectId(item_id)})
    updated["_id"] = str(updated["_id"])
    updated["message"] = "Partial update successful"
    return updated

