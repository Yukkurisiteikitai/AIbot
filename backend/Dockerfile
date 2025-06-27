# ベースイメージとしてNVIDIA CUDA Toolkitを含むイメージを指定
# CUDA 12.4 と cuDNN 8 に対応するイメージを選びます
FROM nvidia/cuda:12.4.1-cudnn8-devel-ubuntu22.04

# 環境変数の設定
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
# llama-cpp-pythonビルド時にCUDAを利用するように設定
ENV CMAKE_ARGS="-DLLAMA_CUBLAS=on"
ENV FORCE_CUDA="1"

# 必要なパッケージのインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.11 python3-pip python3.11-venv git wget && \
    rm -rf /var/lib/apt/lists/*

# Pythonのバージョンをpython3.11に固定
RUN ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# 作業ディレクトリの作成と設定
WORKDIR /app

# リポジトリをクローンする (またはローカルのファイルをコピーする)
# ここではローカルのファイルをコピーする方法を採用します
COPY . /app

# Pythonの依存関係をインストール
# requirements.txt がリポジトリのルートにあると仮定しています
RUN pip install --no-cache-dir -r requirements.txt

# llama-cpp-python をCUDAサポート付きで再インストール (またはインストール)
# requirements.txt に llama-cpp-python が含まれている場合は、
# 一度アンインストールしてから再インストールするか、
# requirements.txt から削除してここでインストールします。
# ここでは、一度アンインストールしてから再インストールする例を示します。
RUN pip uninstall -y llama-cpp-python
RUN pip install --no-cache-dir llama-cpp-python

# ポートの開放 (必要に応じて変更してください)
# EXPOSE 8000

# コンテナ起動時のデフォルトコマンド (必要に応じて変更してください)
# CMD ["python", "your_script_name.py"]