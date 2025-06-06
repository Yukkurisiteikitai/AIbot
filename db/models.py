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

class Question(Base):
    __tablename__ = "Question"

    question_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    thread_id  = Column(String, ForeignKey=("Question.question_id"), nullable=True) # - この質問が特定の会話スレッドに関連している場合。汎用的な質問の場合はNULLでも良いかもしれません。
    question_text  = Column(String, nullable=False) # - AIがユーザーに投げかける質問の本文。（`need_question` に相当）
    reason_for_question  = Column(String, nullable=False)#` - なぜこの質問をするのかの理由や背景（AI内部用、デバッグ用）。（`why_question` に相当）
    priority  = Column(Integer, default=0, nullable=False)#` - 質問の優先度。数値が高いほど優先度が高いなど、ルールを決めます。（`need_level` のアイデア）
    status  = Column(String, nullable=False, default='pending')#  CHECK(status IN ('pending', 'asked', 'answered', 'skipped'))#` - 質問の状態。
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    # *   `pending`: 質問が生成されたが、まだユーザーに提示されていない。
    # *   `asked`: ユーザーに提示されたが、まだ回答されていない。
    # *   `answered`: ユーザーが回答した。
    # *   `skipped`: ユーザーがスキップした、またはシステムが何らかの理由で提示を取りやめた。
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    asked_at  = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    answered_at  = Column(DateTime(timezone=True), nullable=True, server_default=func.now())#DATETIME, NULLABLE` - ユーザーがこの質問に回答した日時。
    related_message_id  = Column(Integer,ForeignKey=("Message.message_id"),nullable=True)# REFERENCES Message (message_id), NULLABLE)#` - この質問が、ユーザーの特定のメッセージへの応答として生成された場合、そのメッセージのID。
    source  = Column(TEXT, nullable=True)#` - この質問が生成された元（例: "episode_analysis", "feedback_trigger", "initial_questions"など）。
    __table_args__ = (
        CheckConstraint(status.in_(['pending', 'asked', 'answered', 'skipped']), name='status_check')
    )
