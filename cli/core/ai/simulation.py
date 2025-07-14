import os
import sys
import httpx
import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from yaml import safe_load

class Reproduction:
    def __init__(self):
        self.name = "Reproduction"
        self.session_active = False
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
        """Reproductionセッションを開始"""
        print("=== Reproduction Mode ===")
        print("シンプルな質問応答モードです。'exit'で終了します。")
        
        self.session_active = True
        
        # 1. スレッド作成（シンプルなセッション管理）
        session_id = self._create_session()
        print(f"セッションID: {session_id}")
        
        # 2-6. 質問応答ループ
        self._conversation_loop()
    
    def _create_session(self) -> str:
        """セッションを作成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"reproduction_{timestamp}"
    
    def _conversation_loop(self) -> None:
        """質問応答ループ"""
        while self.session_active:
            try:
                # 2. 質問の開始
                user_input = input("\n> ").strip()
                
                # 6. 終了をexitで宣言
                if user_input.lower() == 'exit':
                    self._end_session()
                    break
                
                if not user_input:
                    continue
                
                # 3. 質問の応答をストリーミングで受け取る
                self._generate_streaming_response(user_input)
                
                # 4. ストリーミング完了後のバイブレーション
                self._completion_notification()
                
                # 5. まだ気になることがあるなら2に戻る
                print("\n他に質問はありますか？")
                
            except KeyboardInterrupt:
                print("\n\n中断されました。")
                self._end_session()
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")
    
    def _generate_streaming_response(self, user_input: str) -> None:
        """ストリーミングレスポンス生成（実際API呼び出し）"""
        print("\nAI: ", end="", flush=True)
        
        # 非同期関数を同期的に実行
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._call_streaming_api(user_input))
        finally:
            loop.close()
        
        print()  # 改行
    
    async def _call_streaming_api(self, user_input: str) -> None:
        """ストリーミングAPIを呼び出し"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
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
                        print(f"APIエラー: {response.status_code}")
                        return
                    
                    buffer = b""
                    async for chunk in response.aiter_bytes(chunk_size=1):
                        buffer += chunk
                        
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
                                        
                                        if is_complete:
                                            break
                                            
                                except json.JSONDecodeError:
                                    continue
                                except Exception as e:
                                    continue
                        
                        await asyncio.sleep(0.001)
        
        except httpx.ConnectError:
            print(f"APIサーバーに接続できません ({self.api_base_url})")
        except Exception as e:
            print(f"API呼び出しエラー: {str(e)}")
    
    def _completion_notification(self) -> None:
        """完了通知"""
        try:
            # macOSの場合
            os.system("afplay /System/Library/Sounds/Ping.aiff 2>/dev/null")
        except:
            pass
    
    def _end_session(self) -> None:
        """セッション終了"""
        self.session_active = False
        print("Reproductionセッションを終了しました。")

if __name__ == "__main__":
    reproduction = Reproduction()
    reproduction.start_session()
