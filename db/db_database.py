from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base


# 多分パス参照のようなものだと思う
DATABASE_URL = "sqlite+aiosqlite:///./test.db"  # SQLiteの非同期接続URL

async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQLの実行をログに出力するそうなrの?
    # connect_args={"check_same_thread": False} # SQLiteの場合に必要だったが、aiosqliteでは通常不要　なんでいらないのかは知らん
)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession
)

# SQLAlchemyモデルのベースクラス　多分書き込みとかのcrudに必要???
Base = declarative_base()


# DB セッションを取得する時の依存関係 多分使う時にどのクラスから継承しているとかの依存関係を示すやつ?
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


