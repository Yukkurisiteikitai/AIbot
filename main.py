from fastapi import FastAPI, APIRouter,Request
from runtime.runtime import Runtime
import asyncio
import httpx
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from api_module import question_tiket, thread_tiket, call_internal_api,get_server_host_data

# other router
import api_use_db
app = FastAPI()

#DB関連
from db.db_database import async_engine
from db.models import Base


origins = [
    "http://localhost",
    "http://localhost:8010",
    "http://127.0.0.1",
    "http://127.0.0.1:8010",
    "null" # <--- ★この行を必ず追加してください。Developer Consoleで`null`オリジンからアクセスするために必要です。
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 許可するオリジンのリスト
    allow_credentials=True,      # クッキーなどの資格情報を許可するか
    allow_methods=["*"],         # 許可するHTTPメソッド (GET, POST, PUT, DELETEなど)
    allow_headers=["*"],         # 許可するHTTPヘッダー
)
# region READER_tool(基本的に譲歩を取得する)
# AI の本体のモデル情報、CPUやGPUなどの使用状況が余裕があるか?具体的にどれくらいあるか

from contextlib import asynccontextmanager

# 初期化
@app.on_event("startup")
async def startup_database_initialize():
    """
    アプリケーション起動時にDBを初期化する
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables checked/created.")



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
    tags=["AI Questions"], 
)

# 3. /db プレフィクスを持つルーターを定義
# db_router = APIRouter(
#     prefix="/db",
#     tags=["Data sorce"], 
# )



# AIを動かす用のruntime
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





@question_router.post("/")
async def get_init_question(ticket: thread_tiket,request: Request):
    """
    質問システムの初期化エンドポイント
    ここでは質問の初期化を行う
    """
    base_url = get_server_host_data(request=request)

    # {
    #     user_id:int,
    #     message:str,
    # }
    # internal_api_headers = {"Content-Type": "application/json"}

    #　make スレッド
    # async with httpx.AsyncClient() as client:
    #     thread_data = await call_internal_api(
    #         client=client
    #         base_url=base_url,
    #         method="POST",
    #         endpoint="/db/threads",
    #         headers=internal_api_headers
    #     )

        # next_question = thread_data["question"][0]
        
        
        

    
    # b[/db/thread/new]
    # POST
    #     {
    #         user_id:int,
    #         message:str,
    #         mode:str = "search"
    #     }
    # 
    # thread_id = create_new_thread({ticket.user_id,tiket.message})
    

    # スレッドidを作成して返す
    # ただしスレッドidはchatなのかserchなのかを区別するために
    # cht_xxxxxxxxxxx.xxxxxxxx.xxxxxx
    # srh_xxxxxxxxxxx.xxxxxxxx.xxxxxx
    # としてidを発行する

    


    # b[GET: /ai/question/check]
    #     {
    #         user_id:int
    #     }

    # questions:list = get_questions(user_id=ticket.user_id)
    
    # return
    # {
    #     questions[list[str]], {"あなたはどんな生き方をしてきましたか", "あなたの趣味は何ですか", "最近の出来事について教えてください"}
    # }

    # この{questions[0]}
    # を使って質問を行う
    
    # [GET: /ai/question/ask]
    # GET
    #question = get_ai_question(user_id=tiket.user_id, question=questions[0])
    #     {
    #         user_id:int,
    #         question:str -> {questions[0]}
    #     }
    
    "/ai/question/ask"


    # questions[0]は削除される
    

    try:
        # asyncio.run(runtime.init_question())
        # return {"message": "質問システムの初期化が完了しました"}
        thread_id = "cht_" + ticket.user_id + ".xxxxxxxx.xxxxxx"
        return {"thread_id": thread_id, 
                "question": "あなたはだんだん眠くなるのはいつですか？",}
    except Exception as e:
        return {"error": str(e)}
    

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

# region フロー
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
# db_router.include_router(api_use_db.router)

app.include_router(ai_router)
app.include_router(api_use_db.router)