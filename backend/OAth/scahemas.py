from pydantic import BaseModel

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