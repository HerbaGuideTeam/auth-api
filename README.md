# Authentication API

## Overview
The Authentication API is a service designed for user authentication and authorization using Firebase with FastAPI. It includes features such as user registration, login (including Google login), logout, token validation, and fetching user details.

## Features
- User Registration
- User Login
- Google Login
- User Logout
- Token Validation
- Fetch User Details

## Prerequisites
- [Python](https://www.python.org/) 3.8+
- [Firebase](https://firebase.google.com/)
- [Firestore](https://firebase.google.com/docs/firestore) (or another compatible database)
- [Docker](https://www.docker.com/) (optional, for containerized deployment)

## Installation

### Using Pipenv
1. Clone the repository:
    ```sh
    git clone https://github.com/HerbaGuideTeam/auth-api.git
    cd auth-api
    ```

2. Install dependencies:
    ```sh
    pipenv install
    ```

3. Activate the virtual environment:
    ```sh
    pipenv shell
    ```

4. Run the application:
    ```sh
    python main.py
    ```

### Using Docker
1. Build the Docker image:
    ```sh
    docker build -t auth-api .
    ```

2. Run the Docker container:
    ```sh
    docker run -p 8000:8000 auth-api
    ```

## Configuration
Ensure that your Firebase and Firestore configurations are set correctly in the `main.py` file or through environment variables. The application uses Google Cloud Secret Manager for managing secrets.

## Endpoints

### Register
- **URL:** `/signup`
- **Method:** `POST`
- **Payload:**
  ```json
  {
      "name": "John Doe",
      "email": "sample@gmail.com",
      "password": "samplepass123"
  }

#### Responses
- **Success Response (201 Created):**
```json
{
    "message": "User account created successfully for user {user_id}"
}
```
- **Error Response (400 Bad Request):**
```json
{
    "detail": "Account already created for the email {email}"
}
```

### Login
- **URL:** `/login`
- **Method:** `POST`
- **Payload:**
  ```json
  {
      "email": "sample@gmail.com",
      "password": "samplepass123"
  }

#### Responses
- **Success Response (200 OK):**
```json
{
    "token": "{JWT_token}",
    "user": {
        "uid": "{user_id}",
        "email": "john.doe@example.com",
        "display_name": "John Doe"
    }
}
```
- **Error Response (400 Bad Request):**
```json
{
    "detail": "Invalid Credentials"
}
```
  
### Logout
- **URL:** `/logout`
- **Method:** `POST`
- **Payload:**
  ```json
  {
      "token": "<JWT>"
  }

#### Responses
- **Success Response (200 OK):**
```json
{
    "message": "Logout successful"
}
```
- **Error Response (400 Bad Request):**
```json
{
    "detail": "Invalid token: {error_message}"
}
```

### Validate Token
- **URL:** `/ping`
- **Method:** `POST`
- **Headers:**
    - `Authorization`: `Bearer <token>` : use a token from login
  
#### Responses
- **Success Response (200 OK):**
```json
{
    "user_id": "{user_id}",
    "token": "{JWT_token}"
}
```
- **Error Response (400 Bad Request):**
```json
{
    "detail": "Invalid token: {error_message}"
}
```
- **Error Response (401 Unauthorized):**
```json
{
    "detail": "Token has expired"
}
```

### Get user
- **URL:** `/user/{uid}`
- **Method:** `GET`
- #### Responses
- **Success Response (200 OK):**
```json
{
    "uid": "{user_id}",
    "email": "john.doe@example.com",
    "display_name": "John Doe"
}
```
- **Error Response (404 Not Found):**
```json
{
    "detail": "User not found"
}
```

## Models
The `models.py` file defines the following schemas:

### SignUpSchema
```python
class SignUpSchema(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "sample@gmail.com",
                "password": "samplepass123"
            }
        
```
### LoginSchema
```python
class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "sample@gmail.com",
                "password": "samplepass123"
            }
        }
```
### LogoutSchema
```python
class LogoutSchema(BaseModel):
    token: str

    class Config:
        json_schema_extra = {
            "example":{
                "token": ""
            }
        }
```
