# これ = {
### 3.3 AI評価システム（llama.cpp統合）

# app/services/ai_evaluator.py
import asyncio
import json
import time
from typing import Dict, Any
from llama_cpp import Llama

class AnswerEvaluator:
    def __init__(self, model_path: str):
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=8,
            verbose=False,
            use_mmap=True,
            use_mlock=False
        )
        
        # 初期化質問用のテンプレート
        # 注: 実際の質問はデータベースの `InitializationQuestion` テーブルに網羅的に定義され、
        # そこから動的に読み込まれます。以下は代表例およびシステムが認識する質問の範囲を示すものです。
        self.init_questions_templates = [
            # 既存の質問
            "あなたの専門分野について教えてください",
            "現在の職業・役職について詳しく教えてください", 
            "これまでの経験で最も印象的なプロジェクトは何ですか？",
            "今後のキャリア目標について教えてください",
            "このシステムに期待することは何ですか？",
            # 新規追加の質問 (カテゴリ別)
            # カテゴリ1：significant_childhood_experiences (幼少期の重要な体験)
            "子供の頃のことを思い出してみてください。今でも鮮明に記憶に残っている、楽しかった出来事や、誇らしかった経験はありますか？どんなことでも構いません。",
            "逆に、子供の頃に経験したことで、少しつらかったり、怖かったり、悲しかったりした記憶があれば、差し支えない範囲で教えていただけますか？",
            # カテゴリ2：influential_people (影響を受けた人々)
            "これまでの人生で、『この人には大きな影響を受けたな』と感じる人物はいますか？家族、先生、友人、あるいは本や映画の登場人物でも構いません。その人のどんな点に影響を受けましたか？",
            # カテゴリ3：inner_complexes_traumas (内面のコンプレックス・トラウマ)
            "誰にでも、自分の弱みや、人にはあまり言いたくないと感じる部分があると思います。もし、ご自身で『これは自分のコンプレックスだな』と感じることがあれば、少しだけ教えていただけませんか？無理に話す必要は全くありません。",
            # カテゴリ4：personality_traits (性格の特徴)
            "ご自身の性格について、周りの人から『〇〇な人だよね』と言われることはありますか？また、ご自身では自分のことをどんな性格だと思いますか？",
            # カテゴリ5：beliefs_values (信念・価値観)
            "あなたが人生で何かを決める時、『これだけは譲れない』と考えていることや、大切にしている『ルール』のようなものはありますか？",
            # カテゴリ6：hobbies_interests (趣味・興味)
            "時間を忘れて没頭できるような趣味や、最近『面白いな』と興味を持っていることは何ですか？それをしている時、どんな気持ちになりますか？",
            # カテゴリ7：interpersonal_style (対人関係のスタイル)
            "あなたは、大勢で集まるのと、少人数で深く話すのとでは、どちらが心地よいと感じますか？また、初対面の人と話すのは得意な方ですか？",
            # カテゴリ8：emotional_reaction_patterns (感情の反応パターン)
            "最近、何かに対して『すごく嬉しい！』または『すごく腹が立った！』と感じた出来事はありましたか？その時、どのような状況でしたか？",
            # カテゴリ9：aspirations_dreams (理想・夢)
            "もし、何の制約もなかったとしたら、将来どんなことをしてみたいですか？漠然とした憧れや、小さな夢でも構いません。",
            # カテゴリ10：past_failures_learnings (過去の失敗と学び)
            "これまでの経験で、『あれは失敗だったな』と思い出すことはありますか？その経験から、何か学んだことや、今の自分に活かされていることはありますか？",
            # カテゴリ11：internal_conflicts_coping (内面の葛藤と対処法)
            "『Aをしたいけど、Bもしなければならない』というように、心の中で二つの気持ちが対立して、どうしようか迷った経験はありますか？その時、最終的にどのように決断しましたか？",
            # カテゴリ12：emotional_triggers (感情のトリガー)
            "他の人は気にしないようなことでも、自分にとっては特定の言葉や状況が、なぜかとても嬉しくなったり、逆にカチンときたりすることはありますか？",
            # カテゴリ13：behavioral_patterns_underlying_needs (行動パターンと根底にある欲求)
            "あなたは、何かを始める時に、じっくり計画を立ててから行動するタイプですか？それとも、まず行動してみてから考えるタイプですか？具体的な例があれば教えてください。",
            # カテゴリ14：thought_processes_cognitive_biases (思考プロセスと認知バイアス)
            "何かうまくいかないことがあった時、あなたは『全部自分のせいだ』と考えがちですか？それとも『まあ、仕方ないか』と考えることが多いですか？",
            # カテゴリ15：verbal_nonverbal_tics_indicated_thoughts (言動の癖と思考の現れ)
            "無意識のうちによく使ってしまう口癖や、考え事をする時にしてしまう仕草などはありますか？",
            # カテゴリ16：evolution_of_values_turning_points (価値観の変遷と転換点)
            "昔と今とで、『大切にするもの』が変わったなと感じることはありますか？もしあれば、何かきっかけとなった出来事があったのでしょうか？",
            # カテゴリ17：self_perception_self_esteem (自己認識と自尊心)
            "あなたが思う、ご自身の『一番の長所』は何だと思いますか？その長所が活かされたエピソードがあれば教えてください。",
            # カテゴリ18：conflict_resolution_style (対立と解決の方法)
            "他の人と意見が食い違った時、あなたは自分の意見を主張しますか？それとも、相手の意見をまず受け入れようとしますか？",
            # カテゴリ19：relationship_history_adaptation (対人関係の歴史と適応)
            "これまでの友人関係や恋愛関係などを振り返って、人間関係について学んだ最も大きな教訓は何だと思いますか？",
            # カテゴリ20：future_outlook_anxieties_hopes (将来への展望・不安と希望)
            "ご自身の将来について考える時、一番ワクワクする『希望』は何ですか？また、もしあれば、少し気になる『不安』は何ですか？"
        ]
    
    async def evaluate_answer(self, question: str, answer: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """AI を使用して回答を評価"""
        
        # プロンプト構築
        if context.get("question_type") == "initialization":
            prompt = self._build_initialization_evaluation_prompt(question, answer, context)
        else:
            prompt = self._build_standard_evaluation_prompt(question, answer, context)
        
        try:
            # ストリーミング推論実行
            response_stream = self.llm(
                prompt,
                max_tokens=800,
                temperature=0.2,
                stream=True,
                stop=["</evaluation>", "\n\n---"],
                top_p=0.9,
                repeat_penalty=1.1
            )
            
            full_response = ""
            async for chunk in self._async_stream_wrapper(response_stream):
                if chunk and 'choices' in chunk and chunk['choices']:
                    token = chunk['choices'][0].get('text', '')
                    if token:
                        full_response += token
            
            # レスポンス解析
            evaluation = self._parse_evaluation_response(full_response)
            return evaluation
            
        except Exception as e:
            # AI評価エラー時のフォールバック
            return {
                "state": "fail",
                "score": 30,
                "feedback": "AI評価中にエラーが発生しました。より詳細な回答を再試行してください。",
                "follow_up_question": "もう少し具体的に教えていただけますか？",
                "error": str(e)
            }
    
    def _build_initialization_evaluation_prompt(self, question: str, answer: str, context: Dict[str, Any]) -> str:
        """初期化質問用の評価プロンプト"""
        attempt_count = context.get("attempt_count", 1)
        
        return f"""<system>
あなたは新規ユーザーの初期化質問への回答を評価するAIアシスタントです。
ユーザーがシステムを適切に利用できるよう、建設的で親切な評価を行ってください。

評価基準:
1. 具体性 (25点): 具体的な詳細が含まれているか
2. 関連性 (25点): 質問に対して適切に答えているか  
3. 情報量 (25点): 十分な情報が提供されているか
4. 表現力 (25点): 理解しやすい表現で書かれているか

合格基準: 70点以上で合格
試行回数: {attempt_count}回目
</system>

<question>{question}</question>
<answer>{answer}</answer>

以下の形式で評価してください:

<evaluation>
状態: pass または fail
スコア: 0-100の数値
評価詳細: {{
  "具体性": X点,
  "関連性": X点, 
  "情報量": X点,
  "表現力": X点
}}
"""