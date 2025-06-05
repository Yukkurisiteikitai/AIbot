# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, TEXT, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON # SQLite用のJSON型 (SQLAlchemy 1.4以降)
from sqlalchemy.sql import func # CURRENT_TIMESTAMPのような関数を使うため

from .db_database import Base

class User(Base):
    __tablename__ = "User"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    threads = relationship("Thread", back_populates="owner")
    feedbacks = relationship("Feedback", back_populates="user")

class Thread(Base):
    __tablename__ = "Thread"

    thread_id = Column(String, primary_key=True, index=True) # 例: "cht_xxxxxxxx"
    owner_user_id = Column(Integer, ForeignKey("User.user_id"), nullable=False)
    mode = Column(String, nullable=False) # "chat" or "search"
    title = Column(String)
    # message_ids: RDBでは直接リストを持つのは推奨されない。Messageテーブルとのリレーションで表現
    tags = Column(JSON)       # list[str] を想定 -> JSON配列として保存
    meta_data = Column(JSON)  # dict を想定 -> JSONオブジェクトとして保存
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="threads")
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(mode.in_(['chat', 'search']), name='mode_check'),
    )

class Message(Base):
    __tablename__ = "Message"

    message_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    thread_id = Column(String, ForeignKey("Thread.thread_id"), nullable=False)
    sender_user_id = Column(Integer, ForeignKey("User.user_id"), nullable=True) # AIの場合はNULL
    role = Column(String, nullable=False) # "system", "user", "assistant", "ai_question"
    context = Column(TEXT, nullable=False)
    feeling = Column(String, nullable=True)
    cache = Column(JSON, nullable=True) # dict
    edit_history = Column(JSON, nullable=True) # list[dict[str, str]] 例: [{"edited_at": "iso_timestamp", "previous_content": "text"}]
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    thread = relationship("Thread", back_populates="messages")
    sender = relationship("User") # Userからのメッセージの場合
    feedbacks = relationship("Feedback", back_populates="message", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(role.in_(['system', 'user', 'assistant', 'ai_question']), name='role_check'),
    )

class Feedback(Base):
    __tablename__ = "Feedback"

    feedback_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    message_id = Column(Integer, ForeignKey("Message.message_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("User.user_id"), nullable=False) # フィードバックを行ったユーザー
    correct = Column(Integer, nullable=False) # -2 ~ 2
    user_comment = Column(TEXT, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    message = relationship("Message", back_populates="feedbacks")
    user = relationship("User", back_populates="feedbacks")

    __table_args__ = (
        CheckConstraint(correct >= -2, name='correct_min_check'),
        CheckConstraint(correct <= 2, name='correct_max_check'),
    )