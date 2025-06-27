# person data

承知いたしました。これまでの議論で非常に多くの詳細が決まってきましたので、一度「人格情報（Person Data）」のフォーマットについてドキュメントとして整理するのは非常に良いステップですね。これにより、認識の齟齬を防ぎ、今後の開発や議論の土台を強固なものにできます。

まずは、「人格情報（Person Data）」、つまり主に user_profile に格納される情報の構造について、詳細なドキュメントを作成します。ep1isode_data との連携についても触れますが、episode_data の詳細なドキュメントは別途とし、ここでは person_data 側から見た連携のあり方を中心に記述します。

---

## YourselfLM ユーザー人格情報 (Person Data) フォーマット定義 Ver.1.0

**1. はじめに**

本ドキュメントは、AIアプリケーション「YourselfLM」において、ユーザーの自己理解を支援するために収集・保存・分析されるユーザーの人格情報（以下、Person Data）のデータ構造を定義するものです。

Person Dataは、ユーザーとの対話、ユーザーによる直接入力、およびAIによる分析結果から構成され、ユーザープロファイル (user_profile) として管理されます。この情報は、ユーザーの過去の経験、感情、思考、価値観、行動パターンなどを多角的に捉え、ユーザーの自己理解と成長をサポートするための基盤となります。

**2. Person Data (user_profile) 全体構造**

user_profile は、以下の主要なキーを持つYAML/JSONライクな構造で表現されます。

      `user_profile:
  user_id: string # ユーザーの一意な識別子
  profile_version: string # このプロファイル構造自体のバージョン (例: "1.0")
  created_at: datetime # プロファイル作成日時 (ISO 8601形式)
  last_updated: datetime # プロファイル最終更新日時 (ISO 8601形式)
  profile_status: string # プロファイルの状態 (例: "active", "archived_by_user")

  meta_settings: { ... } # ユーザーのメタ設定 (詳細は後述)

  # --- ユーザーから直接入力された情報 (20個のタグに基づく) ---
  # 各タグセクションは、複数のデータエントリをリスト形式で保持
  significant_childhood_experiences: [ { ... }, ... ]
  influential_people: [ { ... }, ... ]
  inner_complexes_traumas: [ { ... }, ... ] # トラウマ・イベントもここに特別な属性で記録
  personality_traits: [ { ... }, ... ]
  beliefs_values: [ { ... }, ... ]
  hobbies_interests: [ { ... }, ... ]
  interpersonal_style: [ { ... }, ... ]
  emotional_reaction_patterns: [ { ... }, ... ]
  aspirations_dreams: [ { ... }, ... ]
  past_failures_learnings: [ { ... }, ... ]
  internal_conflicts_coping: [ { ... }, ... ]
  emotional_triggers: [ { ... }, ... ]
  behavioral_patterns_underlying_needs: [ { ... }, ... ]
  thought_processes_cognitive_biases: [ { ... }, ... ]
  verbal_nonverbal_tics_indicated_thoughts: [ { ... }, ... ]
  evolution_of_values_turning_points: [ { ... }, ... ]
  self_perception_self_esteem: [ { ... }, ... ]
  conflict_resolution_style: [ { ... }, ... ]
  relationship_history_adaptation: [ { ... }, ... ]
  future_outlook_anxieties_hopes: [ { ... }, ... ]
  # (AIに打ち明けた未開示のネガティブな体験 -> inner_complexes_traumas や該当エピソードでカバー)

  ai_analysis_results: { ... } # AIによる分析結果・推定情報 (詳細は後述)
  user_feedback_log: [ { ... }, ... ] # AIの分析等に対するユーザーフィードバック履歴
  reflection_history: [ { ... }, ... ] # 棚卸し・レビュー履歴`

**3. 各主要セクションの詳細定義**

**3.1. user_profile メタ情報**

- user_id (string, 必須): ユーザーを一意に識別するID。
- profile_version (string, 必須): この user_profile のデータ構造自体のバージョン。フォーマット変更時の互換性管理に利用。
- created_at (datetime, 必須): このユーザープロファイルが最初に作成された日時。
- last_updated (datetime, 必須): このユーザープロファイル内のいずれかの情報が最後に更新された日時。
- profile_status (string, 必須): プロファイルの現在の状態。
    - 例: "active" (通常利用中), "archived_by_user" (ユーザーによりアーカイブされた), "pending_deletion" (ユーザーにより削除要求があり、猶予期間中)

**3.2. meta_settings (ユーザーのメタ設定)**

ユーザーがYourselfLMの挙動をカスタマイズするための設定情報。

- privacy_level (string, デフォルト: "private"): プライバシーレベル設定（現在は "private" のみ想定）。
- allow_ai_analysis (boolean, デフォルト: true): AIによるデータ分析を許可するかどうか。
- reflection_reminder_frequency (string, デフォルト: "monthly"): 棚卸しリマインダーの頻度。
    - 選択肢例: "monthly", "quarterly", "yearly", "custom", "off"
- last_reflection_date (date): 最後に棚卸しを行った日付。
- memory_retention_period_months (integer, デフォルト: 3): 「OtherData」ではないアクティブな記憶の基本的な保持期間（月単位）。これを超える古い情報は、AIの重要判断やユーザーのアーカイブ宣言がない限り、陳腐化の対象となる。
- auto_delete_other_data_period_months (integer, デフォルト: 3): 「OtherData」に分類された情報が、最終アクセスや更新からこの期間利用されなかった場合に自動的に完全削除されるまでの期間。
- balance_intervention (object): ポジティブ/ネガティブバランス調整機能の設定。
    - enabled (boolean, デフォルト: true): 機能の有効/無効。
    - threshold (integer, デフォルト: 3): どちらかの感情的発言が何件連続（あるいは一定期間内に何件以上）したら介入するかの閾値。
    - positive_bias_intervention (string, デフォルト: "gentle_suggestion"): ポジティブ側に偏った場合の介入方法。
        - 選択肢例: "gentle_suggestion" (控えめな提案), "off" (介入しない)
    - negative_bias_intervention (string, デフォルト: "active_suggestion"): ネガティブ側に偏った場合の介入方法。
        - 選択肢例: "active_suggestion" (積極的な提案), "off" (介入しない)
- active_ai_analysis_persona_id (string, デフォルト: "standard_analyst"): 現在ユーザーが選択している分析モード時のAIペルソナID。
- **(バックアップ関連設定)**
    - local_auto_backup_enabled (boolean, デフォルト: true): ローカル自動バックアップ機能の有効/無効 (オプトアウト可能)。
    - local_auto_backup_path (string): ローカル自動バックアップの保存先フォルダパス (ユーザーが指定)。
    - local_auto_backup_frequency (string, デフォルト: "daily"): バックアップ頻度。
        - 選択肢例: "daily", "on_app_close", "weekly"
    - local_auto_backup_generations (integer, デフォルト: 7): 保持するバックアップの世代数。
- **(ユーザーインターフェース設定)**
    - ui_theme (string, デフォルト: "system"): UIテーマ ("system", "light", "dark")。
    - analysis_mode_ui_color (string, デフォルト: "white"): 分析モード時のUI基調色。
    - mirror_mode_ui_color (string, デフォルト: "black"): 再現モード時のUI基調色。
    - font_size (string, デフォルト: "medium"): フォントサイズ ("small", "medium", "large")。
- **(その他の高度な設定)**
    - ユーザーが調整可能な各種閾値やAIの挙動に関するパラメータ（詳細は別途「設定項目ドキュメント」で定義）。

**3.3. ユーザー入力情報（タグベースデータ）**

ユーザーが直接入力したり、AIとの対話から抽出・構造化されたりする情報。20個のタグに対応するキーを持ち、各キーの値はデータエントリのリストとなる。

**3.3.1. 共通データエントリ構造**

全てのタグのデータエントリに共通して含まれる可能性のあるメタ情報。

- id (string, 必須): 各エントリの一意な識別子 (UUIDなど)。
- entry_date (datetime, 必須): このエントリが最初に作成・記録された日時。
- last_updated (datetime, 必須): このエントリが最後に更新された日時。
- source (string, 必須): この情報の源泉。
    - 例: "user_direct_input", "dialogue_extraction", "ai_suggestion_confirmed_by_user"
- user_importance (string, デフォルト: "not_set"): ユーザー自身によるこの情報の重要度評価。
    - 選択肢例: "very_high", "high", "medium", "low", "not_set"
- ai_estimated_relevance_score (float, 0.0-1.0): AIが推定する、この情報が現在のユーザー理解や分析にどれだけ関連性が高いかのスコア（オプション）。
- status (string, 必須, デフォルト: "active"): このエントリの現在の状態。
    - "active": 通常の分析対象。
    - "archived_by_user": ユーザーによってアーカイブされた（通常分析からは除外されるが、参照は可能）。
    - "other_data_user_marked_irrelevant": ユーザーによって「重要でない」「関連性が低い」とマークされた。分析の重みは極めて低いか無視される。
    - "other_data_user_denied_ai_interpretation": AIの解釈をユーザーが否定した。
    - "other_data_low_confidence": AIが低信頼度と判断し、ユーザーも積極的に肯定しなかった情報。
    - "deleted_by_user_logical": ユーザーが通常削除（ごみ箱へ移動）した。実質的に other_data の一種。
- sensitivity_level (string, デフォルト: "medium"): 情報の機微度。
    - 選択肢例: "low", "medium", "high", "very_high", "extremely_high" (特にトラウマ関連)
- user_notes (string, 任意): ユーザーがこのエントリに対して自由に記述できるメモ。
- linked_episode_ids (array of strings, 任意): この人格情報エントリの根拠となる、あるいは強く関連する episode_memory 内の episode_id のリスト。**これにより、人格情報が「どのエピソード」から構成されているかのトレーサビリティを確保する。**

**3.3.2. 各タグの詳細定義（例として主要なもの、およびトラウマ関連を重点的に）**

- **タグID: significant_childhood_experiences**
    - **定義:** 幼少期（おおむね小学生くらいまで）に経験し、現在も記憶に残っている、人格形成や価値観に大きな影響を与えたと考えられる出来事や経験。ポジティブな体験だけでなく、困難だった体験やネガティブな感情を伴った体験も含む。
    - **格納される情報（共通メタ情報に加えて）:**
        - description (string, 必須): 具体的な出来事や経験の内容。
        - user_reported_event_timing_text (string, 任意): ユーザーが語った出来事の時期に関するテキスト記述（例：「小学校低学年の頃」「7歳の誕生日」）。
        - estimated_event_period (object, 任意): AIが正規化した出来事の時期。
            - start_age (integer)
            - end_age (integer)
            - developmental_stage_estimation (string): 推定される発達段階（例：「学童期前期」）。AIはこれに基づき、一般論としてどのような影響がありうるかの仮説生成の参考にすることがある。
        - perceived_impact_description (string, 任意): ユーザーが認識している、その経験が現在の自分に与えた影響。
        - primary_emotions_at_event_time (array of strings, 任意): その出来事の当時に感じた主要な感情。
        - narrative_style_tendency (string, 任意): 語られ方の傾向（AIによる分析候補：例「美談化」「悲劇化」「客観的」）。
        - related_context_info (object, 任意): 同時期の家庭環境や文化的背景など、関連するコンテキスト情報。
            - family_environment (string)
            - cultural_background (string)
        - **is_trauma_event_candidate (boolean, デフォルト: false): この幼少期体験が、後のトラウマ・イベントの定義に合致する可能性があるかどうかのAIによる一次的なフラグ（ユーザー確認待ち）。**
    - **AIの活用方法:** 個人の行動原理や価値観の根源を探る。トラウマや肯定的原体験の特定。深層心理への影響推定。発達段階に応じた影響の仮説生成（ユーザーへの問いかけとして）。
    - **注意点:** 記憶の曖昧さ、美化・歪曲リスク。センシティブな内容を含む可能性。AIは診断せず、解釈はユーザーに委ねる。
- **タグID: inner_complexes_traumas**
    - **定義:** 自身が劣等感、弱みと感じていること。過去の大きな失敗、ショックな出来事。そして、**「トラウマ・イベント」として明確に識別される、心的外傷となりうる具体的な体験**（事故、災害、虐待、深刻な人間関係のトラブルなど）。無意識的な回避行動や意識的な恐怖の原因となっているもの。
    - **格納される情報（共通メタ情報に加えて）：**
        - type (string, 必須): コンプレックスの種類、あるいは「トラウマ・イベント」である旨を示す。
            - 例: "social_anxiety_complex", "academic_inferiority_complex", "traumatic_event_witnessing", "traumatic_event_victimization"
        - description (string, 必須): 具体的な内容、状況、感情、思考。
        - **is_trauma_event (boolean, デフォルト: false): このエントリが明確に「トラウマ・イベント」そのものを記述している場合に true とする。**
            - **is_trauma_event: true の場合の追加フィールド（エピソードデータ側で詳細化するが、Person Data側にも要約やキー情報を保持）：**
                - trauma_event_summary (string): トラウマ・イベントの簡潔な要約。
                - user_reported_event_timing_text (string): 出来事の時期。
                - estimated_event_period (object): AIが正規化した時期と推定発達段階。
                - primary_senses_involved_summary (array of strings): 特に強く記憶に残っている五感の種類のリスト（例: "visual", "auditory"）。詳細はエピソードデータを参照。
                - immediate_emotions_summary (array of strings): その場で感じた主要な一次感情のリスト。
        - origin_linked_episode_ids (array of strings, 任意): このコンプレックスやトラウマの直接的な原因となった、あるいは強く関連する episode_memory のIDリスト。
        - avoidance_behaviors_description (string, 任意): このコンプレックスやトラウマに関連する典型的な回避行動。
        - coping_strategies_description (string, 任意): 試みている対処法。
        - impact_on_daily_life_description (string, 任意): 日常生活への影響。
    - **AIの活用方法:** 行動・思考の制約要因の把握。自己評価の歪みの理解。潜在的ストレス源の特定。トラウマ・イベントと他の人格要素（信念、感情トリガー、思考パターン等）との関連性を分析し、ユーザーが自身の反応を理解するのを支援する。
    - **注意点:** **最重要機密情報として扱う。** sensitivity_level は常に "extremely_high" に設定。AIは共感的かつ慎重な応答を徹底し、決して診断的な言及は行わない。ユーザーの明確な同意なしに深掘りせず、安全な開示をサポートする。特定の深刻な内容（自傷他害の念慮など）については、専門機関への相談を強く推奨する応答プロトコルを設ける。
- **(他の18個のタグについても、同様に定義、格納情報、AI活用法、注意点を記述)**
    - **信念・価値観 (beliefs_values)**: 形成の背景となったエピソード (linked_episode_ids) との連携を重視。
    - **感情のトリガー (emotional_triggers)**: 引き起こされる反応として、単一感情だけでなく「フラッシュバック（特定のトラウマ・イベントIDにリンク）」や「複雑な感情群」も記録できるようにする。
    - **行動パターン・反応パターン (behavioral_patterns_underlying_needs, emotional_reaction_patterns)**: それらのパターンの根拠となるエピソード群 (linked_episode_ids) や、関連する信念・価値観へのリンクを保持。

**3.4. ai_analysis_results (AIによる分析結果・推定情報)**

AIがPerson Data全体を分析して得られた洞察や推定。

- last_analysis_date (datetime): 最後に包括的な分析が行われた日時。
- estimated_personality_traits (object): 性格特性の推定結果。
    - big_five_scores (array of objects, 時系列):
        - date (date): 評価日
        - openness (float)
        - conscientiousness (float)
        - extraversion (float)
        - agreeableness (float)
        - neuroticism (float)
        - ai_confidence (float): AIの推定に対する自信度。
        - evidence_episode_ids (array of strings): 推定の根拠となったエピソードIDのリスト。
    - (他の性格フレームワークの推定結果も同様に)
- identified_major_themes (array of objects): AIが抽出したユーザーの主要なテーマやトピック。
    - theme_id (string)
    - name (string): テーマ名 (例: 「キャリアに関する葛藤と成長意欲」)
    - summary (string): AIによるテーマの要約。
    - related_episode_ids (array of strings): このテーマに関連するエピソードIDのリスト。
    - related_value_ids (array of strings): 関連する信念・価値観のIDリスト。
    - sentiment_trend (string): このテーマに関する感情の傾向 (例: "improving", "worsening", "mixed")
    - last_mentioned_date (date): このテーマが最後に言及された日。
- recognized_patterns (array of objects): AIが認識した行動・感情・思考のパターン。
    - pattern_id (string)
    - type (string): パターンの種類 (例: "emotional_reaction", "behavioral_habit", "cognitive_bias")
    - description (string): パターンの説明 (例: 「批判に対して強い自己防衛反応を示す」)
    - trigger_examples_episode_ids (array of strings): このパターンが観察された具体的なエピソードID。
    - estimated_frequency (string): パターンの推定頻度 (例: "often", "sometimes", "rarely")
- overall_insights_and_observations (array of objects, 時系列): AIからの総括的なコメント、気づきの提示、棚卸しで利用する内省のための問いかけなど。
    - date (date)
    - insight_text (string)
    - reflection_prompts (array of strings)

**3.5. user_feedback_log (AIの分析等に対するユーザーフィードバック履歴)**

ユーザーがAIの分析や解釈に対して行ったフィードバックの記録。

- feedback_id (string, 必須)
- date (datetime, 必須)
- target_data_type (string, 必須): フィードバック対象のデータの種類 (例: "ai_analysis_results.estimated_personality_traits.big_five_scores", "user_profile.identified_major_themes")
- target_data_id (string, 必須): フィードバック対象の具体的なデータエントリのID。
- user_comment (string, 必須): ユーザーのコメント内容。
- user_correction_suggestion (object, 任意): ユーザーによる修正案（例: BigFiveのスコア修正案など）。
- ai_action_taken (string): このフィードバックを受けてAIが取った対応 (例: "acknowledged", "reflected_in_future_analysis", "data_status_changed_to_other_data")

**3.6. reflection_history (棚卸し・レビュー履歴)**

ユーザーが行った棚卸しセッションの記録。

- reflection_id (string, 必須)
- date (datetime, 必須): 棚卸しを行った日時。
- type (string, 必須): 棚卸しの種類。
    - 例: "periodic_3month_review", "user_initiated_search_based_review", "event_driven_life_change_review", "ai_suggested_topic_review"
- reviewed_data_ids (array of strings): この棚卸しで主にレビューされたデータエントリのIDリスト。
- user_summary_and_insights_text (string, 任意): ユーザーがこの棚卸しを通じて得た気づきやまとめ。
- ai_guidance_summary (string, 任意): この棚卸しにおいてAIが提供した主要なガイダンスや問いかけの要約。
- next_action_items (array of strings, 任意): この棚卸しの結果、ユーザーが設定した次のアクションや目標。

**4. データ間の連携とトレーサビリティ**

- **エピソード (episode_memory) と Person Data (user_profile) の連携:**
    - episode_memory の各エピソードには、それが影響を与えたり根拠となったりする user_profile 内の特定のデータエントリ（例: ある価値観、ある性格特性の評価）へのリンク（ID参照）を複数保持します (linked_persona_profile_entries)。
    - 逆に、user_profile 内の多くのエントリ（特にユーザー入力に基づくものやAIの分析結果）は、その根拠となる具体的なエピソード群へのリンク（linked_episode_ids や evidence_episode_ids）を保持します。
    - これにより、「この価値観は、いつ、どのようなエピソードや対話（スレッドID経由で特定可能）から形成されたのか？」「このBigFiveのスコアは、どの発言や行動から推定されたのか？」といったトレーサビリティが確保されます。
- **Person Data内の連携:**
    - 異なるタグ間の情報も、意味的な関連性があればIDで相互にリンクされることがあります（例: ある「内面のコンプレックス」が特定の「幼少期の重要体験」に起因する場合など）。

**5. ステータス管理とデータライフサイクル（「OtherData」と削除ポリシー）**

- 各データエントリは status フィールドを持ちます。
- ユーザーが「これは違う」「重要でない」とフィードバックした情報や、AIが信頼度が低いと判断した情報は、status が "other_data_..." となり、分析の重み付けが極めて低く（例: 0.01）なるか、完全に無視されます。
- ユーザーによる通常の「削除」操作は、対象データの status を "deleted_by_user_logical"（論理削除、「ごみ箱」行き）に変更し、実質的に「OtherData」として扱います。
- "deleted_by_user_logical" やその他の "other_data_..." ステータスの情報は、meta_settings.auto_delete_other_data_period_months で設定された期間（例: 3ヶ月）、最終更新やアクセスがなければ自動的に完全に物理削除されます。
- ユーザーによる「完全に削除」操作は、即座に物理削除されます。
- アクティブなデータ (status: "active") も、meta_settings.memory_retention_period_months を超えて長期間参照・更新されない場合、AIによる重要度判断やユーザーのアーカイブ宣言がなければ陳腐化の対象となり、status が変更される（例: "archived_by_system_due_to_staleness"）か、あるいは棚卸し時にユーザーにレビューを促す対象となります。

**6. 改訂履歴**

- 現在はなし

---