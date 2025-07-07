# Setting
Backend_url = "https://c38a-240d-1a-1038-4a00-c57a-eae5-97d4-4284.ngrok-free.app"

Modes_CONST = {
    "Talk": {
        "description": "再現した人格にそのまま話すことができる",
        "value": "talk"
    },
    "Check": {
        "description":
        "AIの現在の思考をStreamingする基本的にBackendのLoggingをそのまま送信するのに加えてAPIのoptionに思考のストリーミングまでしてもらう仕様、かなり細かい",
        "value": "Check"
    },
    "End": {
        "description": "ロールプレイのセッションの終了を意味する基本的にこの単語が含まれると終了になる",
        "value": "end"
    },
    "MAD": {
        "description":
        "わしゃしらん責任もとらん動作が不安定になろうが知らん、だからよう完璧な自由をやろう。\n完全にフィルターを外しモデルの推論そのものの性能を発揮するもの 現在使用しているGemmaモデルの制限を解除する単語を最初に加えて置いた上で推論させる",
        "value": "mad"
    },
}

mode = "talk"

if mode == "talk":
    print("Talk Mode")
elif mode == "check":
    print("Now Start_Check")
elif mode == "end":
    print("会話を終了し分析を開始します。")
    mode = "analysis"
elif mode == "analysis":
    print("本名のモードですね。あなたとの会話から分析を始めるよ")
elif mode == "mad":
    print(
        "開発者もどうなるか正直分かりません。もし面白いことが起きたら「1hourgoodattack@gmail.com」にスクショとテキスト文で送ってください。\n解決策(考えついたら)やコメントを返信します。"
    )
