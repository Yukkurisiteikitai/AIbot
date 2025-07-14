import json
import os
import sys
import httpx
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from yaml import safe_load

class ThreadManager:
    def __init__(self, data_dir: str = "data/threads"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def load_thread(self, thread_id: str) -> Optional[Dict]:
        thread_file = os.path.join(self.data_dir, f"{thread_id}.json")
        if os.path.exists(thread_file):
            with open(thread_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def save_thread(self, thread_id: str, thread_data: Dict) -> None:
        thread_file = os.path.join(self.data_dir, f"{thread_id}.json")
        with open(thread_file, 'w', encoding='utf-8') as f:
            json.dump(thread_data, f, ensure_ascii=False, indent=2)
    
    def create_thread(self, thread_id: str) -> Dict:
        thread_data = {
            "id": thread_id,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "status": "active"
        }
        self.save_thread(thread_id, thread_data)
        return thread_data

class Analysis:
    def __init__(self):
        self.name = "Analysis"
        self.thread_manager = ThreadManager()
        self.current_thread_id = None
        self.current_thread = None
        self._load_config()
    
    def _load_config(self):
        """設定ファイルを読み込み"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '../../config/config.yaml')
            with open(config_path, 'r', encoding='utf-8') as f:
                config = safe_load(f)
            
            backend_config = config.get('Backend_API', {})
            self.api_base_url = backend_config.get('base_url', 'http://localhost:49604')
            self.user_id = backend_config.get('user_id', 1)
        except Exception as e:
            print(f"設定ファイル読み込みエラー: {e}")
            self.api_base_url = "http://localhost:49604"
            self.user_id = 1
    
    def start_session(self) -> None:
        """Analysisセッションを開始"""
        print("=== Analysis Mode ===")
        
        # 1. スレッドの履歴から読み込み（途中で止まった履歴があるかチェック）
        interrupted_thread = self._find_interrupted_thread()
        
        if interrupted_thread:
            print(f"途中で中断されたスレッドが見つかりました: {interrupted_thread['id']}")
            choice = input("続行しますか？ (y/n): ")
            if choice.lower() == 'y':
                self.current_thread = interrupted_thread
                self.current_thread_id = interrupted_thread['id']
            else:
                self._create_new_thread()
        else:
            # 2. ないならスレッドの新規作成
            self._create_new_thread()
        
        # 3. スレッドの会話履歴を取得・表示
        self._display_conversation_history()
        
        # 4. 対話ループ開始
        self._conversation_loop()
    
    def _find_interrupted_thread(self) -> Optional[Dict]:
        """中断されたスレッドを検索"""
        if not os.path.exists(self.thread_manager.data_dir):
            return None
        
        for filename in os.listdir(self.thread_manager.data_dir):
            if filename.endswith('.json'):
                thread_id = filename[:-5]
                thread_data = self.thread_manager.load_thread(thread_id)
                if thread_data and thread_data.get('status') == 'interrupted':
                    return thread_data
        return None
    
    def _create_new_thread(self) -> None:
        """新しいスレッドを作成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_thread_id = f"analysis_{timestamp}"
        self.current_thread = self.thread_manager.create_thread(self.current_thread_id)
        print(f"新しいスレッドを作成しました: {self.current_thread_id}")
    
    def _display_conversation_history(self) -> None:
        """会話履歴を表示"""
        if not self.current_thread['messages']:
            print("新しい会話を開始します。")
            return
        
        print("\n=== 会話履歴 ===")
        messages = self.current_thread['messages']
        
        # 最後の方から表示（一定数以上なら階層化）
        display_count = min(5, len(messages))
        recent_messages = messages[-display_count:]
        
        if len(messages) > display_count:
            print(f"... ({len(messages) - display_count}件の過去のメッセージ)")
        
        for msg in recent_messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            print(f"[{timestamp}] {role}: {content[:100]}{'...' if len(content) > 100 else ''}")
        print("================\n")
    
    def _conversation_loop(self) -> None:
        """対話ループ"""
        print("質問を入力してください（'exit'で終了）:")
        
        while True:
            try:
                # 6. 投げられた質問に回答
                user_input = input("\n> ").strip()
                
                if user_input.lower() == 'exit':
                    self._end_session()
                    break
                
                if not user_input:
                    continue
                
                # ユーザーメッセージを保存
                self._add_message('user', user_input)
                
                # 7. 生成された回答をストリーミング読み込み
                response = self._generate_streaming_response(user_input)
                
                # AIメッセージを保存
                self._add_message('assistant', response)
                
                # 8. ストリーミング完了後のバイブレーション（音で代用）
                self._completion_notification()
                
            except KeyboardInterrupt:
                print("\n\n中断されました。")
                self._mark_interrupted()
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")
    
    def _generate_streaming_response(self, user_input: str) -> str:
        """ストリーミングレスポンス生成（実際API呼び出し）"""
        print("\nAI: ", end="", flush=True)
        
        # 非同期関数を同期的に実行
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            full_response = loop.run_until_complete(self._call_streaming_api(user_input))
        finally:
            loop.close()
        
        print()  # 改行
        return full_response
    
    async def _call_streaming_api(self, user_input: str) -> str:
        """ストリーミングAPIを呼び出し"""
        full_response = ""
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # ストリーミングAPIにリクエスト送信
                payload = {
                    "user_id": self.user_id,
                    "question": user_input
                }
                
                url = f"{self.api_base_url}/ai/question/ask/stream"
                
                async with client.stream(
                    "POST", 
                    url, 
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status_code != 200:
                        error_msg = f"APIエラー: {response.status_code}"
                        print(error_msg)
                        return error_msg
                    
                    # ストリーミングデータをリアルタイムで受信
                    buffer = b""
                    async for chunk in response.aiter_bytes(chunk_size=1):
                        buffer += chunk
                        
                        # 改行で区切って処理
                        while b"\n" in buffer:
                            line_bytes, buffer = buffer.split(b"\n", 1)
                            line = line_bytes.decode('utf-8', errors='ignore').strip()
                            
                            if line.startswith("data: "):
                                try:
                                    data_str = line[6:]
                                    if data_str:
                                        data = json.loads(data_str)
                                        
                                        content = data.get("content", "")
                                        is_complete = data.get("is_complete", False)
                                        
                                        if content:
                                            print(content, end="", flush=True)
                                            full_response += content
                                        
                                        if is_complete:
                                            break
                                            
                                except json.JSONDecodeError:
                                    continue
                                except Exception as e:
                                    continue
                        
                        # 小さな遅延でストリーミング効果を向上
                        await asyncio.sleep(0.001)
        
        except httpx.ConnectError:
            error_msg = f"APIサーバーに接続できません ({self.api_base_url})"
            print(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"API呼び出しエラー: {str(e)}"
            print(error_msg)
            return error_msg
        
        return full_response if full_response else "応答が取得できませんでした。"
    
    def _add_message(self, role: str, content: str) -> None:
        """メッセージをスレッドに追加"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.current_thread['messages'].append(message)
        self.thread_manager.save_thread(self.current_thread_id, self.current_thread)
    
    def _completion_notification(self) -> None:
        """完了通知（バイブレーション代わりに音）"""
        try:
            # macOSの場合
            os.system("afplay /System/Library/Sounds/Glass.aiff 2>/dev/null")
        except:
            # 他のシステムまたはエラーの場合は無視
            pass
    
    def _mark_interrupted(self) -> None:
        """スレッドを中断状態としてマーク"""
        if self.current_thread:
            self.current_thread['status'] = 'interrupted'
            self.thread_manager.save_thread(self.current_thread_id, self.current_thread)
    
    def _end_session(self) -> None:
        """セッション終了"""
        if self.current_thread:
            self.current_thread['status'] = 'completed'
            self.thread_manager.save_thread(self.current_thread_id, self.current_thread)
        print("Analysisセッションを終了しました。")

if __name__ == "__main__":
    analysis = Analysis()
    analysis.start_session()