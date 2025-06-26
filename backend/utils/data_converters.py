from typing import Optional
from datetime import datetime # 正確な日時型を使用

# --- データ変換ヘルパー関数 (utils/data_converters.py に移すのが望ましい) ---
def get_enum_value(enum_cls, value_str: Optional[str], default_enum_member):
    if value_str is None:
        return default_enum_member
    try:
        return enum_cls(value_str)
    except ValueError:
        # print(f"Warning: Invalid value '{value_str}' for enum {enum_cls.__name__}. Using default: {default_enum_member.value}")
        return default_enum_member

def parse_datetime_optional(datetime_str: Optional[str]) -> Optional[datetime]:
    if datetime_str:
        try:
            return datetime.fromisoformat(datetime_str.replace("Z", "+00:00")) # ISO 8601 UTC
        except ValueError:
            # print(f"Warning: Could not parse datetime string '{datetime_str}'. Returning None.")
            return None
    return None

def datetime_to_iso_optional(dt_obj: Optional[datetime]) -> Optional[str]:
    if dt_obj:
        return dt_obj.isoformat().replace("+00:00", "Z")
    return None


