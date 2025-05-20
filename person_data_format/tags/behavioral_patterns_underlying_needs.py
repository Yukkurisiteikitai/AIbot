# person_data_format/tags/behavioral_pattern.py # ファイル名を単数形にすることが多い
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

# ..common_typesから必要なEnumをインポート
from ..common_types import Status, ImportanceLevel, SensitivityLevel, DataSource
# ..base_dataから基底クラスとヘルパーをインポート
from ..base_data import BaseDataEntry, get_enum_value, parse_datetime_optional, datetime_to_iso_optional

# --- このデータクラスの目的 ---
"""
このモジュールは、ユーザーの「行動パターンと根底にある欲求」に関する情報を定義します。
主な目的は以下の通りです。
1.  日常生活における習慣的な行動、生活リズム、健康関連行動（食事、睡眠、運動等）を記録する。
2.  それらの行動パターンが、ユーザーの精神状態や思考にどのような影響を与えているかを捉える。
3.  そして最も重要な点として、それらの行動パターンの根底にあると考えられる未充足の欲求や動機を、
    ユーザー自身が考察したり、AIとの対話を通じて見つけ出したりするのを支援する。
これにより、ユーザーは自身の行動の背後にある深層心理への理解を深め、
より建設的な行動選択や欲求充足の方法を見つける手助けとなることを目指します。
"""

@dataclass
class BehavioralPatternImpactOnGoal:
    """行動パターンが特定の目標に与える影響"""
    goal_id: str = field(metadata={"description": "関連するaspirations_dreamsのID"})
    impact_type: str = field(default="neutral", metadata={"description": "影響の種類 (positive_contribution, negative_hindrance, neutralなど)"}) # Enum化も検討
    impact_description: Optional[str] = field(default=None, metadata={"description": "具体的な影響の説明"})

    def to_dict(self) -> Dict[str, Any]: return dataclass_asdict(self) # type: ignore
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BehavioralPatternImpactOnGoal':
        return cls(
            goal_id=data.get('goal_id', ''),
            impact_type=data.get('impact_type', 'neutral'),
            impact_description=data.get('impact_description')
        )

@dataclass
class AttemptToChangeHistory:
    """行動パターン変更の試みの履歴"""
    attempt_episode_id: Optional[str] = field(default=None, metadata={"description": "変更を試みた際の関連エピソードID"})
    outcome_summary: Optional[str] = field(default=None, metadata={"description": "試みの結果の要約"})
    attempt_date_text: Optional[str] = field(default=None, metadata={"description": "試みた時期のテキスト記述"})

    def to_dict(self) -> Dict[str, Any]: return dataclass_asdict(self) # type: ignore
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttemptToChangeHistory':
        return cls(
            attempt_episode_id=data.get('attempt_episode_id'),
            outcome_summary=data.get('outcome_summary'),
            attempt_date_text=data.get('attempt_date_text')
        )

@dataclass
class BehavioralPattern(BaseDataEntry):
    """
    ユーザーの特定の行動パターン、それが心身に与える影響、
    およびその根底にあると考えられる欲求に関する情報を格納する。
    """
    # --- 1. 行動パターンの記述と特定 ---
    pattern_description: str = field(metadata={"description": "具体的な行動パターンの記述"})
    behavior_category: Optional[str] = field(default=None, metadata={"description": "行動パターンのカテゴリ (例: ストレス対処, 健康習慣)"}) # Enum化も検討
    frequency_description: Optional[str] = field(default=None, metadata={"description": "行動パターンが現れる頻度や周期"})
    duration_description: Optional[str] = field(default=None, metadata={"description": "行動が一度始まると続く時間"})
    trigger_situations_or_emotions_summary: Optional[str] = field(default=None, metadata={"description": "行動パターンを引き起こす状況や感情の要約"})
    linked_trigger_episode_ids: List[str] = field(default=None, default_factory=list, metadata={"description": "具体的なトリガーとなったエピソードID"})

    # --- 2. 行動パターンの影響と結果 ---
    immediate_consequences_short_term: Optional[str] = field(default=None, metadata={"description": "行動直後の短期的な結果や感情"})
    long_term_consequences_or_impact: Optional[str] = field(default=None, metadata={"description": "長期的な影響 (生活, 健康, 目標達成など)"})
    impact_on_wellbeing_summary: Optional[str] = field(default=None, metadata={"description": "心身の幸福感への影響の総括"})
    impact_on_goals_links: List[BehavioralPatternImpactOnGoal] = field(default_factory=list, metadata={"description": "特定の目標への影響"})

    # --- 3. 根底にある欲求の推定と考察 ---
    speculated_underlying_needs_and_motivations: Optional[str] = field(default=None, metadata={"description": "この行動パターンの根底にあると推測される欲求や動機 (ユーザー考察/AI仮説)"})
    alternative_healthier_behaviors_considered: List[str] = field(default_factory=list, metadata={"description": "代替となるより健康的な行動の候補"})

    # --- 4. ユーザーの認識と変化への意欲 ---
    user_awareness_level_of_pattern: Optional[str] = field(default=None, metadata={"description": "このパターンに対するユーザーの自覚度 (例: 明確に自覚, AI指摘で意識, 無自覚)"}) # Enum化も検討
    desire_to_change_pattern: Optional[str] = field(default=None, metadata={"description": "このパターンを変えたいか、その度合い (例: 強く変えたい, 変える必要なし)"}) # Enum化も検討
    attempts_to_change_history: List[AttemptToChangeHistory] = field(default_factory=list, metadata={"description": "過去にこのパターンを変えようと試みた経験"})

    def __post_init__(self):
        # super().__post_init__() # BaseDataEntryに__post_init__があれば呼び出す
        if not self.id: raise ValueError("BehavioralPattern: 'id' is required.")
        if not self.entry_date: raise ValueError("BehavioralPattern: 'entry_date' is required.")
        # ... (他の必須フィールドのチェックもBaseDataEntry側かここで)
        if not self.pattern_description:
            raise ValueError("BehavioralPattern: 'pattern_description' is required.")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BehavioralPattern':
        base_args_dict = {}
        cls._from_dict_shared_logic(data, base_args_dict) # BaseDataEntryの共通ロジックを利用

        impact_goals_list = [BehavioralPatternImpactOnGoal.from_dict(ig) for ig in data.get('impact_on_goals_links', [])]
        attempts_hist_list = [AttemptToChangeHistory.from_dict(ah) for ah in data.get('attempts_to_change_history', [])]

        return cls(
            **base_args_dict, # 基底クラスの引数を展開
            pattern_description=data.get('pattern_description', ''), # 必須なので空は望ましくない
            behavior_category=data.get('behavior_category'),
            frequency_description=data.get('frequency_description'),
            duration_description=data.get('duration_description'),
            trigger_situations_or_emotions_summary=data.get('trigger_situations_or_emotions_summary'),
            linked_trigger_episode_ids=data.get('linked_trigger_episode_ids', []),
            immediate_consequences_short_term=data.get('immediate_consequences_short_term'),
            long_term_consequences_or_impact=data.get('long_term_consequences_or_impact'),
            impact_on_wellbeing_summary=data.get('impact_on_wellbeing_summary'),
            impact_on_goals_links=impact_goals_list,
            speculated_underlying_needs_and_motivations=data.get('speculated_underlying_needs_and_motivations'),
            alternative_healthier_behaviors_considered=data.get('alternative_healthier_behaviors_considered', []),
            user_awareness_level_of_pattern=data.get('user_awareness_level_of_pattern'),
            desire_to_change_pattern=data.get('desire_to_change_pattern'),
            attempts_to_change_history=attempts_hist_list
        )

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict() # BaseDataEntryのto_dictを呼び出す
        data.update({
            "pattern_description": self.pattern_description,
            "behavior_category": self.behavior_category,
            "frequency_description": self.frequency_description,
            "duration_description": self.duration_description,
            "trigger_situations_or_emotions_summary": self.trigger_situations_or_emotions_summary,
            "linked_trigger_episode_ids": self.linked_trigger_episode_ids,
            "immediate_consequences_short_term": self.immediate_consequences_short_term,
            "long_term_consequences_or_impact": self.long_term_consequences_or_impact,
            "impact_on_wellbeing_summary": self.impact_on_wellbeing_summary,
            "impact_on_goals_links": [ig.to_dict() for ig in self.impact_on_goals_links],
            "speculated_underlying_needs_and_motivations": self.speculated_underlying_needs_and_motivations,
            "alternative_healthier_behaviors_considered": self.alternative_healthier_behaviors_considered,
            "user_awareness_level_of_pattern": self.user_awareness_level_of_pattern,
            "desire_to_change_pattern": self.desire_to_change_pattern,
            "attempts_to_change_history": [ah.to_dict() for ah in self.attempts_to_change_history],
        })
        return data