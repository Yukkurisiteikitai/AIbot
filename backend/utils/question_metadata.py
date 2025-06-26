from yaml import safe_load
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from pathlib import Path

@dataclass
class QuestionMetadata:
    """質問メタデータを表すデータクラス"""
    display_name: str
    definition: str
    input_examples: List[str]
    question_prompts_for_ai: List[str]
    related_person_data_key: str
    notes: str
    original_tag_id: int

class QuestionMetadataManager:
    """質問メタデータを管理するクラス"""
    
    def __init__(self, config_path: Union[str, Path] = "configs/meta_question.yaml"):
        self.config_path = Path(config_path)
        self._config_data = self._load_config()
        self._themes = self._config_data["question_themes"]
        self._presentation_order = self._config_data["presentation_order"]
        
        # IDでの高速検索用のマッピングを作成
        self._id_to_theme_name = self._create_id_mapping()
    
    def _load_config(self) -> Dict:
        """設定ファイルを読み込む"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"設定ファイルが見つかりません: {self.config_path}")
        except Exception as e:
            raise Exception(f"設定ファイルの読み込みに失敗しました: {e}")

    def _create_id_mapping(self) -> Dict[int, str]:
        """IDからテーマ名へのマッピングを作成（高速検索用）"""
        id_mapping = {}
        for theme_name, theme_data in self._themes.items():
            original_id = theme_data.get("original_tag_id")
            if original_id is not None:
                id_mapping[original_id] = theme_name
        return id_mapping

    def _create_metadata_object(self, theme_data: Dict) -> QuestionMetadata:
        """辞書データからQuestionMetadataオブジェクトを作成"""
        return QuestionMetadata(
            display_name=theme_data["display_name"],
            definition=theme_data["definition"],
            input_examples=theme_data["input_examples"],
            question_prompts_for_ai=theme_data["question_prompts_for_ai"],
            related_person_data_key=theme_data["related_person_data_key"],
            notes=theme_data["notes"],
            original_tag_id=theme_data["original_tag_id"]
        )

    def get_by_name(self, theme_name: str) -> Optional[QuestionMetadata]:
        """テーマ名でメタデータを取得"""
        if theme_name not in self._themes:
            return None
        return self._create_metadata_object(self._themes[theme_name])
    
    def get_by_id(self, tag_id: int) -> Optional[QuestionMetadata]:
        """IDでメタデータを取得（高速検索）"""
        theme_name = self._id_to_theme_name.get(tag_id)
        if theme_name is None:
            return None
        return self._create_metadata_object(self._themes[theme_name])
    
    def get_presentation_order(self) -> List[str]:
        """プレゼンテーション順序を取得"""
        return self._presentation_order.copy()
    
    def get_all_themes(self) -> Dict[str, QuestionMetadata]:
        """すべてのテーマを取得"""
        return {
            name: self._create_metadata_object(data)
            for name, data in self._themes.items()
        }
    
    def get_ordered_themes(self) -> List[QuestionMetadata]:
        """プレゼンテーション順序でテーマを取得"""
        ordered_themes = []
        for theme_name in self._presentation_order:
            if theme_name in self._themes:
                ordered_themes.append(
                    self._create_metadata_object(self._themes[theme_name])
                )
        return ordered_themes

# 使用例
if __name__ == "__main__":
    # マネージャーの初期化
    manager = QuestionMetadataManager("configs/meta_question.yaml")
    
    # 名前で取得
    metadata = manager.get_by_name("What is you")
    if metadata:
        print(f"Display Name: {metadata.display_name}")
        print(f"Definition: {metadata.definition}")
    
    # IDで取得（高速）
    metadata = manager.get_by_id(1)
    if metadata:
        print(f"Found by ID: {metadata.display_name}")
    
    # すべてのテーマを順序付きで取得
    ordered_themes = manager.get_ordered_themes()
    for theme in ordered_themes:
        print(f"- {theme.display_name} (ID: {theme.original_tag_id})")