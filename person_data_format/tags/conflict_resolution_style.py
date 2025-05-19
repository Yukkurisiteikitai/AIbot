"""
# 対立の解消
面白い人が多くて嬉しいなって思ったりしますおね
なんか楽しいいなって思いますね。

## 対立の難しさ
正義と正義のぶつかり合いだかr亜その中でりょうsりゃが納得できる
正義を見つける
または決着をつける


## 人間性がある?



"""

from dataclasses import dataclass, field, asdict as dataclass_asdict
from typing import List, Optional, Dict, Any
from datetime import datetime

# ..common_typesから必要なEnumをインポート
from ..common_types import Status, ImportanceLevel, SensitivityLevel, DataSource
# ..base_dataから基底クラスとヘルパーをインポート
from ..base_data import BaseDataEntry, get_enum_value, parse_datetime_optional, datetime_to_iso_optional

@dataclass
class BeliefValueOriginEpisodeLink: # 名前をより具体的に
    """この信念・価値観の形成/根拠となった特定のエピソードへの詳細なリンク"""
    episode_id: str = field(metadata={"description": "根拠となるエピソードID"})
    # episode_text_snippet: Optional[str] = field(default=None, metadata={"description": "エピソード内の関連する部分の短い抜粋 (キャッシュ/表示用)"}) # ★追加
    # episode_text_token_indices: Optional[List[int]] = field(default=None, metadata={"description": "エピソード内の関連部分のトークンインデックス範囲 [start, end] (キャッシュ)"}) # ★追加
    reason_for_link: Optional[str] = field(default=None, metadata={"description": "なぜこのエピソードがこの信念と関連するのか (ユーザー/AI解釈)"}) # "why" に相当
    link_established_date: Optional[datetime] = field(default=None, metadata={"description": "このリンクが確立/最後に確認された日時"}) # "date" (リンクの確立日)

    def to_dict(self) -> Dict[str, Any]:
        data = dataclass_asdict(self)
        data['link_established_date'] = datetime_to_iso_optional(self.link_established_date)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BeliefValueOriginEpisodeLink':
        return cls(
            episode_id=data.get('episode_id', ''),
            # episode_text_snippet=data.get('episode_text_snippet'),
            # episode_text_token_indices=data.get('episode_text_token_indices'),
            reason_for_link=data.get('reason_for_link'),
            link_established_date=parse_datetime_optional(data.get('link_established_date'))
        )

@dataclass
class BeliefValueBehavioralExample:
    """信念・価値観が具体的な行動として現れる例"""
    example_description: str = field(metadata={"description": "具体的な行動例の説明"})
    # example_episode_id: Optional[str] = field(default=None, metadata={"description": "その行動例を示すエピソードID (オプション)"}) # (前回同様)

    def to_dict(self) -> Dict[str, Any]: return dataclass_asdict(self)
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BeliefValueBehavioralExample':
        return cls(example_description=data.get('example_description', ''))


@dataclass
class BeliefValue(BaseDataEntry):
    """
    ユーザーの信念や価値観、それが形成された背景、
    および日常生活での現れ方に関する情報を格納する。
    """
    # --- 信念・価値観の核心 ---
    value_statement: str = field(metadata={"description": "信念や価値観を表明する簡潔な記述 (ユーザー記述)"})
    # value_statement_embedding: Optional[List[float]] = field(default=None, metadata={"description": "value_statementのベクトル表現 (キャッシュ/AI分析用)"}) # ★追加
    # embedding_last_updated: Optional[datetime] = field(default=None, metadata={"description": "ベクトル表現の最終更新日時"}) # ★追加

    value_summary_by_ai: Optional[str] = field(default=None, metadata={"description": "ユーザーの複数の発言からAIが要約した信念・価値観の記述"})
    # value_summary_embedding: Optional[List[float]] = field(default=None, metadata={"description": "AI要約のベクトル表現 (キャッシュ/AI分析用)"}) # ★追加
    # summary_embedding_last_updated: Optional[datetime] = field(default=None, metadata={"description": "AI要約ベクトル表現の最終更新日時"}) # ★追加

    # --- 形成の背景・起源 (Saika764さんの「関連情報」の意図を反映) ---
    origin_episode_links: List[BeliefValueOriginEpisodeLink] = field(default_factory=list, metadata={"description": "この信念・価値観が形成された/影響を受けたエピソードへの詳細なリンク"})
    formation_period_text: Optional[str] = field(default=None, metadata={"description": "この信念・価値観が主に形成されたと考えられる時期のテキスト記述"})

    # --- 日常生活での現れ方・影響 ---
    behavioral_examples: List[BeliefValueBehavioralExample] = field(default_factory=list, metadata={"description": "この信念・価値観が具体的な行動として現れる例"})
    impact_on_decision_making_summary: Optional[str] = field(default=None, metadata={"description": "この信念・価値観が意思決定に与える影響の要約"})
    situations_where_challenged_summary: Optional[str] = field(default=None, metadata={"description": "この信念・価値観が試される状況の要約"})
    conflicts_with_other_values_links: List[str] = field(default_factory=list, metadata={"description": "この価値観と矛盾・葛藤する可能性のある他の自分の価値観(beliefs_valuesのID)へのリンク"})

    # --- ユーザーによる内省・評価 ---
    strength_of_conviction: Optional[ImportanceLevel] = field(default=None, metadata={"description": "この信念・価値観に対する確信の強さ"})
    is_limiting_belief: Optional[bool] = field(default=None, metadata={"description": "これが制限的信念である可能性"})

    def __post_init__(self):
        # super().__post_init__()
        if not self.id: raise ValueError("BeliefValue: 'id' is required.")
        if not self.entry_date: raise ValueError("BeliefValue: 'entry_date' is required.")
        if not self.value_statement and not self.value_summary_by_ai:
            raise ValueError("BeliefValue: Either 'value_statement' or 'value_summary_by_ai' is required.")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BeliefValue':
        base_args_dict = {}
        cls._from_dict_shared_logic(data, base_args_dict)

        origin_links_list = [BeliefValueOriginEpisodeLink.from_dict(ol) for ol in data.get('origin_episode_links', [])]
        behavioral_examples_list = [BeliefValueBehavioralExample.from_dict(be) for be in data.get('behavioral_examples', [])]
        strength_str = data.get('strength_of_conviction')
        strength_of_conviction = get_enum_value(ImportanceLevel, strength_str, ImportanceLevel.NOT_SET) if strength_str else None

        return cls(
            **base_args_dict,
            value_statement=data.get('value_statement', ''),
            # value_statement_embedding=data.get('value_statement_embedding'),
            # embedding_last_updated=parse_datetime_optional(data.get('embedding_last_updated')),
            value_summary_by_ai=data.get('value_summary_by_ai'),
            # value_summary_embedding=data.get('value_summary_embedding'),
            # summary_embedding_last_updated=parse_datetime_optional(data.get('summary_embedding_last_updated')),
            origin_episode_links=origin_links_list,
            formation_period_text=data.get('formation_period_text'),
            behavioral_examples=behavioral_examples_list,
            impact_on_decision_making_summary=data.get('impact_on_decision_making_summary'),
            situations_where_challenged_summary=data.get('situations_where_challenged_summary'),
            conflicts_with_other_values_links=data.get('conflicts_with_other_values_links', []),
            strength_of_conviction=strength_of_conviction,
            is_limiting_belief=data.get('is_limiting_belief')
        )

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "value_statement": self.value_statement,
            # "value_statement_embedding": self.value_statement_embedding,
            # "embedding_last_updated": datetime_to_iso_optional(self.embedding_last_updated),
            "value_summary_by_ai": self.value_summary_by_ai,
            # "value_summary_embedding": self.value_summary_embedding,
            # "summary_embedding_last_updated": datetime_to_iso_optional(self.summary_embedding_last_updated),
            "origin_episode_links": [ol.to_dict() for ol in self.origin_episode_links],
            "formation_period_text": self.formation_period_text,
            "behavioral_examples": [be.to_dict() for be in self.behavioral_examples],
            "impact_on_decision_making_summary": self.impact_on_decision_making_summary,
            "situations_where_challenged_summary": self.situations_where_challenged_summary,
            "conflicts_with_other_values_links": self.conflicts_with_other_values_links,
            "strength_of_conviction": self.strength_of_conviction.value if self.strength_of_conviction else None,
            "is_limiting_belief": self.is_limiting_belief,
        })
        return data