from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from . import crud, models, schemas
from .db_database import get_db
# from ..auth import get_current_active_user # 認証用 (今回は省略)


router = APIRouter(
    prefix="/db",
    tags=["db"],
    responses={404: {"description": "Not found"}},
)

thread_router = APIRouter(
    prefix="/threads",
    tags=["db"],
    responses={404: {"description": "Not found"}},
)
question_router = APIRouter(
    prefix="/questions",
    tags=["db"],
    responses={404: {"description": "Not found"}},
)

user_router = APIRouter(
    prefix="/users", # このルーターのプレフィックス
    tags=["Users"],  # Swagger UI でのタグ
)

# 仮の認証済みユーザー取得関数 (実際にはJWT認証などを実装)
async def get_current_user_mock() -> models.User:
    # テスト用に固定ユーザーを返す (実際には認証処理が必要)
    # このユーザーがDBに存在している前提
    return models.User(user_id=1, email="test@example.com", name="Test User", password_hash="dummy")


# api_use_db.py (またはスレッドのルーターファイル)
@thread_router.post("/", response_model=schemas.Thread, status_code=status.HTTP_201_CREATED)
async def create_new_thread(
    thread_data: schemas.ThreadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user_mock)
):
    # まずスレッド本体を作成
    created_thread_basic_info = await crud.create_thread(db=db, thread_data=thread_data, owner_user_id=current_user.user_id)
    if not created_thread_basic_info:
        raise HTTPException(status_code=400, detail="Thread could not be created")

    # 次に、リレーションシップを含めて完全にロードされたスレッドオブジェクトを取得して返す
    # これにより、レスポンスモデルのシリアライズ時に遅延読み込みが発生するのを防ぐ
    db_thread_with_relations = await crud.get_thread(db, thread_id=created_thread_basic_info.thread_id, include_messages=True)
    if not db_thread_with_relations:
        # 作成直後に見つからないのは通常ありえないが、念のため
        raise HTTPException(status_code=500, detail="Failed to retrieve created thread with details")

    return db_thread_with_relations


@thread_router.get("/{thread_id}", response_model=schemas.Thread)
async def read_thread_details(
    thread_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user_mock) # 認証済みユーザー
):
    db_thread = await crud.get_thread(db, thread_id=thread_id, include_messages=True)
    if db_thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    # ここで認可チェック: current_userがこのスレッドを閲覧する権限があるか
    if db_thread.owner_user_id != current_user.user_id:
         # 公開スレッドなどのロジックがなければアクセス拒否
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return db_thread

@thread_router.post("/{thread_id}/messages/", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
async def add_message_to_thread(
    thread_id: str,
    message_data: schemas.MessageCreate, # sender_user_idはリクエストボディに含めるか、認証情報から取る
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user_mock)
):
    db_thread = await crud.get_thread(db, thread_id=thread_id)
    if db_thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    # 認可: このユーザーがこのスレッドにメッセージを投稿できるか
    if db_thread.owner_user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to post message to this thread")

    # メッセージ送信者がリクエストユーザーであることを確認/設定
    if message_data.role == "user" and message_data.sender_user_id != current_user.user_id:
        # API設計として、sender_user_idをリクエストで受け取るか、常に認証ユーザーにするか決める
        # ここでは、もし指定されていて認証ユーザーと異なるならエラーとする例
        # もしAIがユーザーの代わりに投稿するケースなどがあれば、ロジックは変わる
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sender user ID mismatch")
        message_data.sender_user_id = current_user.user_id # 常に認証ユーザーにする場合

    db_message = await crud.create_message(db=db, message_data=message_data, thread_id=thread_id)
    return db_message

# @router.get("/question",response_model=schemas.QuestionBase,status_code=status.HTTP_201_CREATED)
# async def add_question(
#     question
# )

@question_router.get("/users/{user_id}", response_model=List[schemas.Question]) # schemas.Question は適切に定義
async def get_pending_questions_for_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user_mock) # 認証と認可
):
    # 認可: 要求しているユーザーが、指定された user_id の情報を閲覧する権限があるか
    if current_user.user_id != user_id:
        # 管理者権限など、他の条件で許可する場合もある
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    questions = await crud.get_questions_for_user_id(db, user_id=user_id, status='pending', limit=5) # 例: 5件まで
    if not questions:
        # 質問がない場合は空リストを返すか、404とするかは設計次第
        return []
    return questions

@question_router.post("/users/{user_id}", response_model=schemas.Question, status_code=status.HTTP_201_CREATED) # ★レスポンスモデルを単一のQuestionに、ステータスコードを201 (Created) に変更
async def create_question_for_user_endpoint( # ★関数名を変更し、役割を明確に
    user_id: int, # パスパラメータから取得
    question_data: schemas.QuestionCreate, # ★リクエストボディはPydanticモデルで受け取る (schemas.pyで定義)
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user_mock) # 認証と認可
):
    # 認可1: 質問を作成する権限があるか (例: current_user が管理者か、あるいは特定の条件を満たすか)
    # ここでは単純化のため、自分自身 (current_user) の user_id とパスパラメータの user_id が一致する場合のみ許可する、
    # または、current_user が質問を作成する一般的な権限を持つと仮定します。
    # 要件に応じて適切な認可ロジックを実装してください。
    if current_user.user_id != user_id: # もし特定のユーザー向けの質問を他人やAIが作成する場合、このチェックは不適切
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted to create question for this user")


    # question_data から必要な情報を抽出して crud.create_question に渡す
    # crud.create_question の引数に合わせて調整
    db_question = await crud.create_question(
        db=db,
        user_id=user_id, # パスパラメータのuser_id を使用 (この質問が誰に向けられたものか)
        question_text=question_data.question_text,
        why_question=question_data.reason_for_question,
        thread_id=question_data.thread_id, # QuestionCreateスキーマから取得
        priority=question_data.priority,   # QuestionCreateスキーマから取得
        status=question_data.status,     # QuestionCreateスキーマから取得
        source=question_data.source,     # QuestionCreateスキーマから取得
        related_message_id=question_data.related_message_id # QuestionCreateスキーマから取得
    )

    if not db_question: # 通常、crud.create_question が失敗したら例外を投げるべき
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create question")

    return db_question # 作成されたQuestionオブジェクトを返す

@question_router.get("/users/{user_id}/next", response_model=schemas.NextQuestionResponse)
async def get_next_pending_question_for_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user_mock) # 認証
):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    # データベースから次に提示すべき質問を取得 (優先度順、作成日順など)
    pending_questions = await crud.get_questions_for_user_id(db, user_id=user_id, status='pending', limit=1) # crud関数を調整

    if not pending_questions:
        return schemas.NextQuestionResponse(status="no_pending_questions", guidance="特に聞きたいことは見つかりませんでした。何かお話ししたいことはありますか？")

    next_question_db = pending_questions[0]

    # ★★★ AIロジック: 質問に対するガイダンス生成 ★★★
    # (例: next_question_db.question_text と meta_question.yaml を基にLLMで生成)
    generated_guidance = f"この質問「{next_question_db.question_text}」について、具体的なエピソードを交えながら、あなたの考えや感情を詳しく教えてください。" # 仮のガイダンス

    # 質問のステータスを 'asked' に更新し、asked_at を記録
    # (crudに関数を用意: update_question_status_and_timestamp)
    updated_question = await crud.update_question_status( # この関数をcrud.pyに作成
        db,
        question_id=next_question_db.question_id,
        new_status='asked',
        set_asked_at=True
    )
    if not updated_question:
        # 更新に失敗した場合のフォールバック
         raise HTTPException(status_code=500, detail="Failed to update question status")


    return schemas.NextQuestionResponse(
        question_id=updated_question.question_id,
        question_text=updated_question.question_text,
        guidance=generated_guidance,
        status="asked"
    )

@thread_router.post("/{thread_id}/messages/", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
async def add_message_to_thread(
    thread_id: str,
    message_data: schemas.MessageCreate, # sender_user_id, answered_question_id を含む
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user_mock)
):
    # ... (既存のスレッド存在確認、認可チェック) ...

    if message_data.role == "user":
        message_data.sender_user_id = current_user.user_id
    elif message_data.role == "assistant": # "system", "ai_question" など他の非ユーザーロールも同様に
        message_data.sender_user_id = None

    # メッセージをDBに保存
    db_message = await crud.create_message(db=db, message_data=message_data, thread_id=thread_id) # crud.create_messageもanswered_question_idを無視するように

    if message_data.answered_question_id and message_data.role == "user":
        # ユーザーが質問に回答した場合、Questionテーブルを更新
        await crud.update_question_status( # この関数をcrud.pyに作成
            db,
            question_id=message_data.answered_question_id,
            new_status='answered',
            set_answered_at=True,
            user_id_check=current_user.user_id # オプション: 回答者が質問対象者か確認
        )

        # ★★★ ここでバックグラウンドでAI処理をトリガー ★★★
        # (例: FastAPIの BackgroundTasks を使う)
        # background_tasks.add_task(process_user_answer_with_ai, db_message, current_user.user_id, thread_id)
        # process_user_answer_with_ai 関数内で、
        # - 回答の適切性チェック
        # - 不足情報・深掘り質問生成 -> crud.create_question
        # - フェーズ終了判定
        # - タグの分析結果推論 -> Episodeデータ生成
        # を行う。

    return db_message

# User API

# 仮の認証・認可関数 (実際の認証システムに置き換える)
async def get_current_active_user_mock(user_to_check: models.User = Depends(crud.get_user)) -> models.User: # 仮
    # ここでは単純にユーザーが存在すればOKとする
    if not user_to_check:
        raise HTTPException(status_code=403, detail="Not authenticated or inactive user")
    return user_to_check

async def get_admin_user_mock(current_user: models.User = Depends(get_current_active_user_mock)): # 仮
    # if not current_user.is_admin: # Userモデルにis_adminのようなフラグがあると仮定
    #     raise HTTPException(status_code=403, detail="Not enough permissions, admin required")
    return current_user


@user_router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user_data: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    db_user = await crud.get_user_by_email(db, email=user_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(db=db, user=user_data)

@user_router.get("/", response_model=List[schemas.User])
async def read_users_list(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    # current_admin_user: models.User = Depends(get_admin_user_mock) # 例: 管理者のみがユーザー一覧を閲覧可能
):
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users

# 認証について
@user_router.get("/{user_id}", response_model=schemas.User)
async def read_user_details(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user_mock) # 認証済みユーザーを取得
):
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # 認可: 自分自身の情報か、または管理者か？
    if db_user.user_id != current_user.user_id: # and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db_user

@user_router.put("/{user_id}", response_model=schemas.User)
async def update_existing_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user_mock)
):
    # 認可: 自分自身の情報か、または管理者か？
    if user_id != current_user.user_id: # and not current_user.is_admin:
         raise HTTPException(status_code=403, detail="Not enough permissions to update this user")

    db_user = await crud.update_user(db, user_id=user_id, user_update_data=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@user_router.delete("/{user_id}", response_model=schemas.User) # 削除成功時は通常 204 No Content を返すか、削除されたリソースを返す
async def remove_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user_mock) # または管理者
):
    # 認可: 自分自身のアカウント削除か、または管理者か？
    if user_id != current_user.user_id: # and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions to delete this user")

    db_user = await crud.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user # または status_code=204 でボディなし




# deploy
router.include_router(question_router)
router.include_router(thread_router)
router.include_router(user_router)