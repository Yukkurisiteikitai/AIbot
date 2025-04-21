# llm_handler.py
import os
import openai
import logging
from dotenv import load_dotenv
import db_manager # db_manager.py をインポート

# load_dotenv()
import os
import openai
import logging
import json
from dotenv import load_dotenv

# Step 3: 応答生成用モデル (元のモデルなど)
LM_STUDIO_MODEL_RESPONSE = os.getenv("LM_STUDIO_MODEL_RESPONSE") # または元の LM_STUDIO_MODEL


print(f"""
LM_STUDIO_MODEL_RESPONSE = {LM_STUDIO_MODEL_RESPONSE}
\      """)


