# AIbot








# install 
1. install other  
LM Studioをインストールしてください  
https://lmstudio.ai/  
からインストールできます。

LM Studioからllama.cppをインストールしてください

LM Studioの検索窓があるのでそこから使いたいモデルを入れてください。
特に使いたいモデルがなければ軽い`gemma3-1B`をおすすめします

2. discord Bot  
https://discord.com/developers/  
からデベロッパー登録をしてください  

そしたら次にアプリケーションを作成
そのアプリケーションのなかにあるbotの項目からbotを選択し、reset Tokenでトークンを発行してください


3. make .env  

```
DISCORD_BOT_TOKEN="2で説明したトークンを入れてください"
LM_STUDIO_BASE_URL="http://localhost:1234/v1" #デフォルト http://localhost:1234/v1
LM_STUDIO_MODEL_REQUEST="軽いモデル名(1~2B)をf書いてください"
LM_STUDIO_MODEL_RESPONSE="重いしっかりとしたモデル名(12B程度)を書いてください"
```

 
4. make venv   
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

# Usage

1. LM StudioのDeveloperからSelect a model to loadがあるので、それからモデルをロードしてください。
2. Status:stoped という文字の隣にスイッチがあるのでそれをオンにしてください。
3. `python main.py`で起動してください。