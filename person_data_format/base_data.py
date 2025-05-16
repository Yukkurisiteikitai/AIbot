# person_data_format/base_data.py
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime # 正確な日時型を使用
from .common_types import Status, ImportanceLevel, SensitivityLevel, DataSource
from utils.data_converters import get_enum_value, parse_datetime_optional, datetime_to_iso_optional



@dataclass
class BaseDataEntry:
    """全ての記録エントリの基底となるデータ構造"""
    id: str = field(metadata={"description": "一意な識別子 (UUIDなどを想定)"})
    entry_date: datetime = field(metadata={"description": "このエントリが最初に作成・記録された日時 (UTC)"})
    last_updated: datetime = field(metadata={"description": "このエントリが最後に更新された日時 (UTC)"})
    source: DataSource = field(metadata={"description": "この情報の源泉"})
    status: Status = field(default=Status.ACTIVE, metadata={"description": "エントリの現在の状態"})
    user_importance: ImportanceLevel = field(default=ImportanceLevel.NOT_SET, metadata={"description": "ユーザーによるこの情報の重要度評価"})
    sensitivity_level: SensitivityLevel = field(default=SensitivityLevel.MEDIUM, metadata={"description": "情報の機微度"})
    user_notes: Optional[str] = field(default=None, metadata={"description": "ユーザーがこのエントリに対して自由に記述できるメモ"})
    linked_episode_ids: List[str] = field(default_factory=list, metadata={"description": "このエントリの根拠/関連するエピソードIDのリスト (EpisodeDataを参照)"})
    # (オプション) AIによるこのエントリの信頼度や関連度スコアなど
    # ai_confidence_score: Optional[float] = field(default=None)
    # ai_relevance_score: Optional[float] = field(default=None)

    def to_dict(self) -> Dict[str, Any]:
        """dataclassインスタンスを辞書に変換する (Enumとdatetimeを文字列に)"""
        data_dict = {}
        for f in field(self.__class__).fields: # type: ignore
            value = getattr(self, f.name)
            if isinstance(value, Enum):
                data_dict[f.name] = value.value
            elif isinstance(value, datetime):
                data_dict[f.name] = datetime_to_iso_optional(value)
            elif hasattr(value, 'to_dict'): # ネストされたdataclassの場合
                data_dict[f.name] = value.to_dict()
            elif isinstance(value, list) and value and hasattr(value[0], 'to_dict'): # dataclassのリスト
                data_dict[f.name] = [item.to_dict() for item in value]
            else:
                data_dict[f.name] = value
        return data_dict

    @classmethod
    def _from_dict_shared_logic(cls, data: Dict[str, Any], target_instance: Any):
        """サブクラスの from_dict で共通して使えるロジック"""
        target_instance.id = data.get('id', '') # 必須なので、なければエラーかUUID生成が良い
        target_instance.entry_date = parse_datetime_optional(data.get('entry_date')) or datetime.utcnow()
        target_instance.last_updated = parse_datetime_optional(data.get('last_updated')) or datetime.utcnow()
        target_instance.source = get_enum_value(DataSource, data.get('source'), DataSource.UNKNOWN)
        target_instance.status = get_enum_value(Status, data.get('status'), Status.ACTIVE)
        target_instance.user_importance = get_enum_value(ImportanceLevel, data.get('user_importance'), ImportanceLevel.NOT_SET)
        target_instance.sensitivity_level = get_enum_value(SensitivityLevel, data.get('sensitivity_level'), SensitivityLevel.MEDIUM)
        target_instance.user_notes = data.get('user_notes')
        target_instance.linked_episode_ids = data.get('linked_episode_ids', [])
        return target_instance

    # @classmethod
    # def from_dict(cls, data: Dict[str, Any]) -> 'BaseDataEntry':
    #     # この基底クラスを直接インスタンス化することは通常ないが、もし必要なら実装
    #     # 実際には各サブクラスがこれを呼び出すか、類似のロジックを持つ
    #     instance = cls.__new__(cls) # type: ignore
    #     return cls._from_dict_shared_logic(data, instance)