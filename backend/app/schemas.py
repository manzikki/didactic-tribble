from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    nickname: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    quiz_starts: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuizStartResponse(BaseModel):
    nickname: str
    quiz_starts: int
