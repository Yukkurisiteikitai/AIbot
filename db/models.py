# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, TEXT, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.sql import func

from .db_database import Base # あなたのBaseクラスのインポートパス

class User(Base):
    __tablename__ = "User"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=True) # nameもnullable=Trueの可能性あり
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # User -> Thread (一対多: ユーザーは複数のスレッドを持てる)
    threads = relationship("Thread", back_populates="owner", cascade="all, delete-orphan")
    # User -> Feedback (一対多: ユーザーは複数のフィードバックを行える)
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    # User -> Question (一対多: ユーザーは複数の質問を割り当てられる)
    questions_for_this_user = relationship("Question", back_populates="target_user", foreign_keys="[Question.user_id]", cascade="all, delete-orphan")
    # User -> Message (一対多: ユーザーは複数のメッセージを送信できる。sender_user_id経由)
    sent_messages = relationship("Message", back_populates="sender", foreign_keys="[Message.sender_user_id]", cascade="all, delete-orphan")


class Thread(Base):
    __tablename__ = "Thread"

    thread_id = Column(String, primary_key=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("User.user_id"), nullable=False, index=True) # index=True を追加
    mode = Column(String, nullable=False)
    title = Column(String, nullable=True) # titleもnullable=Trueの可能性あり
    tags = Column(JSON, nullable=True)
    meta_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now()) # created_at と同じ役割なら統一を検討

    # Thread -> User (多対一: スレッドの所有者)
    owner = relationship("User", back_populates="threads")
    # Thread -> Message (一対多: スレッドは複数のメッセージを持つ)
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")
    # Thread -> Question (一対多: スレッドは複数の質問に関連付けられる)
    related_questions = relationship("Question", back_populates="thread", foreign_keys="[Question.thread_id]", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(mode.in_(['chat', 'search']), name='thread_mode_check'), # 制約名を具体的に
    )

class Message(Base):
    __tablename__ = "Message"

    message_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    thread_id = Column(String, ForeignKey("Thread.thread_id"), nullable=False, index=True) # index=True を追加
    sender_user_id = Column(Integer, ForeignKey("User.user_id"), nullable=True, index=True) # index=True を追加
    role = Column(String, nullable=False)
    context = Column(TEXT, nullable=False)
    feeling = Column(String, nullable=True)
    cache = Column(JSON, nullable=True)
    edit_history = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Message -> Thread (多対一: メッセージが属するスレッド)
    thread = relationship("Thread", back_populates="messages")
    # Message -> User (多対一: メッセージの送信者)
    sender = relationship("User", back_populates="sent_messages", foreign_keys=[sender_user_id]) # foreign_keys を明示
    # Message -> Feedback (一対多: メッセージは複数のフィードバックを持てる)
    feedbacks = relationship("Feedback", back_populates="message", cascade="all, delete-orphan")
    # Message -> Question (一対多: メッセージは複数のフォローアップ質問をトリガーできる)
    follow_up_questions = relationship("Question", back_populates="originating_message", foreign_keys="[Question.related_message_id]", cascade="all, delete-orphan")


    __table_args__ = (
        CheckConstraint(role.in_(['system', 'user', 'assistant', 'ai_question']), name='message_role_check'), # 制約名を具体的に
    )

class Feedback(Base):
    __tablename__ = "Feedback"

    feedback_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    message_id = Column(Integer, ForeignKey("Message.message_id"), nullable=False, index=True) # index=True を追加
    user_id = Column(Integer, ForeignKey("User.user_id"), nullable=False, index=True) # index=True を追加
    correct = Column(Integer, nullable=False)
    user_comment = Column(TEXT, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Feedback -> Message (多対一: フィードバック対象のメッセージ)
    message = relationship("Message", back_populates="feedbacks")
    # Feedback -> User (多対一: フィードバックを行ったユーザー)
    user = relationship("User", back_populates="feedbacks")

    __table_args__ = (
        CheckConstraint(correct >= -2, name='feedback_correct_min_check'), # 制約名を具体的に
        CheckConstraint(correct <= 2, name='feedback_correct_max_check'), # 制約名を具体的に
    )

class Question(Base):
    __tablename__ = "Question"

    question_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("User.user_id"), nullable=False, index=True) # この質問が誰に向けられたか (FK)
    thread_id  = Column(String, ForeignKey("Thread.thread_id"), nullable=True, index=True) # どのスレッドに関連するか (FK)
    question_text  = Column(String, nullable=False)
    reason_for_question  = Column(String, nullable=True)
    priority  = Column(Integer, default=0, nullable=False)
    status  = Column(String, nullable=False, default='pending')
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    asked_at  = Column(DateTime(timezone=True), nullable=True)
    answered_at  = Column(DateTime(timezone=True), nullable=True)
    related_message_id  = Column(Integer, ForeignKey("Message.message_id"), nullable=True, index=True) # どのメッセージから派生したか (FK)
    source  = Column(TEXT, nullable=True)

    # Question -> User (多対一: この質問の対象ユーザー)
    target_user = relationship("User", back_populates="questions_for_this_user", foreign_keys=[user_id])
    # Question -> Thread (多対一: この質問が関連するスレッド)
    thread = relationship("Thread", back_populates="related_questions", foreign_keys=[thread_id])
    # Question -> Message (多対一: この質問が派生した元のメッセージ)
    originating_message = relationship("Message", back_populates="follow_up_questions", foreign_keys=[related_message_id])

    __table_args__ = (
        CheckConstraint(status.in_(['pending', 'asked', 'answered', 'skipped']), name='question_status_check'),
    )