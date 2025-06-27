from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from google.oauth2 import id_token
from google.auth.transport import requests
from typing import Optional
import db.models

# .envファイルから環境変数を読み込む
from dotenv import load_dotenv
load_dotenv()
import os

from db.api_use_db import create_new_user

# --- 他のモジュールから必要なものをインポート ---
# (auth/utils.py や db/crud.py など、ファイルを分割している前提)
# 今回は説明のために、このファイル内に必要な関数を書いていきます。

from pydantic import BaseModel

# --- 設定 ---
# 環境変数から読み込む。なければデフォルト値を使う
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
if not GOOGLE_CLIENT_ID:
    raise ValueError("GOOGLE_CLIENT_ID is not set in the environment variables or .env file")

# --- FastAPIアプリの初期化 ---
# app = FastAPI()

outh_router = APIRouter(
    prefix="/outh",
    tags=["outh"],
    responses={404: {"description": "Not found"}},
)

# origins = ["*"] # 開発中は "*" でOK。本番ではフロントエンドのURLに限定する

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# --- APIで使うデータモデル (Pydantic) ---

# Googleトークンを受け取るためのリクエストボディモデル
class GoogleToken(BaseModel):
    token: str

# ログイン成功時に返すレスポンスモデル
class LoginResponse(BaseModel):
    message: str
    user_id: int
    user_email: str
    is_new_user: bool
    # ここではGoogleのIDトークンをそのまま使うので、独自トークンは返さない

# # --- データベース関連 (本来は db/ フォルダに分ける) ---
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy import Column, Integer, String

# DATABASE_URL = "sqlite+aiosqlite:///./test.db"  # 非同期SQLite
# async_engine = create_async_engine(DATABASE_URL, echo=True)
# AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)
# Base = declarative_base()

# Userモデル (本来は models.py に)
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     google_id = Column(String, unique=True, index=True) # Googleのsub
#     email = Column(String, unique=True, index=True, nullable=False)
#     name = Column(String)

# DBセッションを取得するための依存関係
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# アプリケーション起動時にテーブルを作成
@app.on_event("startup")
async def startup_event():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


--- CRUD処理 (本来は crud.py に) ---
from sqlalchemy.future import select

async def get_user_by_google_id(db: AsyncSession, google_id: str):
    result = await db.execute(select(User).filter(User.google_id == google_id))
    return result.scalars().first()

async def create_user_from_google(db: AsyncSession, id_info: dict):
    # new_user = User(
    #     google_id=id_info['sub'],
    #     email=id_info['email'],
    #     name=id_info.get('name')
    # )
    # db.add(new_user)
    # await db.commit()
    # await db.refresh(new_user)
    # return new_user
    create_new_user



# --- 認証APIエンドポイント ---

# ルーターを作成してAPIを整理する
auth_router = APIRouter(
    prefix="/auth", # このルーターのエンドポイントはすべて /auth で始まる
    tags=["Authentication"],
)

@auth_router.post("/google/login", response_model=LoginResponse)
async def login_with_google(
    google_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    フロントエンドから受け取ったGoogleのIDトークンを検証し、
    ユーザーをDBに登録または検索する。
    """
    try:
        # Google IDトークンを検証
        id_info = id_token.verify_oauth2_token(
            google_token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        google_user_id = id_info['sub']

        # ユーザーが既に存在するかDBで確認
        user = await get_user_by_google_id(db, google_id=google_user_id)
        
        is_new_user = False
        if not user:
            # 存在しない場合は新規ユーザーとして作成
            user = await create_user_from_google(db, id_info=id_info)
            is_new_user = True
        
        # ログイン成功。フロントエンドにユーザー情報などを返す。
        # フロントエンドはこのレスポンスを受け取り、チャット画面に進むなどの処理を行う。
        return LoginResponse(
            message="Successfully authenticated with Google.",
            user_id=user.id,
            user_email=user.email,
            is_new_user=is_new_user
        )

    except ValueError:
        # トークンが無効な場合
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token."
        )
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )




# --- サンプル：保護されたエンドポイント ---
# このエンドポイントにアクセスするには、有効なGoogle IDトークンが必要

from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/") # ダミー

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
    リクエストの `Authorization: Bearer <token>` ヘッダーからGoogle IDトークンを検証し、
    対応するユーザーを返すための依存関係。
    """
    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        google_user_id = id_info.get("sub")
        if not google_user_id:
            raise ValueError("sub not found in token")
        user = await get_user_by_google_id(db, google_id=google_user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found in our database.")
        return user
    except ValueError:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/users/me")
async def read_users_me(current_user:db.models.User = Depends(get_current_user)):
    """認証されたユーザー自身の情報を返すサンプルエンドポイント"""
    return current_user