from src.services.mongo import db
from bson import json_util

async def insert_user(data):
    user_data = dict(data)
    print("Inserting user data:", user_data)  # This will show what's being inserted
    try:
        result = await db.users.insert_one(user_data)
        return result
    except Exception as e:
        print(f"Error inserting user: {e}")
        raise
    
async def fetch_users():
    try:
        cursor = db.users.find()
        users = await cursor.to_list(length=None)
        # Convert MongoDB documents to JSON-serializable format
        return json_util.dumps(users)
    except Exception as e:
        print(f"Error fetching users: {e}")
        raise
    