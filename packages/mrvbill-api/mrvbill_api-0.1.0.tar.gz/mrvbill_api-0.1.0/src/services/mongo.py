from motor.motor_asyncio import AsyncIOMotorClient
from src.config import get_settings

settings = get_settings()

# Create the client
client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB_NAME]

# Ensure the connection is established
async def init_mongo():
    try:
        await db.command('ping')
        print('Connected to MongoDB!')
    except Exception as e:
        print(f'Error connecting to MongoDB: {e}')
        raise

# Create a function to get the database
def get_db():
    return db

async def ping():
    try:
        await client.admin.command('ping')
        print('Pinged Atlas deployment!')
    except Exception as e:
        print(e)

# Note: You can't directly call an async function like this
# Instead, you should use asyncio.run() or run it in an async context
ping()