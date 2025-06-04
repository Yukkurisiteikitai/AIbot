from fastapi import FastAPI, APIRouter
from runtime.runtime import Runtime
import asyncio

app = FastAPI()


# region READER_tool(基本的に譲歩を取得する)
# AI の本体のモデル情報、CPUやGPUなどの使用状況が余裕があるか?具体的にどれくらいあるか


# ルーディングの設定

# 1. /ai プレフィックスを持つルーターを定義
ai_router = APIRouter(
    prefix="/ai",
    tags=["AI Operations"], # Swagger UI でグループ化されるタグ
    # 依存関係をルーター全体に適用することも可能 (ここでは省略)
)

# 2. /ai/question プレフィックスを持つルーターを定義 (ai_routerの子として)
question_router = APIRouter(
    prefix="/question",
    tags=["AI Questions"], # Swagger UI でグループ化されるタグ
)



runtime = Runtime(config_path="config.yaml")




@ai_router.get("/")
def get_ai_status():
    runtimeConfig = "get_run_machine"
    return runtimeConfig

@ai_router.get("/user_help")
def get_user_help():
    """
    ユーザーがAIに質問をするためのプロンプトを切り替えるエンドポイント
    """
    return {"message": "ユーザーがAIに質問をするためのプロンプトを切り替える"}

@question_router.get("/check")
def check_questions():
    """
    AIに質問がこれ以上残っているのかを確認するエンドポイント
    """
    # ここでは仮に質問が残っていると返す
    return {"remaining_questions": True}


@question_router.get("/ask")
def ask_question():
    """
    AIがユーザーに対する質問を投げるエンドポイント
    現在セットされている質問の中から順番に選ぶ
    内部的にはindexで質問として利用したものをnumberとリストで管理している
    """

    return {"question": "あなたの名前は何ですか？"}


from pydantic import BaseModel

class question_tiket(BaseModel):
    user_id: str
    question: str = "なんもuserから投げられてねーよ"


@question_router.post("/ask")
async def ask_reply(ticket:question_tiket):
    """
    AIがユーザーに対する質問を投げるエンドポイント
    現在セットされている質問の中から順番に選ぶ
    内部的にはindexで質問として利用したものをnumberとリストで管理している
    @pram user_id: ユーザーのID
    @pram message: ユーザーからのメッセージ(質問)
    """
    print(f"ユーザーID: {ticket.user_id}, 質問: {ticket.question}")
    answer = await runtime.process_message(user_id=ticket.user_id, message=ticket.question)
    # ここでは仮に質問を返す
    return {"answer": answer}

@question_router.post("/user_answer")
def user_answer(answer: str):
    """
    ユーザーの質問への回答で追加の質問があれば質問キューに追加するエンドポイント
    ユーザーの回答を保存する
    """
    # ここでは仮に回答を保存したと返す
    return {"message": "ユーザーの回答が保存されました", "answer": answer}

@app.get("/flow")
def get_flow():
    """
    現在のフローを取得するエンドポイント
    """
    # ここでは仮にフロー情報を返す
    return {"current_flow": "default_flow"}

@app.post("/flow")
def set_flow():
    """
    現在のフローの更新をするエンドポイント
    """
    # ここでは仮にフロー情報を返す
    return {"current_flow": "default_flow"}

#     """
#     AIのステータスを取得するエンドポイント
#     """
#     runtimeConfig = "get_run_machine"
#     return {"status": "AI is running", "model": "GPT-4", "cpu_usage": "20%", "gpu_usage": "30%"}

#     /user_help
#     [GET]ユーザーがAIに質問をするためのプロンプトを切り替える/
    
#     /question
#     19の質問(hello)に関するものだ
#     [GET]残っている質問を返す
        
#         /check
#         [GET]AIに質問がこれ以上残っているのかを確認する

#         /ask
#         [GET]AIがユーザーに対する質問を投げる(現在セットされている質問の中から順番に選ぶ)

#         /uesr_answer
#         [POST]ユーザーの質問への回答で追加の質問があれば質問キューに追加する
#         + 
#         ユーザーの回答を保存する

# /flow
#     [GET]現在のフローを取得する
#     [POST]フローを変更する {type: string, state: string}

# endregion



@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


# ルーターのデプロイ
ai_router.include_router(question_router)
app.include_router(ai_router)
