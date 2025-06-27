#ここではQuestioを井井することを目的に活動する
from typing import Dict, Any
from .runtime import Runtime
import yaml
import logging
from pathlib import Path
CONFIG_PATH = "config.yaml"
Q_CONFIG_PATH = "configs/meta_question.yaml"
ai_runtime = Runtime(config_path=CONFIG_PATH)





class Question_config:
    def __init__(self, config_path: str = "error_config.yaml"):
        self.config_path = Path(config_path) # Pathオブジェクトとして扱う
        if not self.config_path.is_file():
            # self.config が初期化される前にエラーを出す可能性があるので logging はここでは使わない
            print(f"ERROR: Config file not found: {self.config_path}")
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        self._config_data: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    # @property
    # def index_return(self) -> list: # 文字列で返すように変更
    #     try:
    #         # model_path は別途 runtime_config にマージする必要があります。
    #         return self._config_data["presentation_order"]
    #     except KeyError as e:
    #         print(f"ERROR: 'question_agent.question_config.taglist' or a part of it not found in config YAML. Error: {e}")
    #         raise
    @property
    def index_return(self) -> list: # 文字列で返すように変更
        try:
            return self._config_data["question_themes"][self._config_data["presentation_order"]]


        except KeyError as e:
            print(f"ERROR: 'question_agent.question_config.taglist' or a part of it not found in config YAML. Error: {e}")
            raise



"""
hobbies_interests: # タグNo.6
    display_name: "趣味・興味関心"
    definition: "個人の余暇時間の過ごし方、純粋に楽しいと感じること、情熱を注げる活動、知的好奇心を刺激される対象。成功体験や他者からの賞賛がきっかけで発展したものも含む。"
    input_examples:
      - "週末は登山に行くのが趣味で、自然の中でリフレッシュしている。"
      - "最近はAIイラストの作成に夢中になっている。"
      - "歴史小説を読むのが好きで、特に古代ローマ史に興味がある。"
    question_prompts_for_ai:
      - "最近、何か夢中になっていることや、楽しいと感じる活動はありますか？"
      - "あなたの知的好奇心をくすぐるものは何ですか？"
      - "どんなことをしている時が、一番リフレッシュできますか？"
      - "あなたの趣味や興味関心について、始めたきっかけや、そこから何を得ているか教えていただけますか？"n
    related_person_data_key: "hobbies_interests"
    notes: "「好き」と「得意」は必ずしも一致しない。「成功体験」と結びつけて記述するよう促すと、より自己理解に繋がる情報が得られる可能性。"
    original_tag_id: 6
"""
class Question:
    def __init__(self,cofig:Question_config):
        
        pass
    # QestionNumbersは1スタートで番号を振ってあるのでQuestion_numberに関してはしっかりと-１しなければならない
    def init_Question(self,question_list:list[str],Question_numbers:list[int]):
        # 質問のタグと質問の回答例を入力として質問を生成する
        now_tag = ""
        for i in Question_numbers:
            now_tag = question_list[i-1]
            sys_p= f"""
現在のタグは{now_tag}です。
このタグの説明:{svg}
"""