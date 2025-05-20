# person_data_format/tags/aspiration_dream.py
from dataclasses import dataclass, field, asdict as dataclass_asdict # asdictをインポート
from typing import List, Optional, Dict, Any
from datetime import datetime

# ..common_typesから必要なEnumをインポート
from ..common_types import ImportanceLevel, Status, SensitivityLevel, DataSource, AspirationCategory
# ..base_dataから基底クラスとヘルパーをインポート
from ..base_data import BaseDataEntry, get_enum_value, parse_datetime_optional, datetime_to_iso_optional

@dataclass
class ConcreteStep:
    """具体的に取った行動を表すデータクラス"""
    description: str = field(default="", metadata={"description": "取った行動の詳細説明"})
    date: Optional[datetime] = field(default=None, metadata={"description": "行動を取った日付 (UTC)"}) # datetime推奨
    linked_action_episode_id: Optional[str] = field(default=None, metadata={"description": "この行動が記録されている具体的なエピソードID"})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "date": datetime_to_iso_optional(self.date),
            "linked_action_episode_id": self.linked_action_episode_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConcreteStep':
        return cls(
            description=data.get('description', ''),
            date=parse_datetime_optional(data.get('date')),
            linked_action_episode_id=data.get('linked_action_episode_id')
        )

@dataclass
class EstimatedPeriod:
    """最初に思いついた時期の推定情報を表すデータクラス"""
    start_age: Optional[int] = field(default=None, metadata={"description": "開始年齢"})
    end_age: Optional[int] = field(default=None, metadata={"description": "終了年齢"})
    developmental_stage_estimation: Optional[str] = field(default=None, metadata={"description": "発達段階の推定"})

    def to_dict(self) -> Dict[str, Any]:
        return dataclass_asdict(self) # シンプルなdataclassならasdictで十分

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EstimatedPeriod':
        return cls(
            start_age=data.get('start_age'),
            end_age=data.get('end_age'),
            developmental_stage_estimation=data.get('developmental_stage_estimation')
        )

@dataclass
class AspirationDreamValueLink: # underlying_values_links の要素の型
    value_entry_id: str = field(metadata={"description": "関連する信念・価値観のID"})
    relevance_description: Optional[str] = field(default=None, metadata={"description": "どのように関連しているかの簡単な説明"})

    def to_dict(self) -> Dict[str, Any]: return dataclass_asdict(self)
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AspirationDreamValueLink':
        return cls(value_entry_id=data.get('value_entry_id',''), relevance_description=data.get('relevance_description'))

@dataclass
class AspirationDreamTraumaLink: # related_complex_or_trauma_links の要素の型
    complex_trauma_entry_id: str = field(metadata={"description": "関連するコンプレックス・トラウマのID"})
    relationship_description: Optional[str] = field(default=None, metadata={"description": "関連の性質"})

    def to_dict(self) -> Dict[str, Any]: return dataclass_asdict(self)
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AspirationDreamTraumaLink':
        return cls(complex_trauma_entry_id=data.get('complex_trauma_entry_id',''), relationship_description=data.get('relationship_description'))


@dataclass
class AspirationDream(BaseDataEntry):
    """夢や目標の詳細情報を表すデータクラス"""
    # --- AspirationDream固有のフィールド ---
    description: str = field(metadata={"description": "夢や目標の詳細な説明"}) # 必須
    category: AspirationCategory = field(default=AspirationCategory.OTHER, metadata={"description": "夢や目標のカテゴリ"})

    motivation_source_description: Optional[str] = field(default=None, metadata={"description": "動機の源についての説明"})
    first_conceived_date_text: Optional[str] = field(default=None, metadata={"description": "最初に思いついた時期のテキスト表現"})
    estimated_first_conceived_period: Optional[EstimatedPeriod] = field(default=None, metadata={"description": "最初に思いついた時期の詳細情報"})
    target_completion_date_text: Optional[str] = field(default=None, metadata={"description": "目標達成予定時期のテキスト表現"})
    concrete_steps_taken_summary: List[ConcreteStep] = field(default_factory=list, metadata={"description": "主要な行動の要約リスト"})
    perceived_obstacles_summary: List[str] = field(default_factory=list, metadata={"description": "主な障害のリスト"})
    required_resources_or_skills_summary: List[str] = field(default_factory=list, metadata={"description": "主要なリソースやスキルのリスト"})
    expected_impact_or_outcome_description: Optional[str] = field(default=None, metadata={"description": "期待される影響や結果の記述"})
    underlying_values_links: List[AspirationDreamValueLink] = field(default_factory=list, metadata={"description": "根底にある価値観へのリンク"})
    related_complex_or_trauma_links: List[AspirationDreamTraumaLink] = field(default_factory=list, metadata={"description": "関連するトラウマや複雑な問題へのリンク"})

    def __post_init__(self): # 必須フィールドの簡易チェック (より厳密なバリデーションは別途)
        if not self.id: raise ValueError("AspirationDream: 'id' is required.")
        if not self.entry_date: raise ValueError("AspirationDream: 'entry_date' is required.")
        if not self.last_updated: raise ValueError("AspirationDream: 'last_updated' is required.")
        if not self.source: raise ValueError("AspirationDream: 'source' is required.")
        if not self.description: raise ValueError("AspirationDream: 'description' is required.")


    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AspirationDream':
        # まず基底クラスのフィールドを初期化する辞書を作成
        # (または、BaseDataEntryにfrom_dictを作成し、それを呼び出す形でも良い)
        # この例では、必要なフィールドを直接渡す形を取る
        base_args = {
            'id': data.get('id', ''), # ここでUUID生成などのデフォルト処理も検討
            'entry_date': parse_datetime_optional(data.get('entry_date')) or datetime.utcnow(),
            'last_updated': parse_datetime_optional(data.get('last_updated')) or datetime.utcnow(),
            'source': get_enum_value(DataSource, data.get('source'), DataSource.UNKNOWN),
            'status': get_enum_value(Status, data.get('status'), Status.ACTIVE),
            'user_importance': get_enum_value(ImportanceLevel, data.get('user_importance'), ImportanceLevel.NOT_SET),
            'sensitivity_level': get_enum_value(SensitivityLevel, data.get('sensitivity_level'), SensitivityLevel.MEDIUM),
            'user_notes': data.get('user_notes'),
            'linked_episode_ids': data.get('linked_episode_ids', [])
        }

        # AspirationDream固有のフィールド
        description = data.get('description', '') # 必須なので空は望ましくないが、呼び出し側でケア
        category = get_enum_value(AspirationCategory, data.get('category'), AspirationCategory.OTHER)
        motivation_source_description = data.get('motivation_source_description')
        first_conceived_date_text = data.get('first_conceived_date_text')

        ep_data = data.get('estimated_first_conceived_period')
        estimated_first_conceived_period = EstimatedPeriod.from_dict(ep_data) if ep_data else None

        target_completion_date_text = data.get('target_completion_date_text')

        concrete_steps_list = [ConcreteStep.from_dict(cs) for cs in data.get('concrete_steps_taken_summary', [])]
        perceived_obstacles_list = data.get('perceived_obstacles_summary', [])
        required_resources_list = data.get('required_resources_or_skills_summary', [])
        expected_impact = data.get('expected_impact_or_outcome_description')

        uv_links_list = [AspirationDreamValueLink.from_dict(uvl) for uvl in data.get('underlying_values_links', [])]
        rct_links_list = [AspirationDreamTraumaLink.from_dict(rctl) for rctl in data.get('related_complex_or_trauma_links', [])]


        return cls(
            **base_args, # 基底クラスの引数を展開
            description=description,
            category=category,
            motivation_source_description=motivation_source_description,
            first_conceived_date_text=first_conceived_date_text,
            estimated_first_conceived_period=estimated_first_conceived_period,
            target_completion_date_text=target_completion_date_text,
            concrete_steps_taken_summary=concrete_steps_list,
            perceived_obstacles_summary=perceived_obstacles_list,
            required_resources_or_skills_summary=required_resources_list,
            expected_impact_or_outcome_description=expected_impact,
            underlying_values_links=uv_links_list,
            related_complex_or_trauma_links=rct_links_list
        )

    def to_dict(self) -> Dict[str, Any]:
        # 基底クラスの to_dict を呼び出し、固有のフィールドを追加する形が良い
        data = super().to_dict() # BaseDataEntry の to_dict を呼び出す
        data.update({
            "description": self.description,
            "category": self.category.value, # Enumは値に変換
            "motivation_source_description": self.motivation_source_description,
            "first_conceived_date_text": self.first_conceived_date_text,
            "estimated_first_conceived_period": self.estimated_first_conceived_period.to_dict() if self.estimated_first_conceived_period else None,
            "target_completion_date_text": self.target_completion_date_text,
            "concrete_steps_taken_summary": [cs.to_dict() for cs in self.concrete_steps_taken_summary],
            "perceived_obstacles_summary": self.perceived_obstacles_summary,
            "required_resources_or_skills_summary": self.required_resources_or_skills_summary,
            "expected_impact_or_outcome_description": self.expected_impact_or_outcome_description,
            "underlying_values_links": [uvl.to_dict() for uvl in self.underlying_values_links],
            "related_complex_or_trauma_links": [rctl.to_dict() for rctl in self.related_complex_or_trauma_links],
        })
        return data