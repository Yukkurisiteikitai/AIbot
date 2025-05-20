from pathlib import Path
from typing import Dict, Any
import yaml

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config: Dict[str, Any] = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    @property
    def model_path(self) -> Path:
        return Path(self.config['llama']['model_path'])
        
    @property
    def llama_config(self) -> Dict[str, Any]:
        return self.config['llama']['runtime_config']
