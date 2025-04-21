# llm_handler.py
import os
import re
import json
import openai
import logging
from dotenv import load_dotenv
import db_manager # db_manager.py をインポート

load_dotenv()

# --- LM Studio 設定 ---
LM_STUDIO_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1") # デフォルト値追加
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio") # デフォルト値または.envから
LM_STUDIO_MODEL_RESPONSE = os.getenv("LM_STUDIO_MODEL_RESPONSE", "loaded-model") # .envから、なければ仮の値
LM_STUDIO_MODEL_REQUEST = os.getenv("LM_STUDIO_MODEL_REQUEST", "loaded-model") # .envから、なければ仮の値
CONVERSATION_HISTORY_LIMIT = int(os.getenv("CONVERSATION_HISTORY_LIMIT", 10)) # 履歴件数制限 (デフォルト10件)

getTag_system_prompt = """
あなたは `data.json` の `tags` から、ユーザーの  
"Situation": { "age": 16, "standing": "自分のことをあまり知らない", "location": "自宅", "time": "夜", "mood": "不安", "goal": "自分を知りたい", "trigger": "自分が図書館で機械学習の本を読んでいる時" }

pgsql
コピーする
編集する
の内容に関連するタグを選び、以下のような JSON で返してください。

```json
{
  "selected_tags": [
    "感情のトリガー",
    "自己認識",
    …
  ]
}
```
"""

logger = logging.getLogger('discord') # discord.py のロガーを使用

# --- OpenAI クライアントの初期化 (LM Studio 用) ---
client = openai.AsyncOpenAI(
    base_url=LM_STUDIO_URL,
    api_key=LM_STUDIO_API_KEY,
)
logger.info(f"Using LM Studio endpoint: {LM_STUDIO_URL}")
logger.info(f"Using LM Studio model (placeholder): {LM_STUDIO_MODEL_RESPONSE,LM_STUDIO_MODEL_REQUEST}") # モデル名を確認用にログ出力
logger.info(f"Conversation history limit: {CONVERSATION_HISTORY_LIMIT}")

async def generate_response(user_id: int, user_message: str, user_db_info: dict) -> str:
    """ユーザー情報とメッセージ、会話履歴に基づいてLLMで応答を生成する (LM Studio版)"""
    # --- プロンプトの組み立て ---
    system_prompt = "あなたはユーザーの分身として応答する人間です。\n"
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

    logger.debug(f"[User:{user_id}] System Prompt:\n{system_prompt}")
    logger.debug(f"[User:{user_id}] User Message: {user_message}")

    # --- 会話履歴の取得 ---
    past_history = await db_manager.get_conversation_history(user_id=user_id, limit=CONVERSATION_HISTORY_LIMIT)
    logger.debug(f"[User:{user_id}] Retrieved {len(past_history)} past messages: {past_history}")

    # --- 履歴フィルタリング (役割の交互性を保証) ---
    filtered_history = []
    if past_history:
        # 最初のメッセージが 'assistant' なら削除 (system の次は user を期待)
        # Note: LM Studio のテンプレートによっては assistant 開始でも良い場合がある
        if past_history[0]['role'] == 'assistant':
            logger.debug("[User:{user_id}] History starts with 'assistant', removing first message.")
            past_history = past_history[1:]

    # 交互になるようにフィルタリング
    last_role = 'system' # 初期状態は system の後とみなす
    for i, msg in enumerate(past_history):
        # 直前の役割と同じならスキップ (エラーの原因)
        if msg['role'] == last_role:
             logger.warning(f"[User:{user_id}] Skipping consecutive role '{msg['role']}' at index {i} in history.")
             continue
        # system が履歴に含まれていたらスキップ
        if msg['role'] == 'system':
             logger.warning(f"[User:{user_id}] Skipping unexpected 'system' role at index {i} in history.")
             continue
        # role が user/assistant 以外ならスキップ (念のため)
        if msg['role'] not in ('user', 'assistant'):
             logger.warning(f"[User:{user_id}] Skipping invalid role '{msg['role']}' at index {i} in history.")
             continue

        filtered_history.append(msg)
        last_role = msg['role']

    # 履歴の最後が 'user' の場合、それも削除 (次の user メッセージと連続するため)
    if filtered_history and filtered_history[-1]['role'] == 'user':
        logger.debug("[User:{user_id}] History ends with 'user', removing last message to prevent conflict.")
        # filtered_history.pop()

    logger.debug(f"[User:{user_id}] Filtered history ({len(filtered_history)} messages): {filtered_history}")

    # --- メッセージリストの構築 ---
    messages = []
    messages.append({"role": "system", "content": system_prompt})
    messages.extend(filtered_history)
    messages.append({"role": "user", "content": user_message})

    logger.debug(f"[User:{user_id}] Messages prepared for LLM (total {len(messages)} items): {messages}")

    
    # --- LM Studio API呼び出し ---
    async def LM_STUDIO_CALL(MODEL:str,messages:list):
        try:
            completion = await client.chat.completions.create(
                model=MODEL,
                messages=messages, # 修正されたメッセージリストを使用
                temperature=0.7,
                max_tokens=300 # 長い応答が必要な場合は増やす
            )
            response_text = completion.choices[0].message.content.strip()

            # --- 応答とユーザーメッセージをDBに保存 ---
            await db_manager.add_conversation_message(user_id=user_id, role="user", content=user_message)
            await db_manager.add_conversation_message(user_id=user_id, role="assistant", content=response_text)

            logger.info(f"[User:{user_id}] Generated response via LM Studio.")
            logger.debug(f"[User:{user_id}] LM Studio Response content: {response_text}")
            return response_text

        except openai.APIConnectionError as e:
            logger.error(f"[User:{user_id}] Failed to connect to LM Studio at {LM_STUDIO_URL}. Is it running? {e}")
            return "ごめんなさい、ローカルAIに接続できませんでした。LM Studioが起動しているか確認してください。"
        except openai.NotFoundError as e:
            logger.error(f"[User:{user_id}] Model '{MODEL}' not found on LM Studio: {e}")
            return f"ごめんなさい、LM Studioでモデル '{MODEL}' が見つかりませんでした。LM Studioで正しいモデルがロードされているか確認してください。"
        except openai.APITimeoutError as e:
            logger.error(f"[User:{user_id}] LM Studio request timed out: {e}")
            return "ごめんなさい、ローカルAIからの応答が時間内に返ってきませんでした。モデルの処理が重いか、LM Studioに問題があるかもしれません。"
        except Exception as e:
            logger.error(f"[User:{user_id}] LM Studio API error: {e}", exc_info=True) # exc_info=True でトレースバックも記録
            error_detail = str(e)
            # エラーメッセージにJinjaエラーが含まれているかチェック
            if "Error rendering prompt with jinja template" in error_detail and "roles must alternate" in error_detail:
                logger.error("[User:{user_id}] Detected role alternation error possibly due to history format.")
                # ユーザーに直接詳細を見せるのは避けた方が良い場合もある
                # return f"ごめんなさい、会話履歴の形式に問題が発生した可能性があります。 '/clear_history' を試してみてください。(詳細: {error_detail})"
                return "ごめんなさい、会話履歴の形式に問題が発生した可能性があります。`/clear_history` コマンドを試してみてください。"
            # その他の予期せぬエラー
            return f"ごめんなさい、ローカルAIで予期せぬエラーが発生しました。ログを確認してください。"

    async def RequestAI():
        
        request_text = await LM_STUDIO_CALL(MODEL=LM_STUDIO_MODEL_REQUEST)
        # ```json ... ``` の中を取り出す
        match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', request_text)
        if match:
            json_str = match.group(1)
            data = json.loads(json_str)
            print(data)
        else:
            print("JSONが見つかりませんでした")  
