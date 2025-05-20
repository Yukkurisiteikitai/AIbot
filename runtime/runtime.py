import asyncio
from typing import Dict, Any
from .config import Config
from .core.llama_handler import LlamaHandler
from .core.person_data_manager import PersonDataManager

class Runtime:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = Config(config_path)
        self.llama = LlamaHandler(self.config.llama_config)
        self.person_data_manager = PersonDataManager()
        
    async def process_message(self, user_id: str, message: str) -> str:
        try:
            # Person Dataの取得
            person_data_token = await self.person_data_manager.get_person_data(user_id)
            
            # レスポンス生成
            response = await self.llama.generate(
                prompt=message,
                person_data_token=person_data_token
            )
            
            return response
            
        except Exception as e:
            # エラーハンドリング
            return f"エラーが発生しました: {str(e)}"
            
    async def run(self):
        # 非同期イベントループの開始
        while True:
            try:
                # メッセージの受信と処理
                # 実際の実装では、メッセージキューやWebSocketなどを使用
                pass
            except Exception as e:
                # エラーハンドリング
                pass