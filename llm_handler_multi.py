# llm_handler_multistep.py
import os
import openai
import logging
import json
from dotenv import load_dotenv

load_dotenv()

# --- 設定 ---
## .envからLM StudioのエンドポイントURLを読み込む
LM_STUDIO_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
LM_STUDIO_API_KEY = "lm-studio"

## モデル名を読み込む
# Step 1: タグ選択用軽量モデル
LM_STUDIO_MODEL_REQUEST = os.getenv("LM_STUDIO_MODEL_REQUEST")
# Step 2: 応答生成用モデル (元のモデルなど)
LM_STUDIO_MODEL_RESPONSE = os.getenv("LM_STUDIO_MODEL_RESPONSE") # または元の LM_STUDIO_MODEL


## --- ロガー設定 ---
logger = logging.getLogger('discord') # または任意のロガー名
# basicConfigを一度だけ設定（既にあれば不要）
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- OpenAI クライアント初期化 (LM Studio 用) ---
# 全ステップで同じクライアントを使い、モデル名を都度指定する
client = openai.AsyncOpenAI(
    base_url=LM_STUDIO_URL,
    api_key=LM_STUDIO_API_KEY,
)
logger.info(f"Using LM Studio endpoint: {LM_STUDIO_URL}")
logger.info(f"Tag Selection Model (Request): {LM_STUDIO_MODEL_REQUEST}")
logger.info(f"Response Generation Model (Response): {LM_STUDIO_MODEL_RESPONSE}")

# --- 定数: data.json の内容 ---
# MARK: 指定先TAG変更
# 実際の data.json ファイルから読み込むか、コード内に直接定義
# ここでは例として直接定義
DATA_JSON_CONTENT = {
  "tags":[
    "幼少期に何があったか", "周囲の人の様子", "コンプレックス等の自分のあまり伝えなかった点",
    "性格の特徴", "信念・価値観", "趣味・興味", "対人関係のスタイル", "感情の反応",
    "理想・夢", "過去の失敗と学び", "内面の葛藤", "感情のトリガー", "行動のパターン",
    "思考プロセス", "言動の癖", "価値観の変遷", "自己認識", "対立と解決の方法",
    "対人関係の歴史", "将来への不安と希望"
  ]
}
TAGS_LIST = DATA_JSON_CONTENT["tags"]


# --- Step 1: タグ選択関数 ---
async def select_relevant_tags(situation: dict) -> list[str]:
    """
    ユーザーの状況に基づいて関連性の高いタグを軽量LLMで選択する。
    """
    if not LM_STUDIO_MODEL_REQUEST:
        logger.error("LM_STUDIO_MODEL_REQUEST is not set in .env file.")
        return ["エラー：タグ選択モデルが設定されていません"] # エラーを示すタグリスト

    # data.jsonの内容を文字列としてプロンプトに埋め込む
    data_json_string = json.dumps(DATA_JSON_CONTENT, ensure_ascii=False, indent=2)
    situation_string = json.dumps(situation, ensure_ascii=False, indent=2)

    # タグ選択用のシステムプロンプト
    system_prompt = f"""あなたはユーザーの状況を分析し、以下の `data.json` の `tags` リストから最も関連性の高いタグを **いくつか** 選択するAIです。
ユーザーの "Situation" 情報を参考にしてください。

--- data.json ---
{data_json_string}
--- ここまで ---

--- User Situation ---
{situation_string}
--- ここまで ---

選択したタグを以下のJSON形式**のみ**で出力してください。他のテキスト（説明文など）は絶対に含めないでください。

```json
{{
  "selected_tags": [
    "選択したタグ1",
    "選択したタグ2",
    ...
  ]
}}
```"""

    logger.debug(f"Tag selection system prompt:\n{system_prompt}")

    try:
        completion = await client.chat.completions.create(
            model=LM_STUDIO_MODEL_REQUEST, # ★ タグ選択用モデルを指定
            messages=[
                {"role": "system", "content": system_prompt},
                # User messageは空か、簡単な指示でも良い
                {"role": "user", "content": "上記の状況に最も関連するタグを選択し、指定されたJSON形式で出力してください。"}
            ],
            temperature=0.2, # 精度重視で低めに設定
            max_tokens=200,  # タグリストのJSON出力には十分なはず
            # response_format={"type": "json_object"} # LM Studioが対応していればより確実
        )
        response_content = completion.choices[0].message.content.strip()
        logger.debug(f"Raw response from tag selection model: {response_content}")

        # --- JSON パース処理 ---
        # ```json ... ``` のようなマークダウンが含まれる場合があるため、抽出を試みる
        json_block_match = re.search(r"```json\s*([\s\S]*?)\s*```", response_content)
        if json_block_match:
            json_string = json_block_match.group(1).strip()
        else:
             # マークダウンがない場合は、全体がJSONであることを期待
             json_string = response_content

        try:
            parsed_json = json.loads(json_string)
            selected_tags = parsed_json.get("selected_tags", [])
            if not isinstance(selected_tags, list):
                 logger.warning(f"Expected 'selected_tags' to be a list, but got: {type(selected_tags)}. Raw: {response_content}")
                 return ["エラー：タグ選択結果の形式が不正です"] # エラーを示すタグ

            logger.info(f"Successfully selected tags: {selected_tags}")
            # 念のため、選択されたタグが元のリストに存在するかチェック（任意）
            valid_tags = [tag for tag in selected_tags if tag in TAGS_LIST]
            if len(valid_tags) != len(selected_tags):
                 logger.warning(f"Some selected tags were not in the original list. Filtered tags: {valid_tags}")
            return valid_tags # 存在するタグのみを返す or selected_tags をそのまま返すか選択

        except json.JSONDecodeError as json_e:
            logger.error(f"Failed to parse JSON response from tag selection model. Error: {json_e}. Response: {response_content}")
            return ["エラー：タグ選択結果のJSON解析に失敗"] # エラータグ
        except Exception as e:
             logger.error(f"An unexpected error occurred during tag selection JSON processing: {e}")
             return ["エラー：タグ選択処理中に予期せぬエラー"] # エラータグ


    except openai.APIConnectionError as e:
         logger.error(f"Failed to connect to LM Studio at {LM_STUDIO_URL} for tag selection. Is it running? {e}")
         return ["エラー：タグ選択用AI接続失敗"] # エラータグ
    except Exception as e:
        logger.error(f"Tag selection API error: {e}")
        error_detail = str(e)
        if "model_not_found" in error_detail.lower():
             return [f"エラー：タグ選択モデル '{LM_STUDIO_MODEL_REQUEST}' が見つかりません"]
        return [f"エラー：タグ選択用AIでエラー ({error_detail})"] # エラータグ

# --- Step 2: DB検索関数 (ダミー) ---
# MARK: 検索->プロンプトデータ
# ここは実際のデータベースに合わせて実装する必要があります
async def search_user_info_by_tags(user_id: int, tags: list[str]) -> dict:
    """
    選択されたタグに基づいてデータベースからユーザー情報を検索する（ダミー実装）。
    """
    logger.info(f"Searching DB for user {user_id} with tags: {tags}")
    # --- ここからダミー実装 ---
    # 本来はここでDBに接続し、tagsに関連する情報を取得する
    # 例: SELECT profile, habit, likes FROM user_profiles WHERE user_id = ? AND category IN (?, ?, ...)
    #     または、タグごとに関連情報を取得するなど
    dummy_data = {
        "profile": "読書が好きで、特に技術書に興味がある。少し内向的かもしれない。",
        "habit": "考え事をするとき、指を机で叩く癖がある。",
        "likes": "静かな場所、図書館、新しい知識",
        "感情のトリガー": "難しい問題に直面すると不安を感じやすいが、解決策を見つけると興奮する。",
        "自己認識": "自分のことをまだよく理解できていないと感じている。",
        # 他のタグに対応する情報があれば追加...
    }
    # 取得したタグに関連する情報だけをフィルタリングする（例）
    filtered_data = {}
    if "エラー：" in "".join(tags): # タグ選択でエラーが発生した場合
         filtered_data["error"] = "タグ選択中にエラーが発生したため、関連情報が見つかりませんでした。"
         return filtered_data

    for tag in tags:
        # タグ名をキーとして単純に検索する例（実際はもっと複雑なマッピングが必要かも）
        
        # 例えば "性格の特徴" タグなら profile や tone に関連するなど
        if tag == "自己認識" and "自己認識" in dummy_data:
            filtered_data["自己認識"] = dummy_data["自己認識"]
        elif tag == "感情のトリガー" and "感情のトリガー" in dummy_data:
            filtered_data["感情のトリガー"] = dummy_data["感情のトリガー"]
        elif tag == "趣味・興味" and "likes" in dummy_data: # "趣味・興味" タグと likes 項目を関連付け
            filtered_data["趣味・興味"] = dummy_data["likes"]
        elif tag == "性格の特徴" and "profile" in dummy_data: # "性格の特徴" タグと profile 項目を関連付け
             filtered_data["性格の特徴"] = dummy_data["profile"] # profileの一部を使うなど工夫も可能
        # 他のタグとDB項目のマッピングを追加...

    if not filtered_data:
        filtered_data["info"] = "関連する情報は見つかりませんでした。" # 何も見つからなかった場合

    logger.info(f"Dummy DB search result for user {user_id}: {filtered_data}")
    # --- ダミー実装ここまで ---
    return filtered_data

# --- Step 3 & 4: 応答生成関数 (改訂版) ---
async def generate_final_response(user_id: int, user_message: str, relevant_user_info: dict) -> str:
    """
    選択されたタグに基づいて取得したユーザー情報とメッセージを元に、応答生成LLMで応答を生成する。
    """
    if not LM_STUDIO_MODEL_RESPONSE:
        logger.error("LM_STUDIO_MODEL_RESPONSE is not set in .env file.")
        return "ごめんなさい、応答生成用のAIモデルが設定されていません。"

    # --- プロンプトの組み立て ---
    system_prompt = "あなたはユーザーの分身として応答するAIです。\n"
    system_prompt += "以下のユーザー情報（関連性の高いと判断された情報）を参考に、その人になりきって自然に会話してください。\n"

    if relevant_user_info:
        system_prompt += "\n--- 関連ユーザー情報 ---\n"
        # relevant_user_info の内容を表示する
        # キーがタグ名になっていることを想定
        for key, value in relevant_user_info.items():
             if key == "error": # DB検索前のエラー情報
                  system_prompt += f"- システム情報: {value}\n"
             elif key == "info": # DB検索で見つからなかった情報
                  system_prompt += f"- システム情報: {value}\n"
             else:
                 # タグ名 (key) をそのまま説明として使う
                 system_prompt += f"- {key}: {value}\n"
        system_prompt += "--- ここまで ---\n"
    else:
        # relevant_user_infoが空の場合（タグ選択失敗 or DB検索結果なし）
        system_prompt += "現在、参照できるユーザー情報がありません。一般的な応答をしてください。\n"
        # もしタグ選択失敗のエラーメッセージがあれば、それも考慮する？ (今はしていない)

    system_prompt += "\nユーザーへの応答だけを生成してください。余計な前置きや説明は不要です。"

    logger.debug(f"Final response system prompt for user {user_id}:\n{system_prompt}")
    logger.debug(f"Original user message from {user_id}: {user_message}")

    # --- LM Studio API呼び出し (応答生成用モデル) ---
    try:
        completion = await client.chat.completions.create(
            model=LM_STUDIO_MODEL_RESPONSE, # ★ 応答生成用モデルを指定 ★
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=250 # 必要に応じて調整
        )
        response_text = completion.choices[0].message.content.strip()
        logger.info(f"Generated final response for user {user_id} via LM Studio ({LM_STUDIO_MODEL_RESPONSE})")
        logger.debug(f"LM Studio Response content: {response_text}")
        return response_text

    except openai.APIConnectionError as e:
         logger.error(f"Failed to connect to LM Studio at {LM_STUDIO_URL} for response generation. Is it running? {e}")
         return "ごめんなさい、応答生成AIに接続できませんでした。LM Studioが起動しているか確認してください。"
    except Exception as e:
        logger.error(f"Response generation API error for user {user_id}: {e}")
        error_detail = str(e)
        if "model_not_found" in error_detail.lower():
             return f"ごめんなさい、応答生成モデル '{LM_STUDIO_MODEL_RESPONSE}' が見つかりませんでした。"
        return f"ごめんなさい、応答生成AIでエラーが発生しました。(詳細: {error_detail})"

# --- 全体の処理フローをまとめる関数 ---
import re # JSON抽出のために追加

async def process_user_request(user_id: int, user_message: str, situation: dict) -> str:
    """
    ユーザーリクエストを処理する一連のステップを実行する。
    1. タグ選択 -> 2. DB検索 -> 3. 応答生成
    """
    # Step 1: 関連タグを選択
    selected_tags = await select_relevant_tags(situation)
    logger.info(f"Step 1 completed for user {user_id}. Selected tags: {selected_tags}")

    # タグ選択でエラーが発生した場合、それをユーザー情報として扱う
    if selected_tags and "エラー：" in selected_tags[0]:
        relevant_user_info = {"error": selected_tags[0]} # エラーメッセージを情報辞書に入れる
    else:
        # Step 2: タグに基づいてDB情報を検索 (ダミー)
        relevant_user_info = await search_user_info_by_tags(user_id, selected_tags)
        logger.info(f"Step 2 completed for user {user_id}. Relevant info found: {list(relevant_user_info.keys())}")

    # Step 3 & 4: 最終応答を生成
    final_response = await generate_final_response(user_id, user_message, relevant_user_info)
    logger.info(f"Step 3 & 4 completed for user {user_id}.")

    return final_response

# --- 実行例 ---
async def main():
    # ユーザーからのメッセージと状況 (例)
    user_id = 123
    user_message = "最近、自分が何を考えているのかよくわからなくなるんだ..."
    situation_data = {
        "age": 16,
        "standing": "自分のことをあまり知らない",
        "location": "自宅",
        "time": "夜",
        "mood": "不安",
        "goal": "自分を知りたい",
        "trigger": "自分が図書館で機械学習の本を読んでいる時"
    }

    # 処理を実行
    response = await process_user_request(user_id, user_message, situation_data)

    print("\n--- Final Response ---")
    print(response)
    print("--- End ---")

if __name__ == "__main__":
    import asyncio
     # --- JSON抽出のための正規表現ライブラリをインポート ---
    import re # select_relevant_tags 関数内で必要になるため、ここでも import しておくか、関数の上に移動
    asyncio.run(main())