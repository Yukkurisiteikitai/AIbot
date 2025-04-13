# db_manager.py
import aiosqlite
import logging

DATABASE = 'bot_database.db'
logger = logging.getLogger('discord') # discord.pyのロガーを使う

async def initialize_database():
    """データベースを初期化し、必要なテーブルを作成する"""
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_info (
                user_id INTEGER NOT NULL,
                info_type TEXT NOT NULL,
                content TEXT NOT NULL,
                PRIMARY KEY (user_id, info_type)
            )
        ''')
        await db.commit()
        logger.info("Database initialized.")

async def add_user_info(user_id: int, info_type: str, content: str):
    """ユーザー情報を追加または更新する"""
    async with aiosqlite.connect(DATABASE) as db:
        try:
            await db.execute('''
                INSERT INTO user_info (user_id, info_type, content)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, info_type) DO UPDATE SET content = excluded.content
            ''', (user_id, info_type, content))
            await db.commit()
            logger.info(f"Added/Updated info for user {user_id}: type='{info_type}'")
            return True
        except Exception as e:
            logger.error(f"Error adding/updating user info for {user_id}: {e}")
            return False

async def get_user_info(user_id: int) -> dict:
    """特定のユーザーのすべての情報を取得する"""
    user_data = {}
    async with aiosqlite.connect(DATABASE) as db:
        try:
            async with db.execute('SELECT info_type, content FROM user_info WHERE user_id = ?', (user_id,)) as cursor:
                async for row in cursor:
                    user_data[row[0]] = row[1]
            logger.debug(f"Retrieved info for user {user_id}: {user_data}")
            return user_data
        except Exception as e:
            logger.error(f"Error getting user info for {user_id}: {e}")
            return {} # エラー時は空辞書を返す

async def delete_user_info(user_id: int):
    """特定のユーザーのすべての情報を削除する"""
    async with aiosqlite.connect(DATABASE) as db:
        try:
            await db.execute('DELETE FROM user_info WHERE user_id = ?', (user_id,))
            await db.commit()
            logger.info(f"Deleted all info for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user info for {user_id}: {e}")
            return False

async def get_specific_user_info(user_id: int, info_type: str) -> str | None:
    """特定のユーザーの特定のタイプの情報を取得する"""
    async with aiosqlite.connect(DATABASE) as db:
        try:
            async with db.execute('SELECT content FROM user_info WHERE user_id = ? AND info_type = ?', (user_id, info_type)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"Error getting specific info for user {user_id}, type {info_type}: {e}")
            return None