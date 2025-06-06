# from . import crud, models

# api で何を参照できるようにしましょうか/
# app/routers/threads.py (例)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from db import crud, models, schemas
from db.db_database import get_db
# from ..auth import get_current_active_user # 認証用 (今回は省略)

router = APIRouter(
    prefix="/threads",
    tags=["threads"],
    responses={404: {"description": "Not found"}},
)

# 仮の認証済みユーザー取得関数 (実際にはJWT認証などを実装)
async def get_current_user_mock() -> models.User:
    # テスト用に固定ユーザーを返す (実際には認証処理が必要)
    # このユーザーがDBに存在している前提
    return models.User(user_id=1, email="test@example.com", name="Test User", password_hash="dummy")


# api_use_db.py (またはスレッドのルーターファイル)
@router.post("/", response_model=schemas.Thread, status_code=status.HTTP_201_CREATED)
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


@router.get("/{thread_id}", response_model=schemas.Thread)
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

@router.post("/{thread_id}/messages/", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
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

# 他のエンドポイント (スレッド一覧、メッセージ編集など) も同様に作成