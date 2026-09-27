from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    confirm_password: str
    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v

class LoginRequest(BaseModel):
    username: str
    password: str

class HomeItem(BaseModel):
    category: str
    quantity: int = Field(ge=1, le=50)
    style: Optional[str] = "modern"

class HomeRequest(BaseModel):
    budget: float = Field(gt=0, le=100000000)
    room_type: str = Field(min_length=2, max_length=80)
    style: str = Field(min_length=2, max_length=80)
    items: list[HomeItem] = Field(min_length=1, max_length=20)

class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=100000000)
    guests: int = Field(ge=1, le=10000)
    event_type: str = Field(min_length=2, max_length=80)
    venue: str = Field(min_length=2, max_length=120)
    preferences: str = Field(default="balanced", max_length=500)

class JewelryRequest(BaseModel):
    budget: float = Field(gt=0, le=100000000)
    occasion: str = Field(min_length=2, max_length=100)
    style: str = Field(min_length=2, max_length=100)
    outfit_description: str = Field(default="Not provided", max_length=500)
