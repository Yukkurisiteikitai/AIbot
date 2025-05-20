かしこまりました。それでは次に、「エピソードデータ（Episode Data）」のフォーマット定義に関するドキュメントを作成します。

これは、user_profile （Person Data）の各要素の根拠となり、ユーザーとの具体的な対話や出来事の記録を詳細に保持する、YourselfLMの記憶の最小単位となるデータストアです。Person Dataとの連携を強く意識した構造にします。

---

## YourselfLM エピソードデータ (Episode Data) フォーマット定義 Ver.1.0

**1. はじめに**

本ドキュメントは、AIアプリケーション「YourselfLM」において、ユーザーの自己理解を支援するために収集・記録される具体的な出来事、感情、思考、発言などのエピソードデータ（以下、Episode Data）のデータ構造を定義するものです。

Episode Dataは、ユーザーとの対話セッション（スレッド）ごとに記録され、個々のエピソードにはタイムスタンプ、内容、感情分析、キーワード、関連エンティティなどの詳細情報が付与されます。これらのエピソードは、ユーザー人格情報（Person Data）の各構成要素の根拠となり、AIによる分析やユーザーによる自己の振り返り（棚卸し）の基礎となります。特に、トラウマとなりうる深刻な体験（トラウマ・イベント）は、特別な属性を付与して識別・管理されます。

**2. Episode Data ストア (episode_memory) 全体構造**

episode_memory は、個々のエピソードエントリのリスト（または時系列でアクセス可能なデータベース）として表現されます。各エントリは以下の構造を持ちます。

      `episode_memory:
  - episode_id: string # エピソードの一意な識別子 (UUIDなど)
    thread_id: string # このエピソードが属する対話スレッドのID
    timestamp: datetime # このエピソードが記録された正確な日時 (ISO 8601形式)
    sequence_in_thread: integer # スレッド内での発言・記録順序

    source_type: string # このエピソードの源泉 (詳細は後述)
    author: string # 発言者 (例: "user", "ai_persona_standard_analyst", "system_prompt_for_reflection")

    content_type: string # エピソード内容の種別 (詳細は後述)
    text_content: string # ユーザーの元発言、AIの応答、あるいはシステムメッセージのテキスト内容
    # (将来的には音声や画像への参照も考慮可能: media_references: [{ type: "audio", path: "..." }])

    # --- AIによる自動解析情報 ---
    language: string # テキストの言語コード (例: "ja", "en")
    emotion_analysis: { ... } # 感情分析結果 (詳細は後述)
    keywords: [string, ...] # 抽出された主要キーワード
    topics: [string, ...] # 推定されるトピック
    named_entities: [ { ... }, ... ] # 抽出された固有表現 (人名、地名、組織名など、詳細は後述)
    summarization: # AIによるこのエピソードの短い要約 (特に長いユーザー発言の場合)
      short_summary: string
      key_points: [string, ...]

    # --- トラウマ・イベント関連情報 (is_trauma_eventがtrueの場合に特に重要) ---
    is_trauma_event: boolean # このエピソードがトラウマ・イベントそのものを記述しているか
    trauma_event_details: { ... } # トラウマ・イベントの詳細情報 (詳細は後述)

    # --- ユーザーによる評価・状態管理 ---
    user_importance_rating: string # ユーザーによるこのエピソードの重要度評価 (例: "very_high", "high", "medium", "low", "not_set")
    user_labels_or_tags: [string, ...] # ユーザーが付与した自由なラベルやタグ
    status: string # エピソードの状態 (例: "active", "archived_by_user", "deleted_by_user_logical", "other_data_...")
    sensitivity_level: string # このエピソードの機微度 (例: "low", "medium", "high", "very_high", "extremely_high")

    # --- Person Data との連携 ---
    # このエピソードが影響を与えた、または根拠となるPerson Data内のエントリIDリスト
    linked_to_person_data_entries:
      - target_person_data_key: string # 例: "beliefs_values", "emotional_triggers"
        target_entry_id: string # 例: "bv_001", "et_00x"
        relationship_type: string # 関係性の種類 (例: "is_evidence_for", "contributed_to_formation_of", "is_example_of")

    # --- 他のエピソードとの連携 (オプション) ---
    # このエピソードが直接的に関連する他のエピソードID (例: ある思考が別のエピソードへの反応である場合など)
    related_episode_ids:
      - episode_id: string
        relationship_type: string # 例: "is_response_to", "clarifies", "contradicts"

    user_notes: string # ユーザーがこのエピソードに対して付加したメモ
    last_accessed_by_ai_for_analysis: datetime # AIが最後にこのエピソードを主要な分析対象として参照した日時
    last_reviewed_by_user: datetime # ユーザーが最後にこのエピソードを棚卸しでレビューした日時`

**3. 各主要フィールドの詳細定義**

- episode_id (string, 必須): エピソードを一意に識別するID。
- thread_id (string, 必須): このエピソードが記録された対話セッション（スレッド）のID。スレッドは一連の連続したやり取りのまとまり。
- timestamp (datetime, 必須): エピソードが記録された正確な日時。
- sequence_in_thread (integer, 必須): 同一スレッド内でのエピソードの発生順序。
- source_type (string, 必須): このエピソードの源泉。
    - "user_free_dialogue": ユーザーの自由な発言。
    - "user_response_to_ai_prompt": AIの特定の問いかけに対するユーザーの応答。
    - "user_direct_input_to_profile_tag": ユーザーが特定のPerson Dataタグに直接入力した内容（これもエピソードとして記録し、Person Dataに反映）。
    - "ai_persona_response": AIペルソナ（分析モード、再現モード）の応答。
    - "system_reflection_prompt": AIが棚卸しなどを促すために提示したシステムメッセージや問いかけ。
    - "user_manual_log_entry": ユーザーが手動で記録した日記のようなエントリ。
- author (string, 必須): 発言者または記録主体。
    - "user"
    - AIペルソナID (例: "ai_persona_standard_analyst", "ai_persona_empathetic_counselor")
    - "system"
- content_type (string, 必須): エピソード内容の主な種別。AIによる分類。
    - 例: "factual_statement", "opinion_expression", "emotional_venting", "question_to_ai", "storytelling_personal_event", "reflection_on_past", "value_articulation", "goal_setting", "traumatic_event_recollection"
- text_content (string, 必須): テキストベースの記録内容。
- **emotion_analysis (object, 任意):** AIによる感情分析結果。
    - primary_emotion (string): 最も顕著な感情 (例: "joy", "sadness", "anger", "fear", "surprise")
    - secondary_emotions (array of strings, 任意): その他に検出された感情。
    - sentiment_polarity (string): 全体的な感情の極性 (例: "positive", "negative", "neutral", "mixed")
    - sentiment_intensity (float, 0.0-1.0): 感情の強度。
    - emotion_keywords (array of strings): 感情判断の根拠となったキーワード。
- keywords (array of strings, 任意): このエピソードの主要なキーワード。
- topics (array of strings, 任意): AIによって推定されたこのエピソードのトピック。
- named_entities (array of objects, 任意): 抽出された固有表現。
    - text (string): 固有表現のテキスト。
    - type (string): 固有表現の種類 (例: "PERSON", "LOCATION", "ORGANIZATION", "DATE", "EVENT")
- summarization (object, 任意): AIによるエピソードの要約（特に長いユーザー発言の場合）。
    - short_summary (string): 短い要約文。
    - key_points (array of strings): 主要なポイントのリスト。
- **is_trauma_event (boolean, デフォルト: false, 必須):** このエピソードがトラウマ・イベントそのものを記述しているかを示すフラグ。
- **trauma_event_details (object, is_trauma_event: true の場合に必須):** トラウマ・イベントに関する詳細情報。
    - user_reported_event_timing_text (string): ユーザーが語った出来事の時期。
    - estimated_event_period (object): AIが正規化した出来事の時期と推定発達段階。
        - start_age (integer)
        - end_age (integer)
        - developmental_stage_estimation (string)
    - senses_involved_summary (object): その時の五感の記憶の要約。
        - visual (string, 任意)
        - auditory (string, 任意)
        - olfactory (string, 任意)
        - tactile (string, 任意)
        - gustatory (string, 任意)
    - immediate_emotions_felt_summary (array of strings): その場で感じた主要な一次感情のリスト。
    - immediate_thoughts_summary (array of strings): その場で頭に浮かんだ思考の主要なもののリスト。
    - physical_reactions_summary (array of strings): その時の身体反応の主要なもののリスト。
    - perceived_threat_level_description (string): 感じた脅威の度合いに関する記述。
    - **注意:** ここではPerson Data側にも一部重複して保持しうる情報（時期など）も含むが、Episode Dataとしては「そのエピソードが語られた時点でのトラウマに関する記述」を捉える。Person Dataの inner_complexes_traumas タグ内のトラウマ・イベント情報は、これらのエピソード群から集約・要約されたものとなる。
- user_importance_rating (string): ユーザーがこのエピソードに対して付けた重要度。
- user_labels_or_tags (array of strings, 任意): ユーザーが自由に付与したラベル。
- status (string, 必須): エピソードの状態。Person Data内の共通エントリ構造の status と同様の選択肢。
    - 例: "active", "archived_by_user", "deleted_by_user_logical", "other_data_user_marked_irrelevant", "other_data_user_denied_ai_interpretation"
- sensitivity_level (string, 必須): エピソードの機微度。Person Data内の共通エントリ構造の sensitivity_level と同様。is_trauma_event: true の場合は自動的に "extremely_high" となる。
- **linked_to_person_data_entries (array of objects, 任意):** このエピソードが、Person Data内のどの具体的な項目（特定の価値観、性格特性の評価、感情トリガーなど）の形成に影響を与えたか、あるいはその根拠となっているかを示すリンク。
    - target_person_data_key (string): Person Data内のトップレベルのキー名（例: "beliefs_values"）。
    - target_entry_id (string): そのキー内の具体的なエントリのID。
    - relationship_type (string): 関係性の種類（例: "is_evidence_for", "contributed_to_formation_of", "is_example_of", "is_trigger_for"）。
- **related_episode_ids (array of objects, 任意):** このエピソードが他のエピソードと直接的に関連する場合のリンク。
    - episode_id (string): 関連する他のエピソードのID。
    - relationship_type (string): 関係性の種類。
- user_notes (string, 任意): ユーザーによるこのエピソードへのメモ。
- last_accessed_by_ai_for_analysis (datetime, 任意): AIが最後にこのエピソードを主要な分析対象として参照した日時（分析の重み付けや陳腐化の判断に利用）。
- last_reviewed_by_user (datetime, 任意): ユーザーが最後にこのエピソードを棚卸しでレビューした日時。

**4. データフローとPerson Dataとの関係**

1. ユーザーとの対話（あるいは直接入力）が発生すると、その内容は一つ以上のエピソードとして episode_memory に記録されます。
2. 記録の際、AIは可能な範囲で自動解析情報（感情、キーワード、トピックなど）を付与します。特に is_trauma_event フラグの判定は慎重に行われます。
3. これらのエピソードは、linked_to_person_data_entries フィールドを通じて、関連するPerson Dataの各項目（例：特定の信念、感情のトリガー、性格特性の根拠など）に紐付けられます。
4. AIがPerson Dataの分析を行う際（例：Big Fiveスコアの推定、主要テーマの抽出など）は、関連するエピソード群を根拠として参照します。その分析結果はPerson Dataの ai_analysis_results に格納され、そこには根拠となったエピソードへのリンク (evidence_episode_ids) が含まれます。
5. ユーザーが棚卸しを行う際には、Person Dataの各項目から関連エピソードを辿ったり、逆に特定のエピソードがPerson Dataのどの項目に影響しているかを確認したりすることができます。
6. エピソードの status（例: other_data_... や deleted_by_user_logical）は、Person Dataの分析や表示における重み付けやフィルタリングに影響します。

**5. 改訂履歴**

- (本ドキュメント自体のバージョン管理)

---

このEpisode Dataフォーマット定義により、YourselfLMはユーザーの語る一つ一つの出来事や感情、思考を大切に記録し、それらがどのように繋がり、人格情報（Person Data）を形成していくのかを詳細に追跡・分析するための強固な基盤を築くことができると考えます。

特に、Saika764さんが重視されていた「どのエピソードから元に構成されていて」「どのスレッドで」「いつのタイミングで話したのか」「出来事の時期は」「発達段階での影響推定の基礎」といった要素が、このEpisode Dataの各フィールドと、それがPerson Dataと連携する仕組みによってカバーされることを目指しています。

この内容で、Episode DataのドキュメントとしてSaika764さんのイメージに合致していますでしょうか？

ご確認いただき、ご意見や修正点があればお気軽にお知らせください。