import asyncio
from typing import Dict, Any
from .config import Config
from .core.llm_handler import LlamaHandler
from .core.person_data_manager import PersonDataManager
import logging
import asyncio

# Runtime クラスの修正
class Runtime:
    def __init__(self, config_path: str = "config.yaml"):
        # logging の設定は main_test_run で行うか、ここに集約
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        try:
            self.config_loader = Config(config_path=config_path)
            # 修正: LlamaHandler に model_path を含む設定を渡す
            self.llama = LlamaHandler(self.config_loader.llama_handler_config) # 修正されたプロパティを使用
            self.logger.info("Runtime initialized successfully.")
        except Exception as e:
            self.logger.error(f"Error during Runtime initialization: {e}", exc_info=True)
            raise

        
    async def process_message(self, user_id: int, message: str) -> str:
        try:
            # Person Dataの取得
            # person_data_token = await self.person_data_manager.get_person_data(user_id)
            
            # レスポンス生成
            response = await self.llama.generate_simple(
                prompt=message
            )
            
            return response
            
        except Exception as e:
            # エラーハンドリング
            return f"エラーが発生しました: {str(e)}"
    

    async def simpleAnswer(self, user_id: str, message: str) -> str:
        try:
            # Person Dataの取得
            # person_data_token = await self.person_data_manager.get_person_data(user_id)
            
            # レスポンス生成
            response = await self.llama.generate(
                prompt=message,
                person_data_token= [2, 76444, 120211, 237048, 67923, 73727, 237536]
            )
            
            return response
            
        except Exception as e:
            # エラーハンドリング
            logging.error(f"Error in simpleAnswer: {e}", exc_info=True)
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

    async def main_test_run(self,conf_path: str = "config.yaml"):
            
            self.logger.info("Starting main_test_run...")
            try:
                # Runtimeの初期化時に config_path を渡す
                ai_runtime = Runtime(config_path=conf_path)
                user_message = "人間とはどのようなものだと認識されているのだい" # テストしたいメッセージ
                self.logger.info(f"Sending message to AI: '{user_message}'")

                tokenS = ai_runtime.llama._decode_prompt(user_message,False)
                print(f"tokenS:{tokenS}")

                # process_message を await で呼び出す
                response = await ai_runtime.process_message(user_id="test_user_id", message=user_message)

                print("-" * 30)
                print("AIの応答:")
                print(response)
                print("-" * 30)

            except FileNotFoundError as e:
                self.logger.error(f"Configuration file error: {e}")
                print(f"設定ファイルが見つかりません: {e}")
            except KeyError as e:
                self.logger.error(f"Configuration key error: {e} - config.yamlの構造を確認してください。")
                print(f"設定ファイルのキーエラー: {e} - config.yamlの構造を確認してください。")
            except Exception as e:
                self.logger.error(f"An unexpected error occurred in main_test_run: {e}", exc_info=True)
                print(f"予期せぬエラーが発生しました: {e}")



# # test
# if __name__ == "__main__":
#     # loggingの基本設定 (既にあれば不要)
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     logger = logging.getLogger(__name__) # このスクリプト自体のロガー

#     CONF_PATH = "/Users/yuuto/Desktop/nowProject/AIbot/config.yaml" # ご自身の環境に合わせてください
#     asyncio.run(main_test_run())