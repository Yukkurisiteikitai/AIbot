from llama_cpp import Llama
from typing import Dict, Any, Optional
import asyncio
import logging
# import asyncio
#  --- JSON抽出のための正規表現ライブラリをインポート ---
import re # select_relevant_tags 関数内で必要になるため、ここでも import しておくか、関数の上に移動
from pathlib import Path
from typing import Dict, Any
import yaml

class LlamaHandler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        print(config.model_path)
        self.llm = Llama(
            model_path=str(config.model_path),
            n_ctx=config['n_ctx'],
            n_batch=config['n_batch'],
            n_threads=config['n_threads'],
            n_gpu_layers=config.get('n_gpu_layers', 0)
        )
        self.logger = logging.getLogger(__name__)
        
    async def generate(
        self,
        prompt: str,
        person_data_token: str,
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> str:
        try:
            # トークン化されたPerson Dataを含むプロンプトを構築
            full_prompt = self._build_prompt(prompt, person_data_token)
            
            # 非同期で生成を実行
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.llm(
                    full_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=["</s>", "Human:", "Assistant:"]
                )
            )
            
            return response['choices'][0]['text']
            
        except Exception as e:
            self.logger.error(f"Generation error: {e}")
            raise
            
    def _build_prompt(self, prompt: str, person_data_token: str) -> str:
        return f"""<s>[INST] <<SYS>>
You are an AI assistant with access to the user's personal data (token: {person_data_token}).
Use this information to provide personalized responses.
<</SYS>>

{prompt} [/INST]"""


# testCode ------------------------------------
class Config:
    def __init__(self, config_path: str = "/Users/yuuto/Desktop/nowProject/AIbot/config.yaml"):
        self.config_path = config_path
        self.config: Dict[str, Any] = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    @property
    def model_path(self) -> Path:
        print(self.config['llama']['model_path'])
        return Path(self.config['llama']['model_path'])
        
    @property
    def llama_config(self) -> Dict[str, Any]:
        return self.config['llama']['runtime_config']

class Runtime:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = Config(config_path=config_path)
        self.llama = LlamaHandler(self.config.llama_config)
        # self.person_data_manager = PersonDataManager()
        
    async def process_message(self, user_id: str, message: str) -> str:
        try:
            # Person Dataの取得
            # person_data_token = await self.person_data_manager.get_person_data(user_id)
            
            # レスポンス生成
            response = await self.llama.generate(
                prompt=message,
                person_data_token="human"
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


# test
if __name__ == "__main__":
    CONF_PATH = "/Users/yuuto/Desktop/nowProject/AIbot/config.yaml"


    # check for yaml to dict?
    with open(CONF_PATH, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
    print(type(data))

    ai_run = Runtime(config_path=CONF_PATH)
    print(ai_run.process_message(user_id="helo",message="人間とはどのようなものだと認識されているのだい"))
