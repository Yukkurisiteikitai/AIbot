from dotenv import load_dotenv
import os
load_dotenv()

# --- LM Studio 設定 ---
# .envファイルからLM StudioのエンドポイントURLを読み込む
# デフォルトは http://localhost:1234/v1
LM_STUDIO_URL = os.getenv("LM_STUDIO_BASE_URL")
# LM StudioはAPIキーを必要としない場合が多いので、ダミーを設定
LM_STUDIO_API_KEY = "lm-studio" # または "dummy-key", "not-needed" など
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL")

print(LM_STUDIO_MODEL)