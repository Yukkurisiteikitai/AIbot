from fastapi import HTTPException,Request
from pydantic import BaseModel
import httpx
from typing import Dict, Any, Optional

class thread_tiket(BaseModel):
    user_id: str
    thread_id: str = "なんもスレッドが投げられてねーよ"
    mode:str = "search"


class question_tiket(BaseModel):
    question: str = "なんも質問が投げられてねーよ"
    answer: str = "なんも回答が投げられてねーよ"




class question_ticket_go(BaseModel):
    user_id:int
    question:str
    



# utils



# --- 内部API呼び出しのためのヘルパー関数 (オプション) ---
async def call_internal_api(
    client: httpx.AsyncClient,
    method: str,
    endpoint: str, # 例: "/db/threads/"
    base_url: str, # 例: "http://localhost:49604"
    json_payload: Optional[Dict[str, Any]] = None,
    params_payload: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    内部APIを呼び出すための汎用ヘルパー。
    エラーハンドリングを含む。
    """
    try:
        url = f"{base_url}{endpoint}"
        response = await client.request(
            method,
            url,
            json=json_payload,
            params=params_payload,
            headers=headers
        )
        response.raise_for_status() # HTTPエラーがあれば例外を発生
        return response.json()
    except httpx.HTTPStatusError as e:
        error_detail = f"Internal API call to {e.request.url} failed with status {e.response.status_code}"
        try:
            error_detail += f" - Response: {e.response.json()}"
        except Exception:
            error_detail += f" - Response (text): {e.response.text}"
        # ここでログを取るのが良い
        print(f"HTTPStatusError: {error_detail}") # 実際にはロギングライブラリを使う
        raise HTTPException(status_code=500, detail="An internal API call failed.") # クライアントには汎用的なエラーを返す
    except httpx.RequestError as e:
        # ネットワーク関連のエラー
        print(f"RequestError: Internal API connection error to {e.request.url}: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable (internal API connection).") # Service Unavailable
    except Exception as e:
        print(f"Unexpected error during internal API call: {e}")
        raise HTTPException(status_code=500, detail="An unexpected internal error occurred.")

def get_server_host_data(request: Request):
    server_host = request.client.host
    server_port = request.url.port if request.url.port else (443 if request.url.scheme == "https" else 80)
    internal_api_base_url = f"{request.url.scheme}://{server_host}:{server_port}"
    return {
        "base_url":internal_api_base_url
    }