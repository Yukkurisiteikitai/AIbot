# app/schemas.py
from pydantic import BaseModel, EmailStr, Field,ConfigDict
from typing import List, Optional, Dict, Any
import datetime # Pydanticでdatetime型を扱うために必要

# Pydantic V2の場合: from pydantic import ConfigDict

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    user_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # Pydantic V1
    class Config:
        # orm_mode = True
        # Pydantic V2
        model_config = ConfigDict(from_attributes=True)


# --- Message Schemas ---
class EditHistoryEntry(BaseModel):
    edited_at: datetime.datetime
    previous_content: str

class MessageBase(BaseModel):
    role: str
    context: str
    feeling: Optional[str] = None
    cache: Optional[Dict[str, Any]] = None

class MessageCreate(MessageBase):
    sender_user_id: Optional[int] = None # AIの場合は指定しない

class Message(MessageBase):
    message_id: int
    thread_id: str
    sender_user_id: Optional[int] = None
    edit_history: Optional[List[EditHistoryEntry]] = None
    timestamp: datetime.datetime

    # Pydantic V1
    class Config:
        # orm_mode = True
        # Pydantic V2
        model_config = ConfigDict(from_attributes=True)


# --- Thread Schemas ---
class ThreadBase(BaseModel):
    mode: str
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    meta_data: Optional[Dict[str, Any]] = None

class ThreadCreate(ThreadBase):
    # スレッド作成時に最初のメッセージも受け取るならここに定義
    # initial_message_context: Optional[str] = None
    pass


class Thread(ThreadBase):
    thread_id: str
    owner_user_id: int
    timestamp: datetime.datetime
    messages: List[Message] = [] # スレッド取得時にメッセージも返す場合

    # Pydantic V1
    class Config:
        # orm_mode = True
    # Pydantic V2
        model_config = ConfigDict(from_attributes=True)


# --- Feedback Schemas ---
class FeedbackBase(BaseModel):
    correct: int = Field(..., ge=-2, le=2) # ge, le で数値範囲バリデーション
    user_comment: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    message_id: int
    # user_idは認証情報から取得するため、リクエストボディには含めないのが一般的

class Feedback(FeedbackBase):
    feedback_id: int
    message_id: int
    user_id: int
    timestamp: datetime.datetime

    # Pydantic V1
    class Config:
        # orm_mode = True
    # Pydantic V2
        model_config = ConfigDict(from_attributes=True)