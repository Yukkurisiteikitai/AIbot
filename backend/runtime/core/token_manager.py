from typing import Dict, Any, Optional
import hashlib
import json
import time

class TokenManager:
    def __init__(self):
        self.token_map: Dict[str, Dict[str, Any]] = {}
        self.reverse_map: Dict[str, str] = {}
        self.token_metadata: Dict[str, Dict[str, Any]] = {}
        
    def encode(self, data: Dict[str, Any]) -> str:
        # データのハッシュを生成
        data_str = json.dumps(data, sort_keys=True)
        token = hashlib.sha256(data_str.encode()).hexdigest()[:16]
        
        # トークンとメタデータを保存
        self.token_map[token] = data
        self.token_metadata[token] = {
            'created_at': time.time(),
            'last_accessed': time.time(),
            'access_count': 0
        }
        
        return token
        
    def decode(self, token: str) -> Optional[Dict[str, Any]]:
        if token in self.token_map:
            # アクセス統計を更新
            self.token_metadata[token]['last_accessed'] = time.time()
            self.token_metadata[token]['access_count'] += 1
            return self.token_map[token]
        return None
        
    def get_metadata(self, token: str) -> Optional[Dict[str, Any]]:
        return self.token_metadata.get(token)