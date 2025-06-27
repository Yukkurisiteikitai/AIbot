import http.client
import json
import urllib.parse # URLエンコード用 (GETリクエストのクエリパラメータなど)
from typing import Dict, Any, Optional, Tuple

# --- 設定 ---
BASE_URL = "localhost"  # FastAPIサーバーのホスト
PORT = 49604            # FastAPIサーバーのポート
DEFAULT_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

# --- ヘルパー関数 ---
def make_request(
    method: str,
    path: str,
    body: Optional[Dict[str, Any]] = None,
    query_params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Tuple[int, Optional[Dict[str, Any]], Optional[str]]:
    """
    指定されたHTTPメソッド、パス、ボディ、ヘッダーでリクエストを送信する。

    Args:
        method: HTTPメソッド (GET, POST, PUT, DELETEなど)
        path: APIエンドポイントのパス (例: "/db/users/")
        body: リクエストボディとなる辞書 (JSONにシリアライズされる)
        query_params: GETリクエストのクエリパラメータとなる辞書
        headers: リクエストヘッダーの辞書

    Returns:
        タプル (ステータスコード, レスポンスボディ(JSON辞書 or None), エラーメッセージ(str or None))
    """
    conn = None
    full_path = path
    request_body_str = None
    actual_headers = DEFAULT_HEADERS.copy()
    if headers:
        actual_headers.update(headers)

    if query_params:
        full_path += "?" + urllib.parse.urlencode(query_params)

    if body is not None:
        try:
            request_body_str = json.dumps(body)
        except TypeError as e:
            print(f"Error serializing body to JSON: {e}")
            return 0, None, f"JSON serialization error: {e}"
    else:
        # GETやDELETEでContent-Length: 0を期待されることがあるので、明示的に空にする
        if method in ["POST", "PUT", "PATCH"]: # ボディが必須なメソッドでbodyがNoneならエラーにしてもよい
             pass # Content-Typeがある場合、空のボディを送ることもある
        # else:
        #     if "Content-Type" in actual_headers: # ボディがないのにContent-Typeがあるのはおかしい場合がある
        #         del actual_headers["Content-Type"]
        pass


    print(f"\n--- Request ---")
    print(f"Method: {method}")
    print(f"Path: {full_path}")
    print(f"Headers: {actual_headers}")
    if request_body_str:
        print(f"Body: {request_body_str}")

    try:
        conn = http.client.HTTPConnection(BASE_URL, PORT)
        conn.request(method, full_path, body=request_body_str, headers=actual_headers)
        response = conn.getresponse()

        status_code = response.status
        response_body_bytes = response.read()
        response_body_str = response_body_bytes.decode('utf-8')

        print(f"\n--- Response ---")
        print(f"Status Code: {status_code}")
        print(f"Headers: {response.getheaders()}")
        print(f"Raw Body: {response_body_str}")

        response_json = None
        if response_body_str:
            try:
                response_json = json.loads(response_body_str)
                print(f"JSON Body: {response_json}")
            except json.JSONDecodeError:
                print("Warning: Response body is not valid JSON.")
                # JSONデコードエラーでも、ステータスコードや生ボディは有用なので返す
        return status_code, response_json, None

    except ConnectionRefusedError:
        error_msg = f"Connection refused. Is the server running at {BASE_URL}:{PORT}?"
        print(f"Error: {error_msg}")
        return 0, None, error_msg
    except http.client.HTTPException as e:
        error_msg = f"HTTPException: {e}"
        print(f"Error: {error_msg}")
        return 0, None, error_msg
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(f"Error: {error_msg}")
        return 0, None, error_msg
    finally:
        if conn:
            conn.close()

# --- テストシナリオ ---
def test_user_crud_and_question_flow():
    created_user_id = None
    created_thread_id = None
    created_question_id = None

    print("\n=== Testing User Creation (POST /db/users/) ===")
    user_payload = {
        "name": "StdLib Tester",
        "email": f"stdlib_tester_{abs(hash(id(make_request)))}@example.com", # ユニークなメールアドレス
        "password": "testpassword123"
    }
    status, data, err = make_request("POST", "/db/users/", body=user_payload)
    assert status == 201, f"User creation failed: {status} - {data or err}"
    assert data is not None and "user_id" in data, "User creation response missing user_id"
    created_user_id = data["user_id"]
    print(f"User created with ID: {created_user_id}")

    if not created_user_id:
        print("Skipping further tests as user creation failed.")
        return

    print(f"\n=== Testing Get User Details (GET /db/users/{created_user_id}) ===")
    status, data, err = make_request("GET", f"/db/users/{created_user_id}")
    assert status == 200, f"Get user failed: {status} - {data or err}"
    assert data is not None and data["email"] == user_payload["email"], "Get user data mismatch"

    print("\n=== Testing Thread Creation (POST /db/threads/) ===")
    # このAPIは get_current_user_mock に依存しているので、
    # 認証をどう扱うかがポイント。ここではモックが user_id=1 を返すと仮定。
    # もし実際の認証が必要なら、ログインAPIを叩いてトークンを取得し、ヘッダーに含める必要がある。
    # ここでは、テスト対象の create_new_thread が内部で user_id=1 を使うと想定。
    thread_payload = {
        "mode": "chat",
        "title": "Thread by StdLib Tester"
    }
    status, data, err = make_request("POST", "/db/threads/", body=thread_payload)
    assert status == 201, f"Thread creation failed: {status} - {data or err}"
    assert data is not None and "thread_id" in data, "Thread creation response missing thread_id"
    created_thread_id = data["thread_id"]
    print(f"Thread created with ID: {created_thread_id}")

    if not created_thread_id:
        print("Skipping question tests as thread creation failed.")
        return

    print(f"\n=== Testing Question Creation (POST /db/questions/users/{created_user_id}) ===")
    question_payload = {
        "question_text": "StdLibからこんにちは！調子はどうですか？",
        "reason_for_question": "Standard library test",
        "priority": 5,
        "status": "pending",
        "source": "stdlib_test_script",
        "thread_id": created_thread_id # 作成したスレッドIDを関連付ける
    }
    status, data, err = make_request("POST", f"/db/questions/users/{created_user_id}", body=question_payload)
    assert status == 201, f"Question creation failed: {status} - {data or err}"
    assert data is not None and "question_id" in data, "Question creation response missing question_id"
    created_question_id = data["question_id"]
    print(f"Question created with ID: {created_question_id}")


    print(f"\n=== Testing Get Pending Questions for User (GET /db/questions/users/{created_user_id}) ===")
    status, data, err = make_request("GET", f"/db/questions/users/{created_user_id}", query_params={"status": "pending"})
    assert status == 200, f"Get pending questions failed: {status} - {data or err}"
    assert isinstance(data, list), "Response for pending questions should be a list"
    found_question = False
    if data: # リストが空でない場合
        for q_data in data:
            if q_data.get("question_id") == created_question_id:
                assert q_data["question_text"] == question_payload["question_text"]
                found_question = True
                break
    # このテストでは上記で1件作成しているので、見つかるはず
    assert found_question, f"Created question (ID: {created_question_id}) not found in pending list for user {created_user_id}"
    print(f"Pending questions for user {created_user_id} (first 5): {data[:5] if data else 'No questions found'}")


    # --- 他のAPIエンドポイントのテストも同様に追加 ---
    # 例: メッセージ投稿
    if created_thread_id:
        print(f"\n=== Testing Add Message to Thread (POST /db/threads/{created_thread_id}/messages/) ===")
        message_payload = {
            "role": "user",
            "context": "StdLibからの最初のメッセージです！"
            # sender_user_id はAPI側で認証ユーザーから設定される想定
        }
        status, data, err = make_request("POST", f"/db/threads/{created_thread_id}/messages/", body=message_payload)
        assert status == 201, f"Add message failed: {status} - {data or err}"
        assert data is not None and "message_id" in data, "Add message response missing message_id"
        print(f"Message added with ID: {data['message_id']}")

    # 例: GET /ai/question/ (init_question)
    print(f"\n=== Testing Init Question (POST /ai/question/) ===")
    init_q_payload = {
        "user_id": str(created_user_id), # thread_tiket の user_id は str 型だったはず
        "mode": "chat"
        # thread_tiket に message フィールドが必要なら追加
    }
    status, data, err = make_request("POST", "/ai/question/", body=init_q_payload)
    assert status == 200, f"Init question failed: {status} - {data or err}" # 成功時は200のはず
    assert data is not None and "thread_id" in data and "question" in data, "Init question response format error"
    print(f"Init question response: {data}")


    print("\n\nAll basic tests completed (if no assertions failed).")

if __name__ == "__main__":
    # FastAPIサーバーを事前に起動しておく必要があります
    # 例: uvicorn main:app --port 49604
    print(f"Testing against server at {BASE_URL}:{PORT}")
    print("Make sure your FastAPI server is running before executing these tests.")
    input("Press Enter to start tests (ensure server is running)...")
    test_user_crud_and_question_flow()