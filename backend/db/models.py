# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.sql import func

import datetime
# from datetime import datetime 

from .db_database import Base # あなたのBaseクラスのインポートパス
# from deltatime import
# import datetime.datatime

class User(Base):
    __tablename__ = "User"

    id = Column(String, primary_key=True, index=True)
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
     # Episode.user と紐づく
    episodes = relationship("Episode", back_populates="user", cascade="all, delete-orphan")
    # PersonDataEntry.user と紐づく
    person_data_entries = relationship("PersonDataEntry", back_populates="user", cascade="all, delete-orphan")
    # user_question_progress プログレスに結びつく
    user_question_progress = relationship("UserQuestionProgress", back_populates="user", cascade="all, delete-orphan")


class Thread(Base):
    __tablename__ = "Thread"

    # thread_id = Column(String, primary_key=True, index=True)
    # id = Column(String, ForeignKey("Thread.id"), primary_key=True, nullable=False, index=True) # 参照先を修正、index追加
    id = Column(String, primary_key=True, nullable=False, index=True)
    owner_user_id = Column(String, ForeignKey("User.id"), nullable=False, index=True) # index=True を追加
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
    # Episode.thread と紐づく
    episodes = relationship("Episode", back_populates="thread", cascade="all, delete-orphan")


    __table_args__ = (
        CheckConstraint(mode.in_(['chat', 'search']), name='thread_mode_check'), # 制約名を具体的に
    )

class Message(Base):
    __tablename__ = "Message"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    thread_id = Column(String, ForeignKey("Thread.id"), nullable=False, index=True) # index=True を追加
    sender_user_id = Column(String, ForeignKey("User.id"), nullable=True, index=True) # index=True を追加
    role = Column(String, nullable=False)
    context = Column(Text, nullable=False)
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

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    message_id = Column(Integer, ForeignKey("Message.id"), nullable=False, index=True) # index=True を追加
    user_id = Column(String, ForeignKey("User.id"), nullable=False, index=True) # index=True を追加
    correct = Column(Integer, nullable=False)
    user_comment = Column(Text, nullable=True)
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

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(String, ForeignKey("User.id"), nullable=False, index=True) # この質問が誰に向けられたか (FK)
    thread_id  = Column(String, ForeignKey("Thread.id"), nullable=True, index=True) # どのスレッドに関連するか (FK)
    question_text  = Column(String, nullable=False)
    reason_for_question  = Column(String, nullable=True)
    priority  = Column(Integer, default=0, nullable=False)
    status  = Column(String, nullable=False, default='pending')
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    asked_at  = Column(DateTime(timezone=True), nullable=True)
    answered_at  = Column(DateTime(timezone=True), nullable=True)
    related_message_id  = Column(Integer, ForeignKey("Message.id"), nullable=True, index=True) # どのメッセージから派生したか (FK)
    source  = Column(Text, nullable=True)

    # Question -> User (多対一: この質問の対象ユーザー)
    target_user = relationship("User", back_populates="questions_for_this_user", foreign_keys=[user_id])
    # Question -> Thread (多対一: この質問が関連するスレッド)
    thread = relationship("Thread", back_populates="related_questions", foreign_keys=[thread_id])
    # Question -> Message (多対一: この質問が派生した元のメッセージ)
    originating_message = relationship("Message", back_populates="follow_up_questions", foreign_keys=[related_message_id])

    __table_args__ = (
        CheckConstraint(status.in_(['pending', 'asked', 'answered', 'skipped']), name='question_status_check'),
    )

class Episode(Base):
    __tablename__ = "episodes"

    # --- 基本情報 (設計書 Section 2) ---
    
    id = Column(String, primary_key=True, index=True) # episode_id
    thread_id = Column(String, ForeignKey("Thread.id"), nullable=False)
    user_id = Column(String, ForeignKey("User.id"), nullable=False) # ユーザーへのリンクも直接持つと便利
    timestamp = Column(DateTime, default=func.now())
    sequence_in_thread = Column(Integer, nullable=False)
    
    source_type = Column(String, nullable=False)
    author = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    text_content = Column(Text, nullable=False)
    
    # --- AIによる自動解析情報 (JSONで格納) ---
    # PostgreSQLではJSONB型が使われ、効率的にクエリできます。SQLiteではJSONとして扱われます。
    language = Column(String, default="ja", nullable=False)
    emotion_analysis = Column(JSON, nullable=True) # { "primary_emotion": "joy", ... }
    keywords = Column(JSON, nullable=True) # ["keyword1", "keyword2"]
    topics = Column(JSON, nullable=True) # ["topic1", "topic2"]
    named_entities = Column(JSON, nullable=True) # [{ "text": "...", "type": "PERSON" }, ...]
    summarization = Column(JSON, nullable=True) # { "short_summary": "...", "key_points": [...] }

    # --- トラウマ・イベント関連情報 ---
    is_trauma_event = Column(Boolean, default=False)
    trauma_event_details = Column(JSON, nullable=True) # is_trauma_eventがtrueの場合に格納

    # --- ユーザーによる評価・状態管理 ---
    user_importance_rating = Column(String, default="not_set", nullable=True)
    user_labels_or_tags = Column(JSON, nullable=True)
    status = Column(String, default="active", nullable=False)
    sensitivity_level = Column(String, default="medium", nullable=False)

    user_notes = Column(Text)
    last_accessed_by_ai_for_analysis = Column(DateTime)
    last_reviewed_by_user = Column(DateTime)
    
    # --- リレーションシップ ---
    thread = relationship("Thread", back_populates="episodes")
    user = relationship("User", back_populates="episodes")
    
    # PersonDataEntryとの多対多リレーションシップを定義
    # `person_data_links` を通じて関連するPersonDataEntryにアクセスできる
    person_data_entries = relationship(
        "PersonDataEntry",
        secondary="person_data_episode_link", # 関連テーブルの名前
        back_populates="linked_episodes"
    )

# --- ステップ1-3: EpisodeとPersonDataを繋ぐ「関連テーブル」 ---
class PersonDataEpisodeLink(Base):
    __tablename__ = 'person_data_episode_link'
    person_data_entry_id = Column(String, ForeignKey('person_data_entries.id'), primary_key=True)
    episode_id = Column(String, ForeignKey('episodes.id'), primary_key=True)


# --- ステップ1-2: Person Data モデルの作成 ---
# 20個のタグを個別のテーブルにするのは大変なので、汎用的なエントリテーブルとして実装
# 設計書: Person Data フォーマット定義 Ver.1.0

class PersonDataEntry(Base):
    __tablename__ = "person_data_entries"

    id = Column(String, primary_key=True, index=True) # 各エントリの一意なID
    user_id = Column(String, ForeignKey("User.id"), nullable=False)
    
    # --- どのタグに属するかを示す ---
    # 設計書の20個のタグ名をここに格納 (例: "significant_childhood_experiences")
    tag_name = Column(String, nullable=False, index=True) 

    # --- 共通メタ情報 (設計書 Section 3.3.1) ---
    entry_date = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    source = Column(String, nullable=False) # "user_direct_input", "dialogue_extraction", ...
    status = Column(String, default="active", nullable=False)
    sensitivity_level = Column(String, default="medium", nullable=False)
    user_notes = Column(Text)

    # --- 各タグ固有の情報 (JSONで格納) ---
    # 例: `significant_childhood_experiences`なら、ここに`description`, `estimated_event_period`等が入る
    entry_content = Column(JSON, nullable=False)

    # --- リレーションシップ ---
    user = relationship("User", back_populates="person_data_entries")

    # Episodeとの多対多リレーションシップを定義
    # `linked_episodes` を通じてこのエントリの根拠となるEpisodeにアクセスできる
    linked_episodes = relationship(
        "Episode",
        secondary="person_data_episode_link", # 関連テーブルの名前
        back_populates="person_data_entries"
    )

# initの管理用のもの
# 初期化質問管理用の新規モデル
class InitializationQuestion(Base):
    __tablename__ = "initialization_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False) # 表示・処理順を管理
    # category = Column(String, nullable=True) # オプション: 質問カテゴリ (例: "significant_childhood_experiences")
    # sub_type = Column(String, nullable=True) # オプション: カテゴリ内タイプ (例: "A", "B")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ
    user_progress = relationship("UserQuestionProgress", back_populates="init_question")

class UserQuestionProgress(Base):
    __tablename__ = "user_question_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("User.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("initialization_questions.id"), nullable=True, index=True)  # 初期化質問用
    regular_question_id = Column(Integer, ForeignKey("Question.id"), nullable=True, index=True)  # 通常質問用
    
    answer_text = Column(Text, nullable=True)
    ai_evaluation = Column(JSON, nullable=True)  # {state: "pass|fail", feedback: "...", score: 0-100}
    attempt_count = Column(Integer, default=0)
    status = Column(String, default="pending", nullable=False)  # pending, answered, passed, failed
    
    answered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ
    user = relationship("User", back_populates="user_question_progress")
    init_question = relationship("InitializationQuestion", back_populates="user_progress")
    regular_question = relationship("Question")
    
    __table_args__ = (
        CheckConstraint(status.in_(['pending', 'answered', 'passed', 'failed']), name='progress_status_check'),
    )

# AIの評価ログを保存するモデル
class AIEvaluationLog(Base):
    __tablename__ = "ai_evaluation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_progress_id = Column(Integer, ForeignKey("user_question_progress.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    
    ai_response = Column(JSON, nullable=False)  # AI評価の生レスポンス
    evaluation_score = Column(Integer, nullable=False)  # 0-100
    is_passed = Column(Boolean, nullable=False)
    feedback_text = Column(Text, nullable=True)
    follow_up_question = Column(Text, nullable=True)
    
    processing_time_ms = Column(Integer, nullable=True)
    model_version = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())