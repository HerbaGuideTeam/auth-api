from pydantic import BaseModel

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
        }

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
