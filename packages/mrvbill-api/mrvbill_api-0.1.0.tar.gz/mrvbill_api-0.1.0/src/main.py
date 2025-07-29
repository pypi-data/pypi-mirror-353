from fastapi import FastAPI, Depends, Response, status
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from typing import List

from auth0_fastapi.config import Auth0Config # type: ignore
from auth0_fastapi.auth.auth_client import AuthClient # type: ignore
from auth0_fastapi.server.routes import router, register_auth_routes # type: ignore
from auth0_fastapi.errors import register_exception_handlers # type: ignore

from src.services.users import insert_user, fetch_users
from src.config import Settings, get_settings

token_auth_scheme = HTTPBearer()
app = FastAPI(
    title="MrvBill API",
    description="API for MrvBill application",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get settings
def get_app_settings():
    return get_settings()

@app.get('/private')
def private(token: str = Depends(token_auth_scheme)):
    print("Token is $t", token)
    return {'message': 'This is a private route'}

@app.get("/")
async def root(settings: Settings = Depends(get_app_settings)):
    return {
        "message": "Hello, World!",
        "version": settings.API_VERSION,
        "debug": settings.DEBUG
    }

@app.get("/user", response_model=List[dict])
async def get_users():
    users = await fetch_users()
    return users

@app.post("/user", response_model=dict)
async def create_user(user):
    result = await insert_user(user.dict())
    return {"id": str(result.inserted_id)}

# For AWS Lambda
handler = Mangum(app)