import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from episode_handler import EpisodeHandler
from llm_analyzer import LLMAnalyzer

# モック用のLLMアナライザー
class MockLLMAnalyzer:
    def __init__(self):
        self.responses = {
            'when': '昨日の午後',
            'where': '近所の公園',
            'who': '友達と',
            'what': '写真を撮った',
            'how': '楽しく'
        }

    async def _call_llm_api(self, prompt: str) -> str:
        if '時間情報' in prompt:
            return self.responses['when']
        elif '場所情報' in prompt:
            return self.responses['where']
        elif '人物情報' in prompt:
            return self.responses['who']
        elif '出来事の内容' in prompt:
            return self.responses['what']
        elif '方法や状況' in prompt:
            return self.responses['how']
        return ''

    async def analyze_content_type(self, text: str) -> str:
        return '過去の出来事の回想'

    async def analyze_emotions(self, text: str) -> dict:
        return {
            'emotions': {'happy': 0.8},
            'polarity': 'positive'
        }

    async def extract_keywords(self, text: str) -> list:
        return ['公園', '写真', '友達']

    async def identify_topics(self, text: str) -> list:
        return ['レジャー', '思い出']

    async def extract_named_entities(self, text: str) -> list:
        return [
            {'text': '公園', 'type': 'LOCATION'},
            {'text': '友達', 'type': 'PERSON'}
        ]

    async def assess_sensitivity(self, text: str) -> str:
        return '低'

@pytest.fixture
def mock_llm_analyzer():
    return MockLLMAnalyzer()

@pytest.fixture
def episode_handler(mock_llm_analyzer):
    return EpisodeHandler(mock_llm_analyzer)

@pytest.mark.asyncio
async def test_process_conversation_message_basic(episode_handler, monkeypatch):
    """基本的な会話メッセージの処理をテスト"""
    # データベースのモック
    mock_add_episode = AsyncMock(return_value=1)  # episode_idを返す
    mock_update_episode = AsyncMock(return_value=True)
    monkeypatch.setattr('db_manager.add_episode', mock_add_episode)
    monkeypatch.setattr('db_manager.update_episode', mock_update_episode)

    # 最初のメッセージ
    result = await episode_handler.process_conversation_message(
        user_id=123,
        role="user",
        content="昨日、近所の公園に行きました"
    )
    assert result is True
    assert 123 in episode_handler.active_episodes

    # 2番目のメッセージ
    result = await episode_handler.process_conversation_message(
        user_id=123,
        role="user",
        content="友達と一緒に写真を撮りました"
    )
    assert result is True
    assert 123 in episode_handler.active_episodes

    # 会話を終了するメッセージ
    result = await episode_handler.process_conversation_message(
        user_id=123,
        role="user",
        content="とても楽しかったです。ありがとう"
    )
    assert result is True
    assert 123 not in episode_handler.active_episodes

@pytest.mark.asyncio
async def test_short_acknowledgement(episode_handler):
    """短い相槌の処理をテスト"""
    result = await episode_handler.process_conversation_message(
        user_id=123,
        role="user",
        content="はい"
    )
    assert result is True
    assert 123 not in episode_handler.active_episodes

@pytest.mark.asyncio
async def test_empty_message(episode_handler):
    """空のメッセージの処理をテスト"""
    result = await episode_handler.process_conversation_message(
        user_id=123,
        role="user",
        content=""
    )
    assert result is True
    assert 123 not in episode_handler.active_episodes

@pytest.mark.asyncio
async def test_episode_completion_by_timeout(episode_handler, monkeypatch):
    """タイムアウトによるエピソードの完了をテスト"""
    # データベースのモック
    mock_add_episode = AsyncMock(return_value=1)  # episode_idを返す
    mock_update_episode = AsyncMock(return_value=True)
    monkeypatch.setattr('db_manager.add_episode', mock_add_episode)
    monkeypatch.setattr('db_manager.update_episode', mock_update_episode)

    # 最初のメッセージ
    await episode_handler.process_conversation_message(
        user_id=123,
        role="user",
        content="昨日、近所の公園に行きました"
    )
    
    # エピソードの最終更新時間を5分以上前に設定
    episode = episode_handler.active_episodes[123]
    episode['last_update'] = (datetime.now().timestamp() - 360).isoformat()
    
    # 新しいメッセージを処理
    result = await episode_handler.process_conversation_message(
        user_id=123,
        role="user",
        content="友達と一緒に写真を撮りました"
    )
    
    assert result is True
    assert 123 not in episode_handler.active_episodes

@pytest.mark.asyncio
async def test_episode_info_extraction(episode_handler, monkeypatch):
    """エピソード情報の抽出をテスト"""
    # データベースのモック
    mock_add_episode = AsyncMock(return_value=1)  # episode_idを返す
    mock_update_episode = AsyncMock(return_value=True)
    monkeypatch.setattr('db_manager.add_episode', mock_add_episode)
    monkeypatch.setattr('db_manager.update_episode', mock_update_episode)

    # 情報を含むメッセージを処理
    await episode_handler.process_conversation_message(
        user_id=123,
        role="user",
        content="昨日、近所の公園で友達と写真を撮りました。とても楽しかったです。"
    )
    
    episode = episode_handler.active_episodes[123]
    assert 'when' in episode['collected_info']
    assert 'where' in episode['collected_info']
    assert 'who' in episode['collected_info']
    assert 'what' in episode['collected_info']
    assert 'how' in episode['collected_info']

@pytest.mark.asyncio
async def test_episode_save_with_db_manager(episode_handler, monkeypatch):
    """データベースへの保存をテスト"""
    # モックのデータベースマネージャー
    mock_add_episode = AsyncMock(return_value=1)  # episode_idを返す
    mock_update_episode = AsyncMock(return_value=True)
    
    monkeypatch.setattr('db_manager.add_episode', mock_add_episode)
    monkeypatch.setattr('db_manager.update_episode', mock_update_episode)
    
    # エピソードを完了させる
    await episode_handler.process_conversation_message(
        user_id=123,
        role="user",
        content="昨日、近所の公園で友達と写真を撮りました。"
    )
    await episode_handler.process_conversation_message(
        user_id=123,
        role="user",
        content="とても楽しかったです。ありがとう"
    )
    
    # データベースへの保存が呼ばれたことを確認
    assert mock_add_episode.called
    assert mock_update_episode.called

@pytest.mark.asyncio
async def test_error_handling(episode_handler, monkeypatch):
    """エラーハンドリングをテスト"""
    # データベースエラーをシミュレート
    mock_add_episode = AsyncMock(side_effect=Exception("Database error"))
    monkeypatch.setattr('db_manager.add_episode', mock_add_episode)
    
    result = await episode_handler.process_conversation_message(
        user_id=123,
        role="user",
        content="テストメッセージ"
    )
    
    assert result is False 