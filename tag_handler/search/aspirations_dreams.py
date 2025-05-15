# aspirations_dream
"""
サンプルデータから
aspiration_dreamsのデータを扱う
入力としてサンプルデータを扱う
その中からaspiration_dreamsを扱う?
    
"""


aspirations_dreams_sample = [
    {
        "id": "ad_001",
        "entry_date": "YYYY-MM-DD",
        "last_updated": "YYYY-MM-DD",
        "source": "dialogue_extraction",
        "user_importance": "very_high",
        "status": "active",
        "sensitivity_level": "medium",
        "user_notes": "これは絶対に実現したい夢だ。",
        "linked_episode_ids": [
            "ep_xxx",
            "ep_yyy"
        ],
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
        "related_complex_or_trauma_links": None
    },
        {
        "id": "ad_001",
        "entry_date": "YYYY-MM-DD",
        "last_updated": "YYYY-MM-DD",
        "source": "dialogue_extraction",
        "user_importance": "very_high",
        "status": "active",
        "sensitivity_level": "medium",
        "user_notes": "これは絶対に実現したい夢だ。",
        "linked_episode_ids": [
            "ep_xxx",
            "ep_yyy"
        ],
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
        "related_complex_or_trauma_links": None
    }
]
# not need data

related_complex_or_trauma_links = {}


from dataclasses import dataclass, field

@dataclass
class weight:
    important: float = field(default=0.2, metadata={"description": "ユーザーにとっての重要度"})

class kind:
    id: str = field(default="", metadata={"description": "ユーザーの名前"})
    age: int = field(default=0, metadata={"description": "ユーザーの年齢（歳）"})

class expelince:
    name: str = field(default="", metadata={"description": "ユーザーの名前"})
    age: int = field(default=0, metadata={"description": "ユーザーの年齢（歳）"})

class problem:
    required_resources_or_skills: str = field{default="", metdata={"description": "ユーザーが夢や目標を達成するのに必要なスキルや能力のこと"}}
    

# weight

from typing import List, Optional
from pydantic import BaseModel

class EstimatedPeriod(BaseModel):
    start_age: Optional[int]
    end_age: Optional[int]
    developmental_stage_estimation: Optional[str]

class ConcreteStep(BaseModel):
    description: str
    date: Optional[str]

class RelatedComplexOrTraumaLink(BaseModel):
    entry_id: str
    relationship: str

class AspirationDream(BaseModel):
    id: str
    entry_date: str
    last_updated: str
    source: str
    user_importance: str
    status: str
    sensitivity_level: Optional[str]
    user_notes: Optional[str]
    linked_episode_ids: List[str]
    description: str
    category: str
    motivation_source_description: Optional[str]
    first_conceived_date_text: Optional[str]
    estimated_first_conceived_period: Optional[EstimatedPeriod]
    target_completion_date_text: Optional[str]
    concrete_steps_taken: Optional[List[ConcreteStep]]
    perceived_obstacles: Optional[List[str]]
    required_resources_or_skills: Optional[List[str]]
    expected_impact_or_outcome: Optional[str]
    underlying_values_links: Optional[List[str]]
    related_complex_or_trauma_links: Optional[List[RelatedComplexOrTraumaLink]]

# 使い方例
dream = AspirationDream(
    id="ad_001",
    entry_date="2024-05-15",
    last_updated="2024-05-15",
    source="dialogue_extraction",
    user_importance="very_high",
    status="active",
    sensitivity_level="medium",
    user_notes="これは絶対に実現したい夢だ。",
    linked_episode_ids=["ep_xxx", "ep_yyy"],
    description="自分の経験を活かして、社会貢献できる事業を立ち上げたい。",
    category="キャリア"
)