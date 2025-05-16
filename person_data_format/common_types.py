# person_data_format/common_types.py
from enum import Enum

class ImportanceLevel(Enum):
    """ユーザーによる情報の重要度レベル"""
    NOT_SET = "not_set"
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class Status(Enum):
    """データエントリの現在の状態"""
    ACTIVE = "active"
    ACHIEVED = "achieved" # (aspirations_dreams用)
    ABANDONED = "abandoned" # (aspirations_dreams用)
    ON_HOLD = "on_hold" # (aspirations_dreams用)
    ARCHIVED_BY_USER = "archived_by_user"
    OTHER_DATA_USER_MARKED_IRRELEVANT = "other_data_user_marked_irrelevant"
    OTHER_DATA_USER_DENIED_AI_INTERPRETATION = "other_data_user_denied_ai_interpretation"
    OTHER_DATA_LOW_CONFIDENCE = "other_data_low_confidence" # AIが低信頼度と判断
    DELETED_BY_USER_LOGICAL = "deleted_by_user_logical" # ごみ箱行き
    # (将来的には: DELETED_PERMANENTLY_BY_POLICY などもシステム内部で使う可能性)

class SensitivityLevel(Enum):
    """情報の機微度レベル"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXTREMELY_HIGH = "extremely_high" # 特にトラウマ関連

class DataSource(Enum):
    """この情報がシステムに記録された源泉"""
    USER_DIRECT_INPUT = "user_direct_input"
    DIALOGUE_EXTRACTION_USER_CONFIRMED = "dialogue_extraction_user_confirmed"
    DIALOGUE_EXTRACTION_AI_INFERRED = "dialogue_extraction_ai_inferred"
    REFLECTION_RESULT_SETTING = "reflection_result_setting"
    IMPORTED_FROM_BACKUP = "imported_from_backup"
    AI_GENERATED_ANALYSIS = "ai_generated_analysis" # AI分析結果など
    SYSTEM_LOG = "system_log" # システム内部ログなど
    UNKNOWN = "unknown"

class AspirationCategory(Enum): # aspiration_dreams専用のカテゴリ
    """夢や目標のカテゴリ"""
    CAREER = "キャリア"
    PERSONAL_GROWTH = "個人的成長"
    SOCIAL_CONTRIBUTION = "社会貢献"
    LIFESTYLE = "ライフスタイル"
    RELATIONSHIPS = "人間関係"
    HEALTH = "健康"
    FINANCIAL = "財務"
    TRAVEL = "旅行"
    HOBBY = "趣味"
    OTHER = "その他"

# --- 他のタグで共通して使う可能性のあるEnumもここに追加 ---
# 例: PersonalityFramework (BigFive, MBTIなど)
# 例: EmotionalPolarity (Positive, Negative, Neutral, Mixed)
# 例: DevelopmentalStage (学童期、青年期など、ただしこれはAIの推定結果の表現として)