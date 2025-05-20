# すべてのテストを実行
pytest tests/

# カバレッジレポート付きで実行
pytest --cov=. tests/

# 特定のテストファイルのみ実行
pytest tests/test_episode_handler.py
pytest tests/test_db_manager.py

# 特定のテスト関数のみ実行
pytest tests/test_episode_handler.py::test_process_conversation_message_basic