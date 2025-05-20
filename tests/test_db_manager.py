import pytest
import json
import aiosqlite
import os
import tempfile
import logging
from db_manager import (
    initialize_database,
    add_episode,
    get_episodes,
    update_episode,
    delete_episode
)

# テスト用のロガーを設定
logger = logging.getLogger('test')

@pytest.fixture
def test_db():
    """テスト用のデータベースファイルを作成し、テスト後に削除する"""
    # 一時ディレクトリにデータベースファイルを作成
    temp_dir = os.path.abspath(tempfile.gettempdir())
    db_path = os.path.join(temp_dir, "test_bot_database.db")
    
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Temp directory: {temp_dir}")
    logger.info(f"Database path: {db_path}")
    
    try:
        # データベースを初期化
        logger.info("Initializing database...")
        import asyncio
        asyncio.run(initialize_database(db_path))
        
        # ファイルが実際に作成されたか確認
        if os.path.exists(db_path):
            logger.info(f"Database file exists at: {db_path}")
            logger.info(f"File size: {os.path.getsize(db_path)} bytes")
        else:
            logger.error(f"Database file was not created at: {db_path}")
            raise RuntimeError(f"Database file was not created: {db_path}")
        
        return db_path
        
    except Exception as e:
        logger.error(f"Error in test_db fixture: {e}")
        raise

@pytest.mark.asyncio
async def test_add_episode(test_db):
    """エピソードの追加をテスト"""
    # テスト前にデータベースをクリーンアップ
    async with aiosqlite.connect(test_db) as db:
        await db.execute('DELETE FROM episodes')
        await db.commit()
    
    user_id = 123
    text_content = "テストエピソード"
    author = "user"
    result = await add_episode(
        user_id=user_id,
        text_content=text_content,
        author=author,
        content_type="テスト",
        emotion_analysis_json=json.dumps({"emotion": "happy"}),
        keywords_json=json.dumps(["テスト", "エピソード"]),
        topics_json=json.dumps(["テスト"]),
        named_entities_json=json.dumps([{"text": "テスト", "type": "TEST"}]),
        sensitivity_level="低",
        db_path=test_db
    )
    assert result is not None
    episodes = await get_episodes(user_id, db_path=test_db)
    assert len(episodes) == 1
    assert episodes[0]['text_content'] == text_content

@pytest.mark.asyncio
async def test_get_episodes_with_limit(test_db):
    """エピソードの取得（制限付き）をテスト"""
    # テスト前にデータベースをクリーンアップ
    async with aiosqlite.connect(test_db) as db:
        await db.execute('DELETE FROM episodes')
        await db.commit()
    
    for i in range(5):
        await add_episode(
            user_id=123,
            text_content=f"テストエピソード{i}",
            author="user",
            db_path=test_db
        )
    episodes = await get_episodes(123, limit=3, db_path=test_db)
    assert len(episodes) == 3

@pytest.mark.asyncio
async def test_update_episode(test_db):
    """エピソードの更新をテスト"""
    # テスト前にデータベースをクリーンアップ
    async with aiosqlite.connect(test_db) as db:
        await db.execute('DELETE FROM episodes')
        await db.commit()
    
    await add_episode(
        user_id=123,
        text_content="元のエピソード",
        author="user",
        db_path=test_db
    )
    episodes = await get_episodes(123, db_path=test_db)
    episode_id = episodes[0]['episode_id']
    result = await update_episode(episode_id, text_content="更新後のエピソード", db_path=test_db)
    assert result is True
    episodes = await get_episodes(123, db_path=test_db)
    assert episodes[0]['text_content'] == "更新後のエピソード"

@pytest.mark.asyncio
async def test_delete_episode(test_db):
    """エピソードの削除をテスト"""
    # テスト前にデータベースをクリーンアップ
    async with aiosqlite.connect(test_db) as db:
        await db.execute('DELETE FROM episodes')
        await db.commit()
    
    await add_episode(
        user_id=123,
        text_content="削除するエピソード",
        author="user",
        db_path=test_db
    )
    episodes = await get_episodes(123, db_path=test_db)
    episode_id = episodes[0]['episode_id']
    result = await delete_episode(episode_id, db_path=test_db)
    assert result is True
    episodes = await get_episodes(123, db_path=test_db)
    assert len(episodes) == 0

@pytest.mark.asyncio
async def test_error_handling(test_db):
    """エラーハンドリングをテスト"""
    # テスト前にデータベースをクリーンアップ
    async with aiosqlite.connect(test_db) as db:
        await db.execute('DELETE FROM episodes')
        await db.commit()
    
    # 存在しないエピソードの更新は失敗するはず
    result = await update_episode(99999, text_content="存在しないエピソード", db_path=test_db)
    assert result is False, "存在しないエピソードの更新は失敗するはず"
    
    # 存在しないエピソードの削除は失敗するはず
    result = await delete_episode(99999, db_path=test_db)
    assert result is False, "存在しないエピソードの削除は失敗するはず" 