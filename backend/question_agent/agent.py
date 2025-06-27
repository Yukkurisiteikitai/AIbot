from runtime.runtime import Runtime
from question_agent.question_data import Question_Data
import asyncio
from utils.log import create_module_logger
from typing import Optional, Dict, Any, Union
import yaml
import os
from dataclasses import dataclass
from functools import wraps
import time

#region エラーハンドリング関連
@dataclass
class QuestionResponse:
    """質問応答のデータクラス"""
    message: str
    success: bool
    error_message: Optional[str] = None
    processing_time: Optional[float] = None


class QuestionAgentError(Exception):
    """QuestionAgentの基本例外クラス"""
    pass


class ConfigError(QuestionAgentError):
    """設定ファイル関連のエラー"""
    pass


class QuestionDataError(QuestionAgentError):
    """質問データ関連のエラー"""
    pass


class TimeoutError(QuestionAgentError):
    """処理タイムアウトエラー"""
    pass


def handle_errors(func):
    """エラーハンドリングデコレータ"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except QuestionAgentError:
            raise
        except Exception as e:
            self.logger.error(f"予期せぬエラー: {str(e)}")
            raise QuestionAgentError(f"処理中にエラーが発生しました: {str(e)}")
    return wrapper

# endregion

class QuestionAgent:
    def __init__(self, config_path: str, timeout: int = 30):
        """
        QuestionAgentの初期化
        
        Args:
            config_path (str): 設定ファイルのパス
            timeout (int): 処理のタイムアウト時間（秒）
            
        Raises:
            ConfigError: 設定ファイルの読み込みに失敗した場合
            QuestionDataError: 質問データの初期化に失敗した場合
        """
        self.timeout = timeout
        self.logger = create_module_logger(__name__)
        
        try:
            self._validate_config(config_path)
            self.runtime = Runtime(config_path=config_path)
            self.q_data = self._initialize_question_data()
            self.logger.info("QuestionAgentの初期化が完了しました")
        except Exception as e:
            self.logger.error(f"初期化エラー: {str(e)}")
            raise ConfigError(f"初期化に失敗しました: {str(e)}")

    def _validate_config(self, config_path: str) -> None:
        """
        設定ファイルの検証
        
        Args:
            config_path (str): 設定ファイルのパス
            
        Raises:
            ConfigError: 設定ファイルが無効な場合
        """
        if not os.path.exists(config_path):
            raise ConfigError(f"設定ファイルが見つかりません: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if not isinstance(config, dict):
                    raise ConfigError("設定ファイルの形式が不正です")
        except yaml.YAMLError as e:
            raise ConfigError(f"設定ファイルの解析に失敗しました: {str(e)}")

    def _initialize_question_data(self) -> Question_Data:
        """
        質問データの初期化
        
        Returns:
            Question_Data: 初期化された質問データオブジェクト
            
        Raises:
            QuestionDataError: 質問データの初期化に失敗した場合
        """
        try:
            return Question_Data(meta_data_path="question_agent/question_data.yaml")
        except Exception as e:
            raise QuestionDataError(f"質問データの初期化に失敗しました: {str(e)}")

    @handle_errors
    async def ask_question(self, user_id: str, question: str) -> QuestionResponse:
        """
        ユーザーからの質問を処理
        
        Args:
            user_id (str): ユーザーID
            question (str): ユーザーからの質問
            
        Returns:
            QuestionResponse: 処理結果を含む応答オブジェクト
            
        Raises:
            QuestionAgentError: 質問処理中にエラーが発生した場合
            TimeoutError: 処理がタイムアウトした場合
        """
        if not user_id or not question:
            return QuestionResponse(
                message="",
                success=False,
                error_message="ユーザーIDと質問は必須です"
            )
            
        start_time = time.time()
        try:
            self.logger.info(f"User {user_id} asks: {question}")
            
            # タイムアウト付きで処理を実行
            response = await asyncio.wait_for(
                self.runtime.process_message(user_id=user_id, message=question),
                timeout=self.timeout
            )
            
            processing_time = time.time() - start_time
            return QuestionResponse(
                message=response,
                success=True,
                processing_time=processing_time
            )
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"処理がタイムアウトしました（{self.timeout}秒）")
        except Exception as e:
            self.logger.error(f"質問処理エラー: {str(e)}")
            return QuestionResponse(
                message="",
                success=False,
                error_message=f"質問の処理に失敗しました: {str(e)}",
                processing_time=time.time() - start_time
            )

    @handle_errors
    async def init_question(self) -> None:
        """
        質問システムの初期化
        
        Raises:
            QuestionDataError: 初期化に失敗した場合
        """
        try:
            await self.q_data.initialize()
            self.logger.info("質問システムの初期化が完了しました")
        except Exception as e:
            self.logger.error(f"質問システムの初期化に失敗: {str(e)}")
            raise QuestionDataError(f"質問システムの初期化に失敗しました: {str(e)}")


async def main():
    """メイン実行関数"""
    try:
        agent = QuestionAgent(config_path="config.yaml")
        await agent.init_question()
        
        response = await agent.ask_question(
            user_id="test_user",
            question="こんにちは"
        )
        
        if response.success:
            print(f"応答: {response.message}")
            print(f"処理時間: {response.processing_time:.2f}秒")
        else:
            print(f"エラー: {response.error_message}")
            
    except QuestionAgentError as e:
        print(f"エラーが発生しました: {str(e)}")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())