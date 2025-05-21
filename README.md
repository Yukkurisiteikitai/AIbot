# AIbot

AIbotは、LLM（大規模言語モデル）を活用した高度な対話システムです。

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

2. 仮想環境を作成して有効化
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

## ライセンス

[ライセンス情報を追加]

## 貢献

[貢献ガイドラインを追加]
