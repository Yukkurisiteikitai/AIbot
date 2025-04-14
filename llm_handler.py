# llm_handler.py
import os
import openai
import logging
from dotenv import load_dotenv

load_dotenv()

# --- LM Studio 設定 ---
# .envファイルからLM StudioのエンドポイントURLを読み込む
# デフォルトは http://localhost:1234/v1
LM_STUDIO_URL = os.getenv("LM_STUDIO_BASE_URL")
# LM StudioはAPIキーを必要としない場合が多いので、ダミーを設定
LM_STUDIO_API_KEY = "lm-studio" # または "dummy-key", "not-needed" など
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL")

logger = logging.getLogger('discord')

# --- OpenAI クライアントの初期化 (LM Studio 用) ---
client = openai.AsyncOpenAI(
    base_url=LM_STUDIO_URL,
    api_key=LM_STUDIO_API_KEY, # ダミーキーを設定
)
logger.info(f"Using LM Studio endpoint: {LM_STUDIO_URL}")

async def generate_response(user_id: int, user_message: str, user_db_info: dict) -> str:
    """ユーザー情報とメッセージに基づいてLLMで応答を生成する (LM Studio版)"""
    # --- プロンプトの組み立て ---
    # (ここはOpenAI版と同じ)
    system_prompt = "あなたはユーザーの分身として応答するAIです。\n"
    system_prompt += "以下のユーザー情報を参考に、その人になりきって自然に会話してください。\n"

    if user_db_info:
        system_prompt += "\n--- ユーザー情報 ---\n"
        for key, value in user_db_info.items():
             if key == 'habit':
                 system_prompt += f"- 口癖や文体: {value}\n"
             elif key == 'likes':
                 system_prompt += f"- 好きなもの: {value}\n"
             elif key == 'profile':
                 system_prompt += f"- プロフィール: {value}\n"
             elif key == 'tone':
                 system_prompt += f"- 話し方のトーン: {value}\n"
             else:
                 system_prompt += f"- {key}: {value}\n"
        system_prompt += "--- ここまで ---\n"
    else:
        system_prompt += "現在、ユーザー情報は登録されていません。一般的な応答をしてください。\n"

    system_prompt += "\nユーザーへの応答だけを生成してください。"

    logger.debug(f"System Prompt for user {user_id}:\n{system_prompt}")
    logger.debug(f"User Message from {user_id}: {user_message}")

    # --- LM Studio API呼び出し ---
    try:
        # 注意: 'model'パラメータはLM Studioでロードしているモデル名に合わせてください。
        # LM Studioのローカルサーバータブで確認できます。
        # モデル名はLM Studio側で管理されるため、特定の値が必要ない場合もありますが、
        # API仕様上必要な場合が多いです。"local-model" やロードしたモデル名の一部など。
        # 例: "loaded-model" や "mistral-7b-instruct-v0.1.Q4_K_M.gguf" など
        # LM Studioのバージョンや設定により、不要な場合や特定の指定が必要な場合があります。
        # まずはダミー値やロード中のモデル名で試してみてください。
        completion = await client.chat.completions.create(
            model=LM_STUDIO_MODEL, # ★ LM Studioでロードしているモデル名に合わせて調整 ★
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=150 # ローカルモデルに合わせて調整が必要な場合あり
        )
        response_text = completion.choices[0].message.content
        logger.info(f"Generated response for user {user_id} via LM Studio")
        logger.debug(f"LM Studio Response content: {response_text}")
        return response_text

    except openai.APIConnectionError as e:
         logger.error(f"Failed to connect to LM Studio at {LM_STUDIO_URL}. Is it running? {e}")
         return "ごめんなさい、ローカルAIに接続できませんでした。LM Studioが起動しているか確認してください。"
    except Exception as e:
        # API呼び出し中の他のエラー (モデルが見つからない、タイムアウトなど)
        logger.error(f"LM Studio API error for user {user_id}: {e}")
        # エラーメッセージに詳細が含まれる場合がある
        error_detail = str(e)
        if "model_not_found" in error_detail.lower():
             return f"ごめんなさい、LM Studioで指定されたモデルが見つかりませんでした。現在ロードされているモデルを確認してください。(エラー詳細: {error_detail})"
        return f"ごめんなさい、ローカルAIでエラーが発生しました。(詳細: {error_detail})"
    