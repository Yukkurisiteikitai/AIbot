import os
import sys
import pytest
import logging

# ロギングの設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from db_manager import initialize_database

@pytest.fixture
async def test_db():
    """テスト用のデータベースファイルを作成し、テスト後に削除する"""
    # プロジェクトのルートディレクトリにデータベースファイルを作成
    db_path = os.path.join(project_root, "test_bot_database.db")
    logger.debug(f"Database path: {db_path}")
    logger.debug(f"Current working directory: {os.getcwd()}")
    
    try:
        # 既存のファイルを削除
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info(f"Removed existing test database: {db_path}")
        
        # データベースを初期化
        logger.debug("Initializing database...")
        await initialize_database(db_path)
        logger.info(f"Initialized test database: {db_path}")
        
        # ファイルが実際に作成されたか確認
        if not os.path.exists(db_path):
            logger.error(f"Database file was not created at: {db_path}")
            raise RuntimeError(f"Database file was not created: {db_path}")
        
        logger.debug(f"Database file exists: {os.path.exists(db_path)}")
        logger.debug(f"Database file size: {os.path.getsize(db_path) if os.path.exists(db_path) else 'N/A'}")
        
        yield db_path
        
    except Exception as e:
        logger.error(f"Error in test_db fixture: {e}")
        raise
    
    finally:
        # テスト後にファイルを削除
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                logger.info(f"Cleaned up test database: {db_path}")
            except Exception as e:
                logger.error(f"Error cleaning up test database: {e}") 