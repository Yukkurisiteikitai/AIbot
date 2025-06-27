from typing import Dict, Any, Optional
import time
from collections import OrderedDict

class CacheManager:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
        self.access_count: Dict[str, int] = {}
        
    def get(self, key: str) -> Optional[str]:
        if key in self.cache:
            # アクセスカウントを更新
            self.access_count[key] += 1
            # 最近アクセスされたアイテムを最後に移動
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
        
    def put(self, key: str, value: str):
        if len(self.cache) >= self.max_size:
            self._evict_least_used()
            
        self.cache[key] = value
        self.access_count[key] = 1
        
    def _evict_least_used(self):
        # 最も使用頻度の低いアイテムを削除
        min_key = min(self.access_count.items(), key=lambda x: x[1])[0]
        del self.cache[min_key]
        del self.access_count[min_key]