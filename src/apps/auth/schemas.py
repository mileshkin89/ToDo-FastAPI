from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, model_validator


class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    email: EmailStr = Field(max_length=100)
    name: str | None = Field(default=None, max_length=50)
    password: str = Field(min_length=5, max_length=100)
    repeat_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.repeat_password:
            raise ValueError("Passwords do not match")
        return self


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str | None = None
    last_login: datetime | None = None

    model_config = {
        "from_attributes": True
    }


class UserListResponse(BaseModel):
    users: list[UserResponse]

    model_config = {
        "from_attributes": True
    }
