from llama_cpp import Llama

# --- 設定項目 ---
# 注意: ここにご自身のGemma GGUFモデルファイルへの正しいパスを指定してください。
# 例: MODEL_PATH = "./models/gemma-7b-it.gguf"
MODEL_PATH = "../../models/gemma-3-1b-it-Q4_K_M.gguf" # あなたのモデルパスに置き換えてください

# GPUにオフロードするレイヤー数。-1にすると可能な限り全てのレイヤーをGPUにオフロードします。
# GPUがない場合やCPUのみで実行したい場合は0を指定してください。
N_GPU_LAYERS = -1 # 例: Apple Silicon Metalなら -1 や 1 が一般的

# モデルのコンテキストウィンドウのサイズ。
CONTEXT_SIZE = 2048

# --- Llamaモデルのロード ---
try:
    print(f"モデル '{MODEL_PATH}' をロード中です...")
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=CONTEXT_SIZE,
        n_gpu_layers=N_GPU_LAYERS,
        verbose=False  # Trueにすると llama.cpp からの詳細なログが出力されます
    )
    print("モデルのロードが完了しました。")
except Exception as e:
    print(f"エラー: モデルのロードに失敗しました。")
    print(f"モデルパス '{MODEL_PATH}' が正しいか、ファイルが存在するか確認してください。")
    print(f"詳細: {e}")
    exit()

# --- ユーザーの質問 ---
user_question = "日本の首都はどこですか？"
print(f"\nユーザーの質問: {user_question}")

# --- 1. テキストをトークンにエンコード ---
print("\n--- エンコード処理 ---")
# tokenizeメソッドはバイト列を期待するので、.encode('utf-8') が必要
# add_bos=True でシーケンスの開始を示すBOSトークンを先頭に追加します。これは多くのモデルで推奨されます。
prompt_tokens = llm.tokenize(user_question.encode('utf-8'), add_bos=True)
print(f"エンコードされたトークンID: {prompt_tokens}")
# 各トークンが何に対応するか（オプション、デバッグ用）
# for token_id in prompt_tokens:
#     try:
#         # llama.cpp のバージョンによって llama_token_to_piece が利用可能か確認
#         if hasattr(llm, 'llama_token_to_piece'):
#             token_str = llm.llama_token_to_piece(token_id)
#         elif hasattr(llm, 'detokenize'): # 古いバージョンではdetokenizeを単一トークンに使うことも
#             token_str = llm.detokenize([token_id]).decode('utf-8', errors='replace')
#         else:
#             token_str = f"(ID: {token_id})"
#         print(f"  ID: {token_id} -> '{token_str}'")
#     except Exception as e:
#         print(f"  ID: {token_id} -> (デコードエラー: {e})")
# prompt_tokens = [2, 76444, 120211, 237048, 67923, 73727, 237536]

# --- 2. トークンから直接推論して次のトークンを生成 ---
print("\n--- 推論処理 (次のトークン予測) ---")

# モデルのコンテキストをリセット（前の推論の影響を避けるため）
llm.reset()

# プロンプトトークンをモデルに評価させる
# n_past は、これまでに処理したトークンの数。最初は0。
# n_threads は利用するスレッド数。Noneでデフォルト。
print(f"プロンプトトークンを評価中...")
llm.eval(prompt_tokens)
print(f"プロンプトトークンの評価完了。")

# 生成するトークンの最大数
max_new_tokens = 30
generated_tokens = []

print(f"\n次の{max_new_tokens}個のトークンを生成します:")
for i in range(max_new_tokens):
    # 次のトークンをサンプリング (最も基本的なサンプリング)
    # temperatureなどのサンプリングパラメータは Llama オブジェクト初期化時や、
    # より高度なサンプリングメソッド (llm.sample_*) で指定できます。
    # ここでは、Llamaオブジェクトに設定されたデフォルトのサンプリング設定が使われます。
    # (明示的に設定したい場合は、Llamaインスタンス作成時に temp, top_k, top_p などを指定するか、
    #  llama_cpp.llama_sample* 関数群を直接利用します)
    next_token = llm.sample(temp=0.7) # 例: 温度を0.7に設定してサンプリング

    # EOS (End of Sequence) トークンが出たら生成を終了
    if next_token == llm.token_eos():
        print("  EOSトークンが生成されたため、終了します。")
        break

    generated_tokens.append(next_token)
    print(f"  生成されたトークンID [{i+1}]: {next_token}")

    # 新しく生成されたトークンをモデルに評価させる (次の予測のため)
    # 1トークンずつ評価する場合は、[next_token] のようにリストで渡します
    llm.eval([next_token])

print(f"\n生成されたトークンIDのシーケンス: {generated_tokens}")


# --- 3. トークンをテキストにデコード ---
print("\n--- デコード処理 ---")
if generated_tokens:
    # detokenizeメソッドはバイト列を返すので、.decode('utf-8') が必要
    # errors='replace' はデコードできない文字があった場合に代替文字に置き換えます
    decoded_text = llm.detokenize(generated_tokens).decode('utf-8', errors='replace')
    print(f"デコードされたテキスト: {decoded_text}")
else:
    print("デコードするトークンがありません。")

print("\n--- 処理完了 ---")