# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select # SQLAlchemy 1.4以降の非同期select
from sqlalchemy.orm import selectinload # リレーションを効率的にロードするため

from . import models, schemas
from typing import Optional
import uuid # thread_id生成用など
import datetime
from typing import Optional,List 


# Config
request_db_contexts_limit = 100 


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


    result = await db.execute(
        select(models.Thread)
        .options(selectinload(models.Thread.messages)) # messages を事前にロード
        .filter(models.Thread.thread_id == db_thread.thread_id)
    )
    loaded_thread = result.scalars().first()
    return loaded_thread if loaded_thread else db_thread # loaded_thread が取得できればそれを使う    


async def get_thread(db: AsyncSession, thread_id: str, include_messages: bool = False):
    query = select(models.Thread).filter(models.Thread.thread_id == thread_id)
    if include_messages:
        # N+1問題を避けるためにselectinloadを使う
        query = query.options(
            selectinload(models.Thread.messages).options(
                    selectinload(models.Message.sender)
                    )
                )
    result = await db.execute(query)
    return result.scalars().first()

async def get_user_threads(db: AsyncSession, user_id: int, skip: int = 0, limit: int = request_db_contexts_limit):
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

async def get_messages_for_thread(db: AsyncSession, thread_id: str, skip: int = 0, limit: int = request_db_contexts_limit):
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


import random
import datetime
async def create_question(
    db: AsyncSession,
    question_text: str,
    user_id: int, # 必須と仮定
    why_question: Optional[str] = None, # オプショナルと仮定
    thread_id: Optional[str] = None, # オプショナルと仮定
    priority: int = 0,
    status: str = 'pending',
    source: Optional[str] = None,
    related_message_id: Optional[int] = None
) -> models.Question:
    db_question = models.Question(
        user_id=user_id,
        thread_id=thread_id,
        question_text=question_text,
        reason_for_question=why_question,
        priority=priority,
        status=status,
        source=source,
        related_message_id=related_message_id
        # question_id は自動採番
        # created_at はDBデフォルト
        # asked_at, answered_at は最初はNone
    )
    db.add(db_question)
    await db.commit()
    await db.refresh(db_question)
    return db_question



async def get_questions_for_user_id(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None # 特定のステータスの質問のみを取得する場合
) -> List[models.Question]:
    query = select(models.Question).filter(models.Question.user_id == user_id)
    if status:
        query = query.filter(models.Question.status == status)
    query = query.order_by(models.Question.priority.desc(), models.Question.created_at.asc()) # 例: 優先度高い順、作成日古い順
    query = query.offset(skip).limit(limit)
    # もしリレーションシップをロードするなら
    # query = query.options(selectinload(models.Question.user), selectinload(models.Question.thread))
    result = await db.execute(query)
    return result.scalars().all()


async def get_question_for_question_id(db: AsyncSession, question_id: int, skip: int = 0, limit: int = request_db_contexts_limit):
    result = await db.execute(
        select(models.Question)
        .filter(models.Question.question_id == question_id)
        .order_by(models.Message.timestamp) # 時系列順
        .offset(skip)
        .limit(limit)
        # .options(selectinload(models.Question.sender)) # sender情報も取得
    )
    return result.scalars().all()


# idではなく番号で呼ばれるような気がしなくもない

async def get_question_for_feedback(db: AsyncSession, q_context: str, skip: int = 0, limit: int = request_db_contexts_limit):
    result = await db.execute(
        select(models.Question)
        .filter(models.Question.question_text == q_context)
        .order_by(models.Message.timestamp) # 時系列順
        .offset(skip)
        .limit(limit)
        # .options(selectinload(models.Question.sender)) # sender情報も取得
    )
    return result.scalars().all()


async def update_question_status( # ★★★ この関数 ★★★
    db: AsyncSession,
    question_id: int,
    new_status: str,
    set_asked_at: bool = False,
    set_answered_at: bool = False,
    user_id_check: Optional[int] = None
) -> Optional[models.Question]:
    query = select(models.Question).filter(models.Question.question_id == question_id)
    if user_id_check is not None:
        query = query.filter(models.Question.user_id == user_id_check)

    result = await db.execute(query)
    db_question = result.scalars().first()

    if not db_question:
        return None

    db_question.status = new_status
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    if set_asked_at:
        db_question.asked_at = now_utc
    if set_answered_at:
        db_question.answered_at = now_utc

    await db.commit()
    await db.refresh(db_question)
    return db_question


# --- User CRUD ---

# (オプション) パスワードハッシュ化のための設定
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    result = await db.execute(select(models.User).filter(models.User.user_id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.User]:
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User:
    # ★★★ パスワードをハッシュ化する処理をここに入れる ★★★
    # hashed_password = get_password_hash(user.password) # passlib を使う場合
    hashed_password = user.password + "_hashed" # 仮のハッシュ化 (実際には上記のようなライブラリを使う)

    db_user = models.User(
        email=user.email,
        name=user.name,
        password_hash=hashed_password # ハッシュ化されたパスワードを保存
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user(db: AsyncSession, user_id: int, user_update_data: schemas.UserUpdate) -> Optional[models.User]:
    result = await db.execute(select(models.User).filter(models.User.user_id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        return None

    update_data = user_update_data.model_dump(exclude_unset=True) # Pydantic V2, 未設定のフィールドは除外
    for key, value in update_data.items():
        setattr(db_user, key, value)

    # updated_at はモデル定義で onupdate=func.now() があれば自動更新されるが、
    # 明示的に更新したい場合はここで設定
    # db_user.updated_at = datetime.datetime.now(datetime.timezone.utc)

    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    result = await db.execute(select(models.User).filter(models.User.user_id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        return None
    await db.delete(db_user)
    await db.commit()
    return db_user # 削除されたユーザーオブジェクトを返す (確認用)