import os
import uvicorn
import pyrebase
from fastapi import FastAPI
from models import LoginSchema, SignUpSchema
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from google.cloud import secretmanager
import json

app = FastAPI(
    description="This is a simple app to show firebase auth with fastapi",
    title="firebase auth",
    docs_url="/"
)

import firebase_admin
from firebase_admin import credentials, auth

def access_secret_version(project_id, secret_id, version_id):
    client = secretmanager.SecretManagerServiceClient()

    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")

    return json.loads(payload)

if not firebase_admin._apps:
    firebaseSa = access_secret_version('c241-ps193', 'firebase_sa','1')
    cred = credentials.Certificate(firebaseSa)
    firebase_admin.initialize_app(cred)

# Fetch the firebaseConfig from Secret Manager
firebaseConfig = access_secret_version('c241-ps193', 'firebase_config','4')

firebase = pyrebase.initialize_app(firebaseConfig)

@app.post('/signup')
async def create_an_account(user_data: SignUpSchema):
    name = user_data.name
    email = user_data.email
    password = user_data.password

    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name
        )
        return JSONResponse(content={"message": f"User account created successfully for user {user.uid}"},
                            status_code=201)
    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=400,
            detail=f"Account already created for the email {email}"
        )

@app.post('/login')
async def create_access_token(user_data: LoginSchema):
    email = user_data.email
    password = user_data.password

    try:
        user = firebase.auth().sign_in_with_email_and_password(
            email=email,
            password=password
        )

        token = user['idToken']

        return JSONResponse(
            content={
                "token": token
            }, status_code=200
        )
    except:
        raise HTTPException(
            status_code=400, detail="Invalid Credentials"
        )

@app.post('/ping')
async def validate_token(request: Request):
    headers = request.headers
    jwt = headers.get('authorization')
    user = auth.verify_id_token(jwt)

    return user["user_id"]

@app.get('/user/{uid}')
async def get_user(uid: str):
    try:
        user = auth.get_user(uid)
        return JSONResponse(
            content={
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name
            }, status_code=200
        )
    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)