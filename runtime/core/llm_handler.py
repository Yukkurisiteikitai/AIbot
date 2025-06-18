from llama_cpp import Llama
from typing import Dict, Any
import logging
from typing import Dict, Any


class LlamaHandler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        print(self.config)
        self.llm = Llama(
            model_path=str(config['model_path']),
            n_ctx=config['n_ctx'],
            n_batch=config['n_batch'],
            n_threads=config['n_threads'],
            n_gpu_layers=config.get('n_gpu_layers', 1),
            # n_gpu_layers=-1,
            chat_format="gemma",
            verbose=True
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
            print(f"プロンプトトークンを評価中...")
            self.llm.eval(full_prompt)
            print(f"プロンプトトークンの評価完了。")

            # 生成するトークンの最大数
            max_new_tokens = 512
            generated_tokens = []

            print(f"epos-token:{self.llm.token_eos()}")
            print(f"aa:{self.llm.detokenize([106]).decode('utf-8', errors='replace')}")
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
                if next_token == self.llm.token_eos() or next_token == 106:
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
    
    async def generate_simple(
    self,
    prompt: str,
    max_tokens: int = 200,
    temperature: float = 1.0 # temperature は sample メソッドで使う
    ) -> str:
        try:
            # Define the chat history with messages
            chat_history = [
                {"role": "user", "content": prompt}
            ]

            # Generate a chat completion using the Llama model
            output = self.llm.create_chat_completion(messages=chat_history)

            # Output the model's response
            print(output)
            return output
            
        except Exception as e:
            self.logger.error(f"Simple generation error: {e}", exc_info=True) # exc_info=Trueでトレースバックも記録
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