import os
import uvicorn
import pyrebase
import firebase_admin
import json
from fastapi import FastAPI
from models import LoginSchema, SignUpSchema, LogoutSchema
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from google.cloud import secretmanager, firestore
from firebase_admin import credentials, auth
from firebase_admin.auth import ExpiredIdTokenError
from google.oauth2 import id_token
from google.auth.transport import requests



app = FastAPI(
    description="This is a simple app to show firebase auth with fastapi",
    title="firebase auth",
    docs_url="/"
)

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

db = firestore.Client()

@app.post('/signup')
async def create_an_account(user_data: SignUpSchema):
    name = user_data.name
    email = user_data.email
    password = user_data.password

    try:
        # Create user in Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name
        )
        
        # Save user data to Firestore
        user_ref = db.collection('users').document(user.uid)
        user_ref.set({
            'uid': user.uid,
            'name': name,
            'email': email
        })
        
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
        user_info = auth.get_user(user['localId'])  # Get user info

        return JSONResponse(
            content={
                "token": token,
                "user": {
                    "uid": user_info.uid,
                    "email": user_info.email,
                    "display_name": user_info.display_name
                }
            }, status_code=200
        )
    except:
        raise HTTPException(
            status_code=400, detail="Invalid Credentials"
        )
    
provider = firebase.auth.GoogleAuthProvider()

@app.post('/login_google')
async def login_google(request: Request):
    body = await request.json()
    token = body.get('id_token')
    if not token:
        raise HTTPException(status_code=400, detail="Authorization token missing")

    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request(), '828100792435-pfg1pvv2dlhmhdqbvvh4sl8ccji6dm6g.apps.googleusercontent.com')
        user_id = id_info['sub']

        try:
            user = auth.get_user(user_id)
        except auth.UserNotFoundError:

            user = auth.create_user(
                uid=user_id,
                email=id_info.get('email'),
                display_name=id_info.get('name')
            )
    
            user_ref = db.collection('users').document(user.uid)
            user_ref.set({
                'uid': user.uid,
                'name': id_info.get('name'),
                'email': id_info.get('email')
            })

        return JSONResponse(
            content={
                "token": token
            }, status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid token: {str(e)}")
    
@app.post('/logout')
async def logout(logout_data: LogoutSchema):
    jwt = logout_data.token
    if not jwt:
        raise HTTPException(status_code=400, detail="Authorization token missing")

    try:
        user = auth.verify_id_token(jwt)
        return JSONResponse(content={"message": "Logout successful"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid token: {str(e)}")

@app.post('/ping')
async def validate_token(request: Request):
    headers = request.headers
    jwt = headers.get('authorization')
    if not jwt:
        raise HTTPException(status_code=400, detail="Authorization token missing")
    try:
        user = auth.verify_id_token(jwt)
        return JSONResponse(content={"user_id": user["uid"], "token": jwt}, status_code=200)
    except ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid token: {str(e)}")

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
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)