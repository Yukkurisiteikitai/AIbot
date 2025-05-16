from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class ImportanceLevel(Enum):
    """重要度レベルを表す列挙型"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class Status(Enum):
    """夢や目標の現在の状態を表す列挙型"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    ON_HOLD = "on_hold"


class SensitivityLevel(Enum):
    """情報の機密性レベルを表す列挙型"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Category(Enum):
    """夢や目標のカテゴリを表す列挙型"""
    CAREER = "キャリア"
    EDUCATION = "教育"
    PERSONAL = "個人"
    FAMILY = "家族"
    HEALTH = "健康"
    FINANCIAL = "財務"
    TRAVEL = "旅行"
    HOBBY = "趣味"
    OTHER = "その他"

class DataSource(Enum):
    """データがどこから書き込まれたのかを記録する"""
    AI = "ai"
    USER = "user"
    AI_SUMMARY_USER = "ai_summary_user"

@dataclass
class ConcreteStep:
    """具体的に取った行動を表すデータクラス"""
    description: str = field(default_factory=str,metadata={"description": "取った行動の詳細説明"})
    date: str = field(default_factory=str,metadata={"description": "行動を取った日付（YYYY-MM-DD形式）"})


@dataclass
class EstimatedPeriod:
    """最初に思いついた時期の推定情報を表すデータクラス"""
    start_age: int = field(metadata={"description": "開始年齢"})
    end_age: int = field(metadata={"description": "終了年齢"})
    developmental_stage_estimation: str = field(default_factory=str,metadata={"description": "発達段階の推定"})


@dataclass
class AspirationDream:
    """夢や目標の詳細情報を表すデータクラス"""

    # --- デフォルト値なしのフィールド (必須項目と判断されるもの) ---
    id: str = field(metadata={"description": "夢や目標の一意識別子"})
    entry_date: str = field(metadata={"description": "記録日（YYYY-MM-DD形式）"}) # または datetime
    last_updated: str = field(metadata={"description": "最終更新日（YYYY-MM-DD形式）"}) # または datetime
    source: DataSource = field(metadata={"description": "情報源"}) # Enum化を推奨
    description: str = field(metadata={"description": "夢や目標の詳細な説明"})
    category: Category = field(metadata={"description": "夢や目標のカテゴリ"}) # from_dictで対処するため、ここではデフォルトなしでも可

    # --- デフォルト値ありのフィールド (任意項目と判断されるもの) ---
    user_importance: ImportanceLevel = field(default=ImportanceLevel.MEDIUM, metadata={"description": "ユーザーにとっての重要度"})
    status: Status = field(default=Status.ACTIVE, metadata={"description": "現在の状態"})
    sensitivity_level: SensitivityLevel = field(default=SensitivityLevel.MEDIUM, metadata={"description": "情報の機密性レベル"})
    user_notes: Optional[str] = field(default=None, metadata={"description": "ユーザーのメモや補足情報"})
    linked_episode_ids: List[str] = field(default_factory=list, metadata={"description": "関連するエピソードのID"})
    motivation_source_description: Optional[str] = field(default=None, metadata={"description": "動機の源についての説明"})
    first_conceived_date_text: Optional[str] = field(default=None, metadata={"description": "最初に思いついた時期のテキスト表現"})
    estimated_first_conceived_period: Optional[EstimatedPeriod] = field(default=None, metadata={"description": "最初に思いついた時期の詳細情報"}) # これ自体がOptional
    target_completion_date_text: Optional[str] = field(default=None, metadata={"description": "目標達成予定時期のテキスト表現"})
    concrete_steps_taken: List[ConcreteStep] = field(default_factory=list, metadata={"description": "具体的に取った行動のリスト"})
    perceived_obstacles: List[str] = field(default_factory=list, metadata={"description": "認識している障害や課題"})
    required_resources_or_skills: List[str] = field(default_factory=list, metadata={"description": "必要なリソースやスキル"})
    expected_impact_or_outcome: Optional[str] = field(default=None, metadata={"description": "期待される影響や結果"})
    underlying_values_links: List[str] = field(default_factory=list, metadata={"description": "根底にある価値観へのリンク"})
    related_complex_or_trauma_links: Optional[List[str]] = field(default_factory=list, metadata={"description": "関連するトラウマや複雑な問題へのリンク"})
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AspirationDream':
        """辞書からAspirationDreamインスタンスを生成するクラスメソッド"""
        # Enumに変換する必要のあるフィールドを処理
        user_importance = ImportanceLevel(data.get('user_importance', 'medium'))
        status = Status(data.get('status', 'active'))
        sensitivity_level = SensitivityLevel(data.get('sensitivity_level', 'medium'))
        
        # カテゴリを処理（既存のカテゴリに一致しない場合はOTHERを使用）
        try:
            category = Category(data.get('category', 'その他'))
        except ValueError:
            category = Category.OTHER
        
        # 推定期間を処理
        estimated_period_data = data.get('estimated_first_conceived_period', {})
        estimated_period = EstimatedPeriod(
            start_age=estimated_period_data.get('start_age', 0),
            end_age=estimated_period_data.get('end_age', 0),
            developmental_stage_estimation=estimated_period_data.get('developmental_stage_estimation', '')
        )
        
        # 具体的なステップを処理
        concrete_steps_data = data.get('concrete_steps_taken', [])
        concrete_steps = [
            ConcreteStep(
                description=step.get('description', ''),
                date=step.get('date', '')
            ) for step in concrete_steps_data
        ]
        
        # メインのAspirationDreamインスタンスを作成
        return cls(
            id=data.get('id', ''),
            entry_date=data.get('entry_date', ''),
            last_updated=data.get('last_updated', ''),
            source=data.get('source', '') or data.get('write_who', ''),  # sourceかwrite_whoのどちらかを使用
            user_importance=user_importance,
            status=status,
            sensitivity_level=sensitivity_level,
            user_notes=data.get('user_notes', ''),
            linked_episode_ids=data.get('linked_episode_ids', []),
            description=data.get('description', ''),
            category=category,
            motivation_source_description=data.get('motivation_source_description', ''),
            first_conceived_date_text=data.get('first_conceived_date_text', ''),
            estimated_first_conceived_period=estimated_period,
            target_completion_date_text=data.get('target_completion_date_text', ''),
            concrete_steps_taken=concrete_steps,
            perceived_obstacles=data.get('perceived_obstacles', []),
            required_resources_or_skills=data.get('required_resources_or_skills', []),
            expected_impact_or_outcome=data.get('expected_impact_or_outcome', ''),
            underlying_values_links=data.get('underlying_values_links', []),
            related_complex_or_trauma_links=data.get('related_complex_or_trauma_links')
        )


@dataclass
class AspirationDreamsCollection:
    """夢や目標のコレクションを表すデータクラス"""
    dreams: List[AspirationDream] = field(default_factory=list, metadata={"description": "夢や目標のリスト"})
    
    def add_dream(self, dream: AspirationDream) -> None:
        """夢や目標をコレクションに追加するメソッド"""
        self.dreams.append(dream)
    
    def get_by_id(self, dream_id: str) -> Optional[AspirationDream]:
        """IDで夢や目標を検索するメソッド"""
        for dream in self.dreams:
            if dream.id == dream_id:
                return dream
        return None
    
    def get_by_category(self, category: Category) -> List[AspirationDream]:
        """カテゴリで夢や目標をフィルタリングするメソッド"""
        return [dream for dream in self.dreams if dream.category == category]
    
    def get_by_importance(self, importance: ImportanceLevel) -> List[AspirationDream]:
        """重要度で夢や目標をフィルタリングするメソッド"""
        return [dream for dream in self.dreams if dream.user_importance == importance]
    
    def get_by_status(self, status: Status) -> List[AspirationDream]:
        """状態で夢や目標をフィルタリングするメソッド"""
        return [dream for dream in self.dreams if dream.status == status]


# サンプルデータから変換してみる例
def parse_aspiration_dreams_sample(json_data: Dict[str, Any]) -> AspirationDreamsCollection:
    """JSONデータからAspirationDreamsCollectionを生成する関数"""
    collection = AspirationDreamsCollection()
    
    # JSONデータの構造が少し特殊なため、適切に取り出す
    dreams_data = []
    if isinstance(json_data, dict) and any(key == "" for key in json_data.keys()):
        for key, value in json_data.items():
            if isinstance(value, list):
                dreams_data = value
                break
    
    for dream_data in dreams_data:
        try:
            dream = AspirationDream.from_dict(dream_data)
            collection.add_dream(dream)
        except Exception as e:
            print(f"Error processing dream data: {e}")
    
    return collection


# 使用例
if __name__ == "__main__":
    import json
    
    # 問題のあるJSON文字列を修正
    json_str = """{
        "": [
            {
                "id": "ad_001",
                "entry_date": "YYYY-MM-DD",
                "last_updated": "YYYY-MM-DD",
                "write_who": "dialogue_extraction",
                "user_importance": "very_high",
                "status": "active",
                "sensitivity_level": "medium",
                "user_notes": "これは絶対に実現したい夢だ。",
                "linked_episode_ids": ["ep_xxx", "ep_yyy"],
                "description": "自分の経験を活かして、社会貢献できる事業を立ち上げたい。",
                "category": "キャリア",
                "motivation_source_description": "過去のボランティア経験と、現在のスキルセットの組み合わせから、多くの人を助けたいという思いが強くなった。",
                "first_conceived_date_text": "大学卒業の頃",
                "estimated_first_conceived_period": {
                    "start_age": 22,
                    "end_age": 23,
                    "developmental_stage_estimation": "青年期後期"
                },
                "target_completion_date_text": "5年以内",
                "concrete_steps_taken": [
                    {
                        "description": "関連分野のビジネス書を10冊読んだ。",
                        "date": "YYYY-MM-DD"
                    },
                    {
                        "description": "起業セミナーに参加した。",
                        "date": "YYYY-MM-DD"
                    }
                ],
                "perceived_obstacles": [
                    "資金調達の難しさ",
                    "事業計画の具体化",
                    "時間的な制約"
                ],
                "required_resources_or_skills": [
                    "リーダーシップ",
                    "マーケティング知識",
                    "資金"
                ],
                "expected_impact_or_outcome": "多くの人のQOL向上に貢献し、自分自身も大きな達成感を得る。",
                "underlying_values_links": [
                    "bv_social_contribution",
                    "bv_self_growth"
                ],
                "related_complex_or_trauma_links": null
            }
        ]
    }"""
    
    json_data = json.loads(json_str)
    collection = parse_aspiration_dreams_sample(json_data)
    
    # コレクションの内容を確認
    for dream in collection.dreams:
        print(f"ID: {dream.id}")
        print(f"説明: {dream.description}")
        print(f"カテゴリ: {dream.category.value}")
        print(f"重要度: {dream.user_importance.value}")
        print(f"状態: {dream.status.value}")
        print("---")