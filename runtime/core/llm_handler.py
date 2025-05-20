from llama_cpp import Llama
from typing import Dict, Any, Optional
import asyncio
import logging

class LlamaHandler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
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