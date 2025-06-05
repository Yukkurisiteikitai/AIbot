# db_manager.py
import aiosqlite
import logging
import datetime
from utils.log import LogSystem # これはあなたのカスタムログシステムですね

DATABASE = 'bot_database.db'
log_sys = LogSystem(__name__, module_name='ai_covertions')

async def initialize_database():
    """データベースを初期化し、必要なテーブルを作成する"""
    async with aiosqlite.connect(DATABASE) as db:
        # ユーザー情報を保存するテーブル
        # Userテーブルとして再定義 (以前の会話のUserテーブル定義を参考にしています)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS User (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        log_sys.log_with_context(level="info", message="Table 'User' checked/created.")

        # Threadテーブル (以前の会話のThreadテーブル定義を参考)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Thread (
                thread_id TEXT PRIMARY KEY,
                owner_user_id INTEGER NOT NULL,
                mode TEXT NOT NULL CHECK(mode IN ('chat', 'search')),
                title TEXT,
                message_ids TEXT, -- JSON array of message_ids (if you stick to this)
                tags TEXT,       -- JSON array of strings
                meta_data TEXT,  -- JSON object
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_user_id) REFERENCES User (user_id)
            )
        ''')
        log_sys.log_with_context(level="info", message="Table 'Thread' checked/created.")

        # Messageテーブル (以前の Chat_Thread を改名・修正)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Message (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                sender_user_id INTEGER, -- ユーザーからのメッセージの場合。AIの場合はNULLなど
                role TEXT NOT NULL CHECK(role IN ('system', 'user', 'assistant', 'ai_question')),
                context TEXT NOT NULL,
                feeling TEXT,
                cache TEXT,        -- JSON object
                edit_history TEXT, -- ここに編集履歴をJSON文字列として保存
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (thread_id) REFERENCES Thread (thread_id),
                FOREIGN KEY (sender_user_id) REFERENCES User (user_id)
            )
        ''')
        log_sys.log_with_context(level="info", message="Table 'Message' checked/created.")

        # Feedbackテーブル (以前の会話のFeedbackテーブル定義を参考)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL, -- フィードバックを行ったユーザー
                correct INTEGER NOT NULL CHECK(correct >= -2 AND correct <= 2),
                user_comment TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES Message (message_id),
                FOREIGN KEY (user_id) REFERENCES User (user_id)
            )
        ''')
        log_sys.log_with_context(level="info", message="Table 'Feedback' checked/created.")

        # Messageテーブルのインデックス (user_idではなくthread_idとtimestampが良いでしょう)
        await db.execute('''
            CREATE INDEX IF NOT EXISTS idx_message_thread_id_timestamp
            ON Message (thread_id, timestamp)
        ''')
        # owner_user_id にもインデックスがあると良いかもしれません
        await db.execute('''
            CREATE INDEX IF NOT EXISTS idx_thread_owner_user_id
            ON Thread (owner_user_id)
        ''')

        await db.commit()
        log_sys.log_with_context(level="info", message="Database initialization complete.")
