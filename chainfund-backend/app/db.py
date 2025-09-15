from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient = None
database = None


async def init_db():
    global client, database
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.database_name]
    print(f"Connected to MongoDB: {settings.database_name}")


async def close_db():
    global client
    if client:
        client.close()
        print("MongoDB connection closed")


async def get_database():
    return database


async def get_collection(collection_name: str):
    db = await get_database()
    return db[collection_name]