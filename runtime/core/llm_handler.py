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
        print(self.config)
        self.llm = Llama(
            model_path=str(config['model_path']),
            n_ctx=config['n_ctx'],
            n_batch=config['n_batch'],
            n_threads=config['n_threads'],
            n_gpu_layers=config.get('n_gpu_layers', 0)
        )
        self.logger = logging.getLogger(__name__)
        
    async def generate(
        self,
        prompt: str,
        person_data_token: list,
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> str:
        try:
            # トークン化されたPerson Dataを含むプロンプトを構築
            full_prompt = self._build_prompt(prompt, person_data_token)
            print(f"full_prpmpt:{full_prompt}")#test
            # これなんか知らないけどデコードの処理がうまくいってない?
            print(f"==== TEST =====\n\nHelllifieo;jf;oawjfeio;jfo;:{self.llm.detokenize(full_prompt).decode('utf-8', errors='replace')}\n\n ==== =====")

            # 絶対にここでToken化して処理を行うように整理していないからだろ
            
            # 非同期で生成を実行
            # loop = asyncio.get_event_loop()
            # おそらくtokenでの反映をしていないのでllama.cppでの応答ができるようにそこを調節する
            # response = await loop.run_in_executor(
            #     None,
            #     lambda: self.llm(
            #         full_prompt,
            #         max_tokens=max_tokens,
            #         temperature=temperature,
            #         stop=["</s>", "Human:", "Assistant:"]
            #     )
            # )
            print(f"プロンプトトークンを評価中...")
            self.llm.eval(full_prompt)
            print(f"プロンプトトークンの評価完了。")

            # 生成するトークンの最大数
            max_new_tokens = 512
            generated_tokens = []

            print(f"\n次の{max_new_tokens}個のトークンを生成します:")
            for i in range(max_new_tokens):
                # 次のトークンをサンプリング (最も基本的なサンプリング)
                # temperatureなどのサンプリングパラメータは Llama オブジェクト初期化時や、
                # より高度なサンプリングメソッド (llm.sample_*) で指定できます。
                # ここでは、Llamaオブジェクトに設定されたデフォルトのサンプリング設定が使われます。
                # (明示的に設定したい場合は、Llamaインスタンス作成時に temp, top_k, top_p などを指定するか、
                #  llama_cpp.llama_sample* 関数群を直接利用します)
                next_token = self.llm.sample(temp=0.7) # 例: 温度を0.7に設定してサンプリング

                # EOS (End of Sequence) トークンが出たら生成を終了
                if next_token == self.llm.token_eos():
                    print("  EOSトークンが生成されたため、終了します。")
                    break

                generated_tokens.append(next_token)
                print(f"  生成されたトークンID [{i+1}]: {next_token}")

                # 新しく生成されたトークンをモデルに評価させる (次の予測のため)
                # 1トークンずつ評価する場合は、[next_token] のようにリストで渡します
                self.llm.eval([next_token])

            print(f"\n生成されたトークンIDのシーケンス: {generated_tokens}")


            # --- 3. トークンをテキストにデコード ---
            print("\n--- デコード処理 ---")
            if generated_tokens:
                # detokenizeメソッドはバイト列を返すので、.decode('utf-8') が必要
                # errors='replace' はデコードできない文字があった場合に代替文字に置き換えます
                decoded_text = self.llm.detokenize(generated_tokens).decode('utf-8', errors='replace')
                print(f"デコードされたテキスト: {decoded_text}")
            else:
                print("デコードするトークンがありません。")
            
            return decoded_text
            
        except Exception as e:
            self.logger.error(f"Generation error: {e}")
            raise
            
    def _decode_prompt(self, text: str,ADD_bos:bool) -> list:
        return self.llm.tokenize(text.encode('utf-8'), add_bos=ADD_bos)


    def _build_prompt(self, prompt: str, person_data_token: list) -> list:
        prompt_tokens = self._decode_prompt(text= f"""<s>[INST] <<SYS>>
    You are an AI assistant with access to the user's personal data (token: 
    """,ADD_bos=True)
        prompt_tokens.extend(person_data_token)
        # prompt_tokens = self.llm.tokenize(user_question.encode('utf-8'), add_bos=True)
        prompt_tokens.extend(
            self._decode_prompt(text=f""").
    Use this information to provide personalized responses.
    <</SYS>>

    {prompt} [/INST]""",ADD_bos=False)
        )
        return prompt_tokens



# testCode ------------------------------------
# Config クラスの修正
class Config:
    def __init__(self, config_path: str = "/Users/yuuto/Desktop/nowProject/AIbot/config.yaml"):
        self.config_path = Path(config_path) # Pathオブジェクトとして扱う
        if not self.config_path.is_file():
            # self.config が初期化される前にエラーを出す可能性があるので logging はここでは使わない
            print(f"ERROR: Config file not found: {self.config_path}")
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        self._config_data: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @property
    def model_path_str(self) -> str: # 文字列で返すように変更
        try:
            # config.yaml 内の実際の model_path の場所に合わせて調整してください
            # 例: self._config_data['llama']['model_path']
            # 現在のコードの llama_config プロパティで参照している runtime_config 内に model_path があると仮定
            # もし config.yaml の llama.model_path にあるならそちらを参照
            # ここでは、config.yaml の 'llama'.'runtime_config'.'model_path' にあると仮定して取得します
            # 実際のYAML構造に合わせてください。
            # 前回のログから、config.yamlの'llama'.'runtime_config'.'model_path'にパスがあると推測されます。
            # ただし、LlamaHandlerに渡す設定は runtime_config 全体なので、
            # model_path は別途 runtime_config にマージする必要があります。
            return str(self._config_data['llama']['runtime_config']['model_path'])
        except KeyError as e:
            print(f"ERROR: 'llama.runtime_config.model_path' or a part of it not found in config YAML. Error: {e}")
            raise

    @property
    def llama_handler_config(self) -> Dict[str, Any]: # 新しいプロパティ名
        try:
            # runtime_config をベースに、model_path を絶対パス文字列として確実に含める
            config_for_handler = self._config_data['llama']['runtime_config'].copy()
            # model_path が runtime_config 内にすでにある場合はそれを使う。
            # なければ、別途定義された場所から取得して追加する。
            # あなたの config.yaml では llama.runtime_config.model_path にあるようなので、そのままで良いはず。
            # 念のため、絶対パスに変換し、文字列であることを保証する。
            model_path_value = config_for_handler.get('model_path')
            if not model_path_value:
                # もし runtime_config に model_path がなければ、別の場所から取得するロジックが必要
                # ここではエラーとするか、別の場所 (例: self._config_data['llama']['model_path']) から取得
                raise KeyError("'model_path' not found within llama.runtime_config in YAML.")

            # 相対パスの場合、config.yaml の場所を基準に絶対パスに変換することを検討
            base_dir = self.config_path.parent
            absolute_model_path = base_dir / Path(model_path_value)
            if not absolute_model_path.is_file():
                 print(f"WARNING: Model file at resolved path {absolute_model_path} not found. Checking original path: {model_path_value}")
                 if not Path(model_path_value).is_file(): # 元のパスでも確認
                     raise FileNotFoundError(f"Model file not found at {model_path_value} or {absolute_model_path}")
                 config_for_handler['model_path'] = str(Path(model_path_value).resolve()) # 元のパスを絶対パス化
            else:
                 config_for_handler['model_path'] = str(absolute_model_path.resolve())

            return config_for_handler
        except KeyError as e:
            print(f"ERROR: 'llama.runtime_config' or a part of it not found in config YAML. Error: {e}")
            raise

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

        
    async def process_message(self, user_id: str, message: str) -> str:
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
    # loggingの基本設定 (既にあれば不要)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__) # このスクリプト自体のロガー

    CONF_PATH = "/Users/yuuto/Desktop/nowProject/AIbot/config.yaml" # ご自身の環境に合わせてください

    async def main_test_run():
        logger.info("Starting main_test_run...")
        try:
            # Runtimeの初期化時に config_path を渡す
            ai_runtime = Runtime(config_path=CONF_PATH)
            user_message = "人間とはどのようなものだと認識されているのだい" # テストしたいメッセージ
            logger.info(f"Sending message to AI: '{user_message}'")

            tokenS = ai_runtime.llama._decode_prompt(user_message,False)
            print(f"tokenS:{tokenS}")

            # process_message を await で呼び出す
            response = await ai_runtime.process_message(user_id="test_user_id", message=user_message)

            print("-" * 30)
            print("AIの応答:")
            print(response)
            print("-" * 30)

        except FileNotFoundError as e:
            logger.error(f"Configuration file error: {e}")
            print(f"設定ファイルが見つかりません: {e}")
        except KeyError as e:
            logger.error(f"Configuration key error: {e} - config.yamlの構造を確認してください。")
            print(f"設定ファイルのキーエラー: {e} - config.yamlの構造を確認してください。")
        except Exception as e:
            logger.error(f"An unexpected error occurred in main_test_run: {e}", exc_info=True)
            print(f"予期せぬエラーが発生しました: {e}")
        
        

    # 非同期関数を実行
    asyncio.run(main_test_run())
