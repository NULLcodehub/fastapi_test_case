from fastapi import FastAPI
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import os

app = FastAPI()

# MongoDB Atlas connection URI (replace <username>, <password>, <cluster_url>, and <dbname> with your values)
MONGO_URI = "mongodb+srv://souravsahaprgmr:fXwVHcJnoddSjHBU@cluster0.0h1fz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGO_URI)
db = client[os.getenv("dbname", "testdb")]  # Use 'testdb' by default

# Pydantic model for CRUD operations
class ItemModel(BaseModel):
    name: str
    description: str

# Helper function to transform MongoDB ObjectID to string
def mongo_helper(item):
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "description": item["description"]
    }

# Create
@app.post("/items")
async def create_item(item: ItemModel):
    new_item = await db["items"].insert_one(item.dict())
    created_item = await db["items"].find_one({"_id": new_item.inserted_id})
    return mongo_helper(created_item)

# Read
@app.get("/items")
async def read_items():
    items = []
    async for item in db["items"].find():
        items.append(mongo_helper(item))
    return items

# Update
@app.put("/items/{item_id}")
async def update_item(item_id: str, item: ItemModel):
    await db["items"].update_one({"_id": item_id}, {"$set": item.dict()})
    updated_item = await db["items"].find_one({"_id": item_id})
    return mongo_helper(updated_item)

# Delete
@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    result = await db["items"].delete_one({"_id": item_id})
    return {"deleted_count": result.deleted_count}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "FastAPI with MongoDB Atlas is working!"}
