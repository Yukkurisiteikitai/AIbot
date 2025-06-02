import logging
import traceback
import inspect
from typing import Optional, Dict, Any


class LogSystem:
    def __init__(self, name: str = "default_logger", module_name: Optional[str] = None):
        # モジュール名を含めたロガー名を生成
        if module_name:
            logger_name = f"{name}.{module_name}"
        else:
            logger_name = name
            
        self.logger = logging.getLogger(logger_name)
        self.module_name = module_name or name
        
        # 既存のハンドラーがある場合はスキップ（重複防止）
        if not self.logger.handlers:
            self._setup_logger()

    def _setup_logger(self):
        self.logger.setLevel(logging.DEBUG)

        # Console handler with detailed format for monitoring
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 詳細なフォーマット（ファイル名、行番号、関数名を含む）
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def get_logger(self):
        return self.logger

    def log_with_context(self, level: str, message: str, exception: Optional[Exception] = None):
        """コンテキスト情報付きでログを出力"""
        # 呼び出し元の情報を取得
        frame = inspect.currentframe().f_back
        caller_info = {
            'filename': frame.f_code.co_filename,
            'line_number': frame.f_lineno,
            'function_name': frame.f_code.co_name,
            'module': self.module_name
        }
        
        # メッセージにコンテキスト情報を追加
        context_message = f"[{caller_info['module']}] {message}"
        
        # 例外情報がある場合は追加
        if exception:
            context_message += f" | Exception: {type(exception).__name__}: {str(exception)}"
        
        # ログレベルに応じて出力
        log_method = getattr(self.logger, level.lower())
        log_method(context_message)
        
        # 例外の場合はスタックトレースも出力
        if exception and level.upper() in ['ERROR', 'CRITICAL']:
            self.logger.error("Stack trace:")
            self.logger.error(traceback.format_exc())

    def error_with_trace(self, message: str, exception: Optional[Exception] = None):
        """エラーログと詳細なトレース情報を出力"""
        self.log_with_context('error', message, exception)
        
        # 現在のスタックフレーム情報を収集
        stack = inspect.stack()
        self.logger.error("=== Call Stack ===")
        for i, frame_info in enumerate(stack[1:6]):  # 最大5レベルまで
            self.logger.error(
                f"  [{i}] {frame_info.filename}:{frame_info.lineno} "
                f"in {frame_info.function}()"
            )

    def monitor_function(self, func):
        """関数の実行を監視するデコレーター"""
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            module_name = func.__module__
            
            self.logger.info(f"[MONITOR] {module_name}.{func_name}() 開始")
            
            try:
                result = func(*args, **kwargs)
                self.logger.info(f"[MONITOR] {module_name}.{func_name}() 正常終了")
                return result
            except Exception as e:
                self.error_with_trace(
                    f"[MONITOR] {module_name}.{func_name}() でエラー発生", 
                    e
                )
                raise
                
        return wrapper

    def log_module_status(self, status: str, details: Optional[Dict[str, Any]] = None):
        """モジュールの状態をログ出力"""
        message = f"[{self.module_name}] Status: {status}"
        if details:
            detail_str = ", ".join([f"{k}={v}" for k, v in details.items()])
            message += f" | Details: {detail_str}"
        
        self.logger.info(message)


# 使用例とユーティリティ関数
def create_module_logger(module_name: str) -> LogSystem:
    """モジュール用のロガーを作成"""
    return LogSystem("app_monitor", module_name)


# 使用例
if __name__ == "__main__":
    # 各モジュール用のロガー作成
    db_logger = create_module_logger("database")
    api_logger = create_module_logger("api")
    auth_logger = create_module_logger("auth")
    
    # 通常のログ
    db_logger.get_logger().info("データベース接続開始")
    
    # エラー監視の例
    try:
        # 何らかの処理
        raise ValueError("データベース接続エラー")
    except Exception as e:
        db_logger.error_with_trace("データベース処理でエラー", e)
    
    # モジュール状態のログ
    api_logger.log_module_status("RUNNING", {"port": 8080, "connections": 5})
    
    # 関数監視の例
    @db_logger.monitor_function
    def sample_db_operation():
        # データベース操作
        print("DB操作実行中...")
        return "成功"
    
    sample_db_operation()