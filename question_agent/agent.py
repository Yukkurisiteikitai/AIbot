from runtime.runtime import Runtime
from question_agent.question_data import Question_Data
import asyncio
from utils.log import create_module_logger


ai_runtime = Runtime(config_path="config.yaml")
print(asyncio.run(ai_runtime.process_message(user_id="jfoaeg;o3f",message="hello")))


class Question_Agent:
    def __init__(self, config_path: str):
        self.runtime = Runtime(config_path=config_path)
        self.q_data = Question_Data(meta_data_path="question_agent/question_data.yaml")
        self.logger = create_module_logger(__name__)

    async def ask_question(self, user_id: str, question: str) -> str:
        self.logger.info(f"User {user_id} asks: {question}")
        response = await self.runtime.process_message(user_id=user_id, message=question)
        return response
    
    def init_question(self):
        # 質問データの初期化
        # 最初きに呼び出される質問の仕組み
        # というか、fronで整理した方がいいのではないか?
        pass


q_agent = Question_Agent(config_path="config.yaml")
q_agent.init_question()
# init question モード