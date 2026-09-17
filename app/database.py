from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection URL
MONGO_URL = "mongodb://localhost:27017"

# Create async MongoDB client
client = AsyncIOMotorClient(MONGO_URL)

# Select database
database = client["taskflow"]

# Select users collection
users_collection = database["users"]