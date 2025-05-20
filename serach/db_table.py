-- エピソードメモリのメインテーブル
CREATE TABLE episode_memory (
    episode_id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    sequence_in_thread INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    author TEXT NOT NULL,
    content_type TEXT NOT NULL,
    text_content TEXT NOT NULL,
    language TEXT,
    is_trauma_event BOOLEAN DEFAULT FALSE,
    user_importance_rating TEXT,
    status TEXT NOT NULL,
    sensitivity_level TEXT NOT NULL,
    user_notes TEXT,
    last_accessed_by_ai_for_analysis DATETIME,
    last_reviewed_by_user DATETIME
);

-- 感情分析結果テーブル
CREATE TABLE episode_emotion_analysis (
    episode_id TEXT PRIMARY KEY,
    primary_emotion TEXT,
    sentiment_polarity TEXT,
    sentiment_intensity REAL,
    FOREIGN KEY (episode_id) REFERENCES episode_memory(episode_id)
);

-- キーワードとトピックテーブル
CREATE TABLE episode_keywords (
    episode_id TEXT,
    keyword TEXT,
    type TEXT, -- 'keyword' or 'topic'
    PRIMARY KEY (episode_id, keyword, type),
    FOREIGN KEY (episode_id) REFERENCES episode_memory(episode_id)
);

-- トラウマイベント詳細テーブル
CREATE TABLE episode_trauma_details (
    episode_id TEXT PRIMARY KEY,
    event_timing_text TEXT,
    start_age INTEGER,
    end_age INTEGER,
    developmental_stage TEXT,
    perceived_threat_level TEXT,
    FOREIGN KEY (episode_id) REFERENCES episode_memory(episode_id)
);

-- Person Dataとの連携テーブル
CREATE TABLE episode_person_data_links (
    episode_id TEXT,
    target_person_data_key TEXT,
    target_entry_id TEXT,
    relationship_type TEXT,
    PRIMARY KEY (episode_id, target_person_data_key, target_entry_id),
    FOREIGN KEY (episode_id) REFERENCES episode_memory(episode_id)
);

-- エピソード間の関連テーブル
CREATE TABLE episode_relationships (
    source_episode_id TEXT,
    target_episode_id TEXT,
    relationship_type TEXT,
    PRIMARY KEY (source_episode_id, target_episode_id),
    FOREIGN KEY (source_episode_id) REFERENCES episode_memory(episode_id),
    FOREIGN KEY (target_episode_id) REFERENCES episode_memory(episode_id)
);

