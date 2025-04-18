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

def teketou():
    user_quote = f"> {interaction.user.mention}: {message}\n\n"
        full_response_text = ai_response # LLMの応答のみを変数に

        # Discordの文字数制限
        MAX_CHARS = 2000

        # --- メッセージ分割ロジック ---
        messages_to_send = []
        # 最初のメッセージにはユーザーの引用を含める
        first_message_content = user_quote + full_response_text

        if len(first_message_content) <= MAX_CHARS:
            # 2000文字以下ならそのまま送信
            messages_to_send.append(first_message_content)
        else:
            # 2000文字を超える場合は分割する
            # 最初のチャンク (引用符 + 応答の冒頭)
            remaining_chars_first = MAX_CHARS - len(user_quote)
            if remaining_chars_first <= 0: # 引用だけで2000文字超える場合(レアケース)
                 logger.warning("User quote itself exceeds character limit.")
                 # 引用符だけ送るか、エラーにするかなど対応が必要
                 messages_to_send.append(user_quote[:MAX_CHARS]) # 強制的に切り詰め
                 # 応答部分は別途送る (ただし引用なし)
                 response_part = full_response_text
            else:
                 messages_to_send.append(user_quote + full_response_text[:remaining_chars_first])
                 response_part = full_response_text[remaining_chars_first:]

            # 残りの応答部分を2000文字ごとに分割
            # (ここでは単純な文字数分割。改行や単語境界を考慮するとより良い)
            while len(response_part) > 0:
                chunk = response_part[:MAX_CHARS]
                messages_to_send.append(chunk)
                response_part = response_part[MAX_CHARS:]

        # --- 分割したメッセージを送信 ---
        if not messages_to_send:
             logger.warning(f"No messages to send for user {user_id} after processing.")
             await interaction.followup.send("(空の応答)") # 何か送る必要がある
             return

        # 最初のチャンクは followup.send で送信
        await interaction.followup.send(messages_to_send[0])

        # 2番目以降のチャンクがある場合は、続けて送信
        # interaction.followup.send は複数回呼び出せる
        if len(messages_to_send) > 1:
            for chunk in messages_to_send[1:]:
                 # await interaction.channel.send(chunk) # こちらでも良い
                 print(chunk) # followupを続ける