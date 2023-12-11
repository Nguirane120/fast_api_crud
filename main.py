from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from bson import ObjectId


app = FastAPI()

# MongoDB connection URL
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
database = client["fast_api"]
collection = database["items"]

class Item(BaseModel):
    id: str = Field(None, alias='_id')  # Champ ID correspondant au champ _id de MongoDB
    name: str
    description: str = None
    
    
    
@app.post("/items/", status_code=201)
async def create_item(item: Item):
    result = await collection.insert_one(item.model_dump())
    
    # Retrieving the ID of the inserted document

    inserted_id = result.inserted_id
    items = {
        "id": str(inserted_id),
        **item.model_dump(),  # Return all fields including 'name' and 'description'
        }
    # Returning the ID as a response
    return items  # Converting ObjectId to string for JSON response




@app.get("/items/")
async def read_items():
    items = []
    
    cursor = collection.find({})
    
    async for document in cursor:  
        document['_id'] = str(document['_id'])  

        item_model = Item(**document)  
        items.append(item_model)
    
    if items:
        return items
    raise HTTPException(status_code=404, detail="Items not found")

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    item = await collection.find_one({"_id": ObjectId(item_id)})
    if item:
        item["_id"] = str(item["_id"])  # Convertir l'ObjectId en str
        return Item(**item)
    raise HTTPException(status_code=404, detail="Item not found")


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    print(item_id)
    updated_item = await collection.find_one_and_update(
        {"_id": ObjectId(item_id)}, {"$set": item.model_dump()}
    )
    if updated_item:
        return item
    raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/items/{item_id}", response_model=Item)
async def delete_item(item_id: str):
    deleted_item = await collection.find_one_and_delete({"_id": ObjectId(item_id)})
    if deleted_item:
        # Convertir l'_id en str avant de le retourner
        deleted_item["_id"] = str(deleted_item["_id"])
        return deleted_item
    raise HTTPException(status_code=404, detail="Item not found !")
