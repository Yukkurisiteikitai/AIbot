# main.py HelloWrold
import time
import os
import logging
import sys
import importlib

# ロガーの設定
LOG_FILE = "bot.log"
logger = logging.getLogger("他のげん")
logger.setLevel(logging.INFO)  # ログレベルを設定

# コンソール出力用のハンドラー
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# ファイル出力用のハンドラー
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.INFO)

# フォーマッターの作成と設定
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# ハンドラーをロガーに追加
logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.info("HelloWorld")

THINK_SYSTEMS = ["bigfive", "mbti", "sfe"]
SELECT_SYSTEM = "bigfive"

# 動的にモジュールをインポート
try:
    if SELECT_SYSTEM in THINK_SYSTEMS:
        # 動的にモジュールをインポート
        llm_handler_multi = importlib.import_module(f"think_handler.{SELECT_SYSTEM}")
        logger.info(f"Successfully imported think system: {SELECT_SYSTEM}")
    else:
        logger.warning(f"Invalid system selected: {SELECT_SYSTEM}. Defaulting to bigfive.")
        llm_handler_multi = importlib.import_module("think_handler.bigfive")
except ImportError as e:
    logger.error(f"Error importing think system module: {e}")
    sys.exit(1)

print("HelloWorld")