# person_data_format/episode_data.py
from dataclasses import dataclass, field, asdict as dataclass_asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from .common_types import Status, ImportanceLevel, SensitivityLevel, DataSource  # 共通Enum
from .base_data import BaseDataEntry, get_enum_value, parse_datetime_optional, datetime_to_iso_optional  # 基底クラスとヘルパー


@dataclass
class EmotionAnalysis:
    primary_emotion: Optional[str] = None
    secondary_emotions: List[str] = field(default_factory=list)
    sentiment_polarity: Optional[
        str] = None  # positive, negative, neutral, mixed
    sentiment_intensity: Optional[float] = None  # 0.0-1.0
    emotion_keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return dataclass_asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionAnalysis':
        return cls(primary_emotion=data.get('primary_emotion'),
                   secondary_emotions=data.get('secondary_emotions', []),
                   sentiment_polarity=data.get('sentiment_polarity'),
                   sentiment_intensity=data.get('sentiment_intensity'),
                   emotion_keywords=data.get('emotion_keywords', []))


@dataclass
class NamedEntity:
    text: str
    type: str  # PERSON, LOCATION, ORGANIZATION, DATE, EVENTなど

    def to_dict(self) -> Dict[str, Any]:
        return dataclass_asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NamedEntity':
        return cls(text=data.get('text', ''), type=data.get('type', ''))


@dataclass
class TraumaEventDetails:  # is_trauma_event: true の場合の詳細
    user_reported_event_timing_text: Optional[str] = None
    # estimated_event_period: Optional[EstimatedPeriod] # EstimatedPeriodを再利用 (必要ならインポート)
    senses_involved_summary: Optional[Dict[str, str]] = field(
        default_factory=dict)  # visual, auditoryなど
    immediate_emotions_felt_summary: List[str] = field(default_factory=list)
    immediate_thoughts_summary: List[str] = field(default_factory=list)
    physical_reactions_summary: List[str] = field(default_factory=list)
    perceived_threat_level_description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return dataclass_asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TraumaEventDetails':
        return cls(
            user_reported_event_timing_text=data.get(
                'user_reported_event_timing_text'),
            # estimated_event_period=EstimatedPeriod.from_dict(data['estimated_event_period']) if data.get('estimated_event_period') else None,
            senses_involved_summary=data.get('senses_involved_summary'),
            immediate_emotions_felt_summary=data.get(
                'immediate_emotions_felt_summary', []),
            immediate_thoughts_summary=data.get('immediate_thoughts_summary',
                                                []),
            physical_reactions_summary=data.get('physical_reactions_summary',
                                                []),
            perceived_threat_level_description=data.get(
                'perceived_threat_level_description'))


@dataclass
class EpisodeLinkToPersonData:
    target_person_data_key: str  # 例: "beliefs_values"
    target_entry_id: str  # 例: "bv_001"
    relationship_type: Optional[str] = None  # 例: "is_evidence_for"

    def to_dict(self) -> Dict[str, Any]:
        return dataclass_asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EpisodeLinkToPersonData':
        return cls(target_person_data_key=data.get('target_person_data_key',
                                                   ''),
                   target_entry_id=data.get('target_entry_id', ''),
                   relationship_type=data.get('relationship_type'))


@dataclass
class RelatedEpisodeLink:
    episode_id: str
    relationship_type: Optional[str] = None  # 例: "is_response_to"

    def to_dict(self) -> Dict[str, Any]:
        return dataclass_asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RelatedEpisodeLink':
        return cls(episode_id=data.get('episode_id', ''),
                   relationship_type=data.get('relationship_type'))


@dataclass
class EpisodeData(BaseDataEntry):
    """個々のエピソード（ユーザーの発言、AIの応答など）を記録するデータ構造"""
    thread_id: str = field(metadata={"description": "このエピソードが属する対話スレッドのID"})
    sequence_in_thread: int = field(metadata={"description": "スレッド内での発言・記録順序"})
    author: str = field(
        metadata={"description":
                  "発言者 (user, ai_persona_id, system)"})  # Enum化も検討

    content_type: str = field(metadata={"description":
                                        "エピソード内容の種別"})  # Enum化も検討
    text_content: str = field(metadata={"description": "テキスト内容"})

    # --- AIによる自動解析情報 ---
    language: Optional[str] = field(
        default=None, metadata={"description": "テキストの言語コード (例: 'ja')"})
    emotion_analysis: Optional[EmotionAnalysis] = field(default=None)
    keywords: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    named_entities: List[NamedEntity] = field(default_factory=list)
    summarization_short: Optional[str] = field(
        default=None, metadata={"description": "短い要約"})
    summarization_key_points: List[str] = field(
        default_factory=list, metadata={"description": "主要なポイント"})

    # --- トラウマ・イベント関連 ---
    is_trauma_event: bool = field(
        default=False, metadata={"description": "トラウマ・イベントそのものを記述しているか"})
    trauma_event_details: Optional[TraumaEventDetails] = field(
        default=None,
        metadata={"description": "トラウマ・イベントの詳細 (is_trauma_eventがTrueの場合)"})

    # --- Person Data との連携 ---
    linked_to_person_data_entries: List[EpisodeLinkToPersonData] = field(
        default_factory=list)

    # --- 他のエピソードとの連携 ---
    related_episode_links: List[RelatedEpisodeLink] = field(
        default_factory=list)

    last_accessed_by_ai_for_analysis: Optional[datetime] = field(default=None)
    last_reviewed_by_user: Optional[datetime] = field(default=None)

    def __post_init__(self):
        super().__post_init__()  # 基底クラスのチェックを呼び出す場合
        if not self.thread_id:
            raise ValueError("EpisodeData: 'thread_id' is required.")
        # sequence_in_thread は自動採番されるかもしれないので、ここではチェックしないケースも
        if not self.author:
            raise ValueError("EpisodeData: 'author' is required.")
        if not self.content_type:
            raise ValueError("EpisodeData: 'content_type' is required.")
        if self.text_content is None:
            raise ValueError("EpisodeData: 'text_content' is required."
                             )  # 空文字列は許容するかもしれないがNoneは不可
        if self.is_trauma_event and self.trauma_event_details is None:
            # print("Warning: Episode marked as trauma_event but no trauma_event_details provided.")
            pass  # あるいはエラーにするか、デフォルトのTraumaEventDetailsを生成

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EpisodeData':
        base_args_dict = {}  # BaseDataEntry のフィールドを格納する辞書
        # BaseDataEntry._from_dict_shared_logic を使いたいが、ここでは手動で設定
        base_args_dict['id'] = data.get('id', '')
        base_args_dict['entry_date'] = parse_datetime_optional(
            data.get('entry_date')) or datetime.utcnow()
        base_args_dict['last_updated'] = parse_datetime_optional(
            data.get('last_updated')) or datetime.utcnow()
        base_args_dict['source'] = get_enum_value(DataSource,
                                                  data.get('source'),
                                                  DataSource.UNKNOWN)
        base_args_dict['status'] = get_enum_value(Status, data.get('status'),
                                                  Status.ACTIVE)
        base_args_dict['user_importance'] = get_enum_value(
            ImportanceLevel, data.get('user_importance'),
            ImportanceLevel.NOT_SET)
        base_args_dict['sensitivity_level'] = get_enum_value(
            SensitivityLevel, data.get('sensitivity_level'),
            SensitivityLevel.MEDIUM)
        base_args_dict['user_notes'] = data.get('user_notes')
        base_args_dict['linked_episode_ids'] = data.get(
            'linked_episode_ids', [])  # BaseDataEntry側のlinked_episode_ids

        ea_data = data.get('emotion_analysis')
        emotion_analysis = EmotionAnalysis.from_dict(
            ea_data) if ea_data else None
        ne_list = [
            NamedEntity.from_dict(ne) for ne in data.get('named_entities', [])
        ]
        ted_data = data.get('trauma_event_details')
        trauma_event_details = TraumaEventDetails.from_dict(
            ted_data) if ted_data else None
        ltpd_list = [
            EpisodeLinkToPersonData.from_dict(l)
            for l in data.get('linked_to_person_data_entries', [])
        ]
        rel_list = [
            RelatedEpisodeLink.from_dict(r)
            for r in data.get('related_episode_links', [])
        ]

        return cls(
            **base_args_dict,
            thread_id=data.get('thread_id', ''),
            sequence_in_thread=data.get('sequence_in_thread',
                                        0),  # デフォルト0は適切か要検討
            author=data.get('author', ''),
            content_type=data.get('content_type', ''),
            text_content=data.get('text_content', ''),
            language=data.get('language'),
            emotion_analysis=emotion_analysis,
            keywords=data.get('keywords', []),
            topics=data.get('topics', []),
            named_entities=ne_list,
            summarization_short=data.get('summarization_short'),
            summarization_key_points=data.get('summarization_key_points', []),
            is_trauma_event=data.get('is_trauma_event', False),
            trauma_event_details=trauma_event_details,
            linked_to_person_data_entries=ltpd_list,
            related_episode_links=rel_list,
            last_accessed_by_ai_for_analysis=parse_datetime_optional(
                data.get('last_accessed_by_ai_for_analysis')),
            last_reviewed_by_user=parse_datetime_optional(
                data.get('last_reviewed_by_user')))

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "thread_id":
            self.thread_id,
            "sequence_in_thread":
            self.sequence_in_thread,
            "author":
            self.author,
            "content_type":
            self.content_type,
            "text_content":
            self.text_content,
            "language":
            self.language,
            "emotion_analysis":
            self.emotion_analysis.to_dict() if self.emotion_analysis else None,
            "keywords":
            self.keywords,
            "topics":
            self.topics,
            "named_entities": [ne.to_dict() for ne in self.named_entities],
            "summarization_short":
            self.summarization_short,
            "summarization_key_points":
            self.summarization_key_points,
            "is_trauma_event":
            self.is_trauma_event,
            "trauma_event_details":
            self.trauma_event_details.to_dict()
            if self.trauma_event_details else None,
            "linked_to_person_data_entries":
            [l.to_dict() for l in self.linked_to_person_data_entries],
            "related_episode_links":
            [r.to_dict() for r in self.related_episode_links],
            "last_accessed_by_ai_for_analysis":
            datetime_to_iso_optional(self.last_accessed_by_ai_for_analysis),
            "last_reviewed_by_user":
            datetime_to_iso_optional(self.last_reviewed_by_user),
        })
        return data
