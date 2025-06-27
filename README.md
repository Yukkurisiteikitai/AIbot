# YorselfLM
YorselfLMは、LLM（大規模言語モデル）を活用した高度な対話システムです。
[仕組み]
https://qiita.com/Nikeri/items/3508fa6fe3fca6f5778f


## 機能

- マルチモーダルな対話処理
- エピソード管理と分析
- データベース管理
- 設定可能な設定ファイル
- テスト環境の整備

## 必要条件

- Python 3.8以上
- 必要なパッケージは `requirements.txt` に記載

## インストール

1. リポジトリをクローン
```bash
git clone [repository-url]
```

2. 仮想環境の作成
```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
.\venv\Scripts\activate   # Windowsの場合
```

3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

## 設定

`config.yaml` ファイルで以下の設定が可能です：
- データベース設定
- LLM設定
- システム設定
- その他のカスタマイズ可能なパラメータ

## 使用方法

1. 設定ファイルの準備
2. データベースの初期化
3. システムの起動

## テスト

テストの実行：
```bash
python -m pytest tests/
```

または、Windowsの場合：
```bash
.\test.bat
```

## プロジェクト構造

- `llm_handler_multi.py`: メインのLLM処理モジュール
- `episode_handler.py`: エピソード管理
- `db_manager.py`: データベース管理
- `llm_analyzer.py`: LLM分析機能
- `config.yaml`: 設定ファイル
- `tests/`: テストディレクトリ
- `docs/`: ドキュメント
- `data/`: データファイル
- `models/`: モデルファイル
- `utils/`: ユーティリティ関数


## 貢献

このプロジェクトへの貢献を歓迎します。以下のガイドラインに従ってください：

### 開発の流れ

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

### コーディング規約

- PythonのPEP 8スタイルガイドに従ってください
- 新しい機能を追加する場合は、テストを必ず作成してください
- ドキュメントの更新を忘れずに行ってください
- コミットメッセージは明確で具体的に記述してください

### バグ報告

バグを発見した場合は、以下の情報を含めてIssueを作成してください：
- バグの詳細な説明
- 再現手順
- 期待される動作
- スクリーンショット（該当する場合）
- 環境情報（OS、Pythonバージョンなど）

### 機能リクエスト

新しい機能の提案は大歓迎です。以下の情報を含めてIssueを作成してください：
- 機能の詳細な説明
- その機能が必要な理由
- 実装案（もしあれば）

### プルリクエストのレビュー

プルリクエストは以下の基準でレビューされます：
- コードの品質と可読性
- テストの網羅性
- ドキュメントの更新
- 既存の機能との互換性
