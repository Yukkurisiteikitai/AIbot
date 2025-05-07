import logging

LOG_FILE = "bot.log"
logger = logging.getLogger("他のげん")
logger.setLevel(logging.INFO)

# コンソール出力用のハンドラー
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)


# loggerオブジェクトの作成
logger = logging.getLogger("ログ太郎")

logger.info("I am info log.")
logger.warning("I am warning log.")