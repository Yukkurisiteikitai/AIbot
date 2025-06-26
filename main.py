from fastapi import FastAPI, APIRouter,Request
from runtime.runtime import Runtime
import asyncio
import httpx
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from api_module import thread_tiket, call_internal_api,get_server_host_data, question_ticket_go

# other router
import db.api_use_db as api_use_db
from OAth.google_auth import outh_router

#DB関連
from db.db_database import async_engine
from db.models import Base


# 設定
app = FastAPI()
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
ai_question_router = APIRouter(
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





@ai_question_router.post("/")
async def get_init_question(ticket: thread_tiket,request: Request):
    """
    質問システムの初期化エンドポイント
    ここでは質問の初期化を行う
    """
    base_url:str = get_server_host_data(request=request)

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
    

# profile
from utils.question_metadata import QuestionMetadataManager
q_manager = QuestionMetadataManager(config_path="configs/meta_question.yaml")
system_init = True

class qu_t(BaseModel):
    user_id:int
    need_theme:str = "Not Found Theme"

@ai_question_router.post("/make")
async def question_make(contextHello:qu_t,request:Request):
    if contextHello.need_theme == "Not Found Theme":
        return {"state":"error","context":"Not Found Theme"}
    
    base_url = get_server_host_data(request=request)
    internal_api_headers = {"Content-Type": "application/json"}
    # # 　make スレッド
    # need_items = ["what","when","how"]

    # if system_init == False: 
    #     need_items.append("where")
    #     need_items.append("why")
    
    need_items = ["どんな","いつ","どのように"]

    if system_init == False: 
        need_items.append("いつ")
        need_items.append("なぜ")
    
    addList:list[str] = []

    for q_item in need_items:
        # 質問情報
        prompt = f"""
あなたは質問のプロフェッショナルです。
{contextHello.need_theme}について{q_item}の観点から質問を考えてください。
"""     
        # url = f"{base_url}/ai/question/ask"
        # print(base_url)
        # シンプル質問
        async with httpx.AsyncClient() as client:
            answer = await call_internal_api(
                client=client,
                base_url=base_url,
                json_payload={"question":prompt,"user_id":contextHello.user_id},
                method="POST",
                endpoint="/ai/question/ask",
                headers=internal_api_headers
            )    
        
        print(f"answer:{answer}")
        addList.append(answer["answer"]) # {"answer":"answer_context"}だから

    return {"questions":addList}

class Question_tiket_answer_check(BaseModel):
    question:str = "<<<<<$o__o$>>>>>"
    answer:str = ">S_^_5<"
    user_id:int = 0
# {question:"質問1", answer:"回答1"}

@ai_question_router.get("/answer/check")
async def get_question_answer_check(ticket:Question_tiket_answer_check):
    prompt = f"""
質問:[{ticket.question}]
回答:[{ticket.answer}]
回答として間違ったものかどうかを
 - True
 - False
でブーリアンで回答してください。
説明等の他の要素は回答を禁止します。
""" 
    
    answer = await runtime.process_message(user_id=ticket.user_id, message=prompt)
    
    if answer in "False":
        return {"state":True}
    elif answer in "True":
        return {"state":False}


    

@ai_question_router.get("/")
def check_questions():
    """
    質問の情報が残っているか?
    """
    # ここでは仮に質問が残っていると返す
    # 質問

    return {"remaining_questions": True}


@ai_question_router.get("/ask")
def ask_question():
    """
    AIがユーザーに対する質問を投げるエンドポイント
    現在セットされている質問の中から順番に選ぶ
    内部的にはindexで質問として利用したものをnumberとリストで管理している
    """

    return {"question": "あなたの名前は何ですか？"}

# @question_make

# from fastapi import BackgroundTasks
# from db.db_database import AsyncSessionLocal
# async def generate_questions_in_background(
#     db_session_factory: sessionmaker, # sessionmakerの型ヒント
#     user_id: int,
#     thread_id: str, # スレッドIDも渡す
#     need_theme: str,
#     is_initial_phase: bool, # system_init の状態を渡す
#     base_url_for_llm: str,
#     headers_for_llm: Dict[str, str]
# ):
#     async with db_session_factory() as db: # タスク内で新しいセッション
#         need_items = ["what", "when", "how"]
#         if not is_initial_phase: # 初期フェーズでなければ (つまり完了済みなら)
#             need_items.extend(["where", "why"])

#         all_generated_questions_text = []
#         for q_item in need_items:
#             prompt = f"""あなたは質問のプロフェッショナルです。
# テーマ「{need_theme}」について、「{q_item}」の観点からユーザーに尋ねるべき具体的な質問を1つだけ、簡潔に考えてください。
# 質問文のみを返してください。余計な説明や挨拶は不要です。
# 例: テーマ「趣味」、観点「what」の場合、「あなたの主な趣味は何ですか？」
# 質問: """

#             try:
#                 # /ai/question/ask を呼び出す (runtime.process_message 経由)
#                 # user_id は str 型で渡す想定 (runtime.py の process_message の型ヒントによる)
#                 response_payload = await call_internal_api(
#                     client=httpx.AsyncClient(), # ループごとにクライアント作成は非効率だが、簡潔化のため
#                     base_url=base_url_for_llm,
#                     json_payload={"question": prompt, "user_id": str(user_id)}, # user_id を str に
#                     method="POST",
#                     endpoint="/ai/question/ask", # runtime.process_messageを呼び出すエンドポイント
#                     headers=headers_for_llm
#                 )
#                 generated_question = response_payload.get("answer", "").strip()

#                 if generated_question and len(generated_question) > 5 and "?" in generated_question: # 簡単なバリデーション
#                     all_generated_questions_text.append(generated_question)
#                     # DBに保存
#                     await crud.create_question(
#                         db=db,
#                         user_id=user_id,
#                         thread_id=thread_id, # thread_id も保存
#                         question_text=generated_question,
#                         why_question=f"Generated for theme '{need_theme}', aspect '{q_item}'",
#                         priority=5, # 適宜設定
#                         source=f"{need_theme}/{q_item}"
#                     )
#                     print(f"Background: Saved Q: {generated_question}")
#                 else:
#                     print(f"Background: Invalid Q for {need_theme}/{q_item}: {generated_question}")
#             except Exception as e:
#                 print(f"Background: Error generating/saving Q for {need_theme}/{q_item}: {e}")

#         # (オプション) 初期フェーズ完了フラグをDBで更新
#         if is_initial_phase and all_generated_questions_text: # 質問が生成されたら初期フェーズ完了とみなす
#             user_to_update = await crud.get_user(db, user_id)
#             if user_to_update:
#                 # Userモデルに system_init_completed のような属性があると仮定
#                 setattr(user_to_update, 'system_init_completed', True)
#                 await db.commit()
#                 print(f"Background: User {user_id} system_init_completed set to True.")

#         print(f"Background task for user {user_id}, theme {need_theme} completed. Generated: {len(all_generated_questions_text)} questions.")


# @ai_question_router.post("/make", response_model=QuestionMakeResponse, status_code=status.HTTP_202_ACCEPTED)
# async def question_make(
#     context_hello: QuTicket, # QuTicket に thread_id を含めるように修正
#     request: Request,
#     background_tasks: BackgroundTasks,
#     db: AsyncSession = Depends(get_db), # system_init_status を取得するためにDBセッションを使用
#     current_user: models.User = Depends(get_current_user_mock) # 認証
# ):
#     if context_hello.need_theme == "Not Found Theme":
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="need_theme is required.")
#     if current_user.user_id != context_hello.user_id: # 認可チェック
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted.")

#     server_data = get_server_host_data(request=request)
#     base_url = server_data["base_url"]
#     internal_api_headers = {"Content-Type": "application/json"}

#     # ユーザーの system_init 状態をDBから取得
#     user_db_info = await crud.get_user(db, user_id=context_hello.user_id)
#     if not user_db_info:
#         raise HTTPException(status_code=404, detail="User not found to check init status.")
#     # Userモデルに system_init_completed: bool カラムがあると仮定
#     is_initial_phase_for_user = not getattr(user_db_info, 'system_init_completed', False)

#     background_tasks.add_task(
#         generate_questions_in_background,
#         AsyncSessionLocal, # DBセッションファクトリを渡す
#         context_hello.user_id,
#         context_hello.thread_id, # QuTicket から thread_id を取得
#         context_hello.need_theme,
#         is_initial_phase_for_user,
#         base_url,
#         internal_api_headers
#     )

#     return QuestionMakeResponse(
#         status="processing_initiated",
#         message=f"Question generation for theme '{context_hello.need_theme}' for user {context_hello.user_id} has been initiated."
#     )

api_concurrecy_limiter = asyncio.Semaphore(4)
@ai_question_router.post("/ask")
async def ask_reply(ticket:question_ticket_go):
    async with api_concurrecy_limiter:
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

@ai_question_router.post("/user_answer")
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
ai_router.include_router(ai_question_router)
# db_router.include_router(api_use_db.router)


app.include_router(ai_router)
app.include_router(api_use_db.router)
app.include_router(outh_router)