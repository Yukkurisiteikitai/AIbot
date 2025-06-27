from pathlib import Path
from typing import Dict, Any
import yaml
import logging


# testCode ------------------------------------
# Config クラスの修正
class Config:
    def __init__(self, config_path: str = "/Users/yuuto/Desktop/nowProject/AIbot/config.yaml"):
        self.config_path = Path(config_path) # Pathオブジェクトとして扱う
        if not self.config_path.is_file():
            # self.config が初期化される前にエラーを出す可能性があるので logging はここでは使わない
            print(f"ERROR: Config file not found: {self.config_path}")
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        self._config_data: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)


    
    @property
    def model_path_str(self) -> str: # 文字列で返すように変更
        try:
            # config.yaml 内の実際の model_path の場所に合わせて調整してください
            # 例: self._config_data['llama']['model_path']
            # 現在のコードの llama_config プロパティで参照している runtime_config 内に model_path があると仮定
            # もし config.yaml の llama.model_path にあるならそちらを参照
            # ここでは、config.yaml の 'llama'.'runtime_config'.'model_path' にあると仮定して取得します
            # 実際のYAML構造に合わせてください。
            # 前回のログから、config.yamlの'llama'.'runtime_config'.'model_path'にパスがあると推測されます。
            # ただし、LlamaHandlerに渡す設定は runtime_config 全体なので、
            # model_path は別途 runtime_config にマージする必要があります。
            return str(self._config_data['llama']['runtime_config']['model_path'])
        except KeyError as e:
            print(f"ERROR: 'llama.runtime_config.model_path' or a part of it not found in config YAML. Error: {e}")
            raise

    @property
    def llama_handler_config(self) -> Dict[str, Any]: # 新しいプロパティ名
        try:
            # runtime_config をベースに、model_path を絶対パス文字列として確実に含める
            config_for_handler = self._config_data['llama']['runtime_config'].copy()
            # model_path が runtime_config 内にすでにある場合はそれを使う。
            # なければ、別途定義された場所から取得して追加する。
            # あなたの config.yaml では llama.runtime_config.model_path にあるようなので、そのままで良いはず。
            # 念のため、絶対パスに変換し、文字列であることを保証する。
            model_path_value = config_for_handler.get('model_path')
            if not model_path_value:
                # もし runtime_config に model_path がなければ、別の場所から取得するロジックが必要
                # ここではエラーとするか、別の場所 (例: self._config_data['llama']['model_path']) から取得
                raise KeyError("'model_path' not found within llama.runtime_config in YAML.")

            # 相対パスの場合、config.yaml の場所を基準に絶対パスに変換することを検討
            base_dir = self.config_path.parent
            absolute_model_path = base_dir / Path(model_path_value)
            if not absolute_model_path.is_file():
                 print(f"WARNING: Model file at resolved path {absolute_model_path} not found. Checking original path: {model_path_value}")
                 if not Path(model_path_value).is_file(): # 元のパスでも確認
                     raise FileNotFoundError(f"Model file not found at {model_path_value} or {absolute_model_path}")
                 config_for_handler['model_path'] = str(Path(model_path_value).resolve()) # 元のパスを絶対パス化
            else:
                 config_for_handler['model_path'] = str(absolute_model_path.resolve())

            return config_for_handler
        except KeyError as e:
            print(f"ERROR: 'llama.runtime_config' or a part of it not found in config YAML. Error: {e}")
            raise