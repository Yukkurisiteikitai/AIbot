from dotenv import load_dotenv
import os
import asyncio
load_dotenv()

# --- LM Studio 設定 ---
# .envファイルからLM StudioのエンドポイントURLを読み込む
# デフォルトは http://localhost:1234/v1
LM_STUDIO_URL = os.getenv("LM_STUDIO_BASE_URL")
# LM StudioはAPIキーを必要としない場合が多いので、ダミーを設定
LM_STUDIO_API_KEY = "lm-studio" # または "dummy-key", "not-needed" など
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL")
import db_manager
system_prompt = "teketou"
user_id = 1015220054528364584
user_message = "入力"

async def his():
    history = []
    await history = db_manager.get_user_history(user_id=user_id)
    prompts = []
    prompts.append({"role": "system", "content": system_prompt})

    # for i in history:
    prompts.append(history)
    prompts.append({"role": "user", "content": user_message})
    print(prompts)
    print(history)