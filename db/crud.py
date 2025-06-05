# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select # SQLAlchemy 1.4以降の非同期select
from sqlalchemy.orm import selectinload # リレーションを効率的にロードするため

from . import models, schemas
from typing import Optional
import uuid # thread_id生成用など
import datetime

# --- User CRUD ---
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).filter(models.User.user_id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    # パスワードハッシュ化はここで行う (passlibなどを使用)
    hashed_password = user.password + "_hashed" # 仮のハッシュ化
    db_user = models.User(
        email=user.email,
        name=user.name,
        password_hash=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# --- Thread CRUD ---
async def create_thread(db: AsyncSession, thread_data: schemas.ThreadCreate, owner_user_id: int) -> models.Thread:
    # thread_id の生成 (例: "cht_" + uuid)
    prefix = "cht_" if thread_data.mode == "chat" else "srh_"
    generated_thread_id = prefix + str(uuid.uuid4())

    db_thread = models.Thread(
        thread_id=generated_thread_id,
        owner_user_id=owner_user_id,
        mode=thread_data.mode,
        title=thread_data.title,
        tags=thread_data.tags,
        meta_data=thread_data.meta_data
    )
    db.add(db_thread)
    await db.commit()
    await db.refresh(db_thread)
    return db_thread

async def get_thread(db: AsyncSession, thread_id: str, include_messages: bool = False):
    query = select(models.Thread).filter(models.Thread.thread_id == thread_id)
    if include_messages:
        # N+1問題を避けるためにselectinloadを使う
        query = query.options(selectinload(models.Thread.messages).options(selectinload(models.Message.sender)))
    result = await db.execute(query)
    return result.scalars().first()

async def get_user_threads(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Thread)
        .filter(models.Thread.owner_user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# --- Message CRUD ---
async def create_message(db: AsyncSession, message_data: schemas.MessageCreate, thread_id: str) -> models.Message:
    db_message = models.Message(
        thread_id=thread_id,
        sender_user_id=message_data.sender_user_id, # ユーザーからの場合
        role=message_data.role,
        context=message_data.context,
        feeling=message_data.feeling,
        cache=message_data.cache
        # edit_historyは最初は空か、初期メッセージの場合は設定しない
    )
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message

async def edit_message(db: AsyncSession, message_id: int, new_context: str) -> Optional[models.Message]:
    result = await db.execute(select(models.Message).filter(models.Message.message_id == message_id))
    db_message = result.scalars().first()
    if not db_message:
        return None

    # 編集履歴の処理
    edit_entry = schemas.EditHistoryEntry(
        edited_at=datetime.datetime.now(datetime.timezone.utc), # UTCで保存推奨
        previous_content=db_message.context
    )
    if db_message.edit_history is None:
        db_message.edit_history = []

    # SQLAlchemyは変更を検知するために新しいリストを割り当てる必要がある場合がある
    current_history = []
    current_history = list(db_message.edit_history)
    current_history.append(edit_entry.model_dump()) # Pydantic V2: model_dump(), V1: dict()
    db_message.edit_history = current_history # 更新

    db_message.context = new_context
    db_message.timestamp = datetime.datetime.now(datetime.timezone.utc) # 最終更新日時を更新
    await db.commit()
    await db.refresh(db_message)
    return db_message

async def get_messages_for_thread(db: AsyncSession, thread_id: str, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Message)
        .filter(models.Message.thread_id == thread_id)
        .order_by(models.Message.timestamp) # 時系列順
        .offset(skip)
        .limit(limit)
        .options(selectinload(models.Message.sender)) # sender情報も取得
    )
    return result.scalars().all()


# --- Feedback CRUD ---
async def create_feedback(db: AsyncSession, feedback_data: schemas.FeedbackCreate, user_id: int) -> models.Feedback:
    db_feedback = models.Feedback(
        message_id=feedback_data.message_id,
        user_id=user_id, # 認証済みユーザーID
        correct=feedback_data.correct,
        user_comment=feedback_data.user_comment
    )
    db.add(db_feedback)
    await db.commit()
    await db.refresh(db_feedback)
    return db_feedback