import discord
from discord.ext import commands
import os
import asyncio
import whisper
import openai # LM Studio互換APIにも使用
import requests
import wave
import io
import tempfile
import time
from dotenv import load_dotenv

# --- 設定 ---
load_dotenv() # .envファイルから環境変数を読み込む

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # LM Studioでは不要な場合が多い
LM_STUDIO_API_BASE = "http://localhost:1234/v1" # LM StudioのAPIエンドポイント
LM_STUDIO_MODEL_NAME = "loaded-model-name" # LM Studioでロードしているモデル名（APIによっては不要/任意）

VOICEVOX_URL = "http://127.0.0.1:50021" # ローカルのVOICEVOXエンジンのURL
# 重要：ご自身のVOICEVOX環境で "/speakers" を確認し、"YS4" の正しいIDに置き換えてください
YS4_SPEAKER_ID = 46 # 仮のID。必ず確認・修正してください！

WHISPER_MODEL_SIZE = "base" # or "tiny", "small", "medium", "large"
RECORDING_TIMEOUT_SECONDS = 10 # 何秒間録音するか（デモ用）

# --- 初期化 ---
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# LM Studio APIを使用するためのOpenAIクライアント設定
# APIキーはダミーか空文字列で良い場合が多い（LM Studioの設定による）
lm_studio_client = openai.OpenAI(base_url=LM_STUDIO_API_BASE, api_key="not-needed")

# Whisperモデルの読み込み
print("Loading Whisper model...")
try:
    whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
    print(f"Whisper model '{WHISPER_MODEL_SIZE}' loaded.")
except Exception as e:
    print(f"Error loading Whisper model: {e}")
    whisper_model = None

voice_clients = {}
user_audio_data = {}

# --- ヘルパー関数 ---

async def transcribe_audio(audio_path: str) -> str:
    """Whisperを使って音声ファイルを文字起こしする（ブロッキング処理）"""
    if not whisper_model:
        print("Whisper model not loaded.")
        return "Error: Whisper model not loaded."
    try:
        print(f"Transcribing {audio_path}...")
        result = whisper_model.transcribe(audio_path, fp16=False) # fp16=False for CPU
        print(f"Transcription result: {result['text']}")
        return result["text"]
    except Exception as e:
        print(f"Error during transcription: {e}")
        return f"Error during transcription: {e}"

async def get_ai_response(text: str) -> str:
    """LM Studio APIを使って応答を生成する（ブロッキング処理）"""
    try:
        print(f"Sending to LM Studio: {text}")
        response = lm_studio_client.chat.completions.create(
            model=LM_STUDIO_MODEL_NAME, # LM Studioでロード中のモデルを指定 (設定によっては不要)
            messages=[
                {"role": "system", "content": "あなたは親切なAIアシスタントです。"},
                {"role": "user", "content": text}
            ],
            temperature=0.7, # 必要に応じて調整
        )
        ai_text = response.choices[0].message.content.strip()
        print(f"LM Studio response: {ai_text}")
        return ai_text
    except openai.APIConnectionError as e:
         print(f"LM Studio connection error: {e}")
         return f"Error: LM Studioへの接続に失敗しました。サーバーが起動していますか？ ({LM_STUDIO_API_BASE})"
    except Exception as e:
        print(f"Error getting AI response from LM Studio: {e}")
        return f"Error getting AI response: {e}"

async def generate_ys4_speech(text: str) -> bytes | None:
    """VOICEVOX APIを使って指定モデル(YS4)の音声を生成する（ブロッキング処理）"""
    try:
        # 1. audio_query (音声合成用のクエリを作成)
        print(f"Generating VOICEVOX query for YS4 (ID: {YS4_SPEAKER_ID}): {text}")
        res_query = requests.post(
            f"{VOICEVOX_URL}/audio_query",
            params={"text": text, "speaker": YS4_SPEAKER_ID}
        )
        res_query.raise_for_status() # エラーチェック
        audio_query = res_query.json()
        # 必要に応じて audio_query のパラメータを調整 (speedScale, pitchScale 등)
        # audio_query["speedScale"] = 1.2
        print("VOICEVOX query generated.")

        # 2. synthesis (音声合成を実行)
        print("Synthesizing VOICEVOX audio...")
        res_synth = requests.post(
            f"{VOICEVOX_URL}/synthesis",
            params={"speaker": YS4_SPEAKER_ID},
            json=audio_query
        )
        res_synth.raise_for_status() # エラーチェック
        print("VOICEVOX audio synthesized.")
        return res_synth.content # WAVデータのバイト列を返す
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with VOICEVOX ({VOICEVOX_URL}): {e}")
        if e.response is not None:
            print(f"VOICEVOX Response Status: {e.response.status_code}")
            print(f"VOICEVOX Response Body: {e.response.text}")
            if e.response.status_code == 404:
                 return f"Error: VOICEVOX APIが見つかりません。URL ({VOICEVOX_URL}) やSpeaker ID ({YS4_SPEAKER_ID}) を確認してください。"
            elif e.response.status_code == 422:
                 return f"Error: VOICEVOXへのリクエストが無効です。Speaker ID ({YS4_SPEAKER_ID}) が正しいか、テキストが長すぎないか確認してください。"
        return f"Error: VOICEVOXとの通信に失敗しました。エンジンが起動していますか？ ({VOICEVOX_URL})"
    except Exception as e:
        print(f"Error during TTS generation: {e}")
        return f"Error during TTS generation: {e}" # エラーメッセージを返すように変更

# --- Discord Sinkクラス (変更なし) ---
class UserAudioSink(discord.Sink):
    def __init__(self, filters=None):
        super().__init__(filters=filters)
        self.user_audio_buffers = {} # {user_id: io.BytesIO}

    def write(self, data, user):
        if user is None:
            return
        if user.id not in self.user_audio_buffers:
            self.user_audio_buffers[user.id] = io.BytesIO()
        self.user_audio_buffers[user.id].write(data)

    def cleanup(self):
        print("Sink cleanup called.")
        for user_id, buffer in self.user_audio_buffers.items():
            if buffer.getbuffer().nbytes > 0:
                buffer.seek(0)
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                     with wave.open(temp_wav, 'wb') as wf:
                        wf.setnchannels(self.CHANNELS)
                        wf.setsampwidth(2)
                        wf.setframerate(self.SAMPLING_RATE)
                        wf.writeframes(buffer.getvalue())
                     print(f"Saved temporary audio for user {user_id} to {temp_wav.name}")
                     user_audio_data[user_id] = temp_wav.name
            buffer.close()
        self.user_audio_buffers.clear()


# --- Botイベントハンドラ (変更なし) ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('Bot is ready.')
    if not whisper_model:
        print("Warning: Whisper model failed to load. Transcription will not work.")

# --- Botコマンド (!join, !leave は変更なし) ---
@bot.command(name='join')
async def join(ctx: commands.Context):
    """Botをボイスチャネルに参加させます"""
    if ctx.author.voice is None:
        await ctx.send("あなたはボイスチャンネルに参加していません。")
        return

    channel = ctx.author.voice.channel
    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(channel)
    else:
        vc = await channel.connect()
        voice_clients[ctx.guild.id] = vc
        await ctx.send(f'ボイスチャンネル「{channel.name}」に参加しました。')

@bot.command(name='leave')
async def leave(ctx: commands.Context):
    """Botをボイスチャネルから退出させます"""
    if ctx.voice_client:
        guild_id = ctx.guild.id
        if guild_id in voice_clients:
            vc = voice_clients[guild_id]
            if vc.is_recording():
                vc.stop_recording()
            await vc.disconnect()
            del voice_clients[guild_id]
            user_audio_data.clear()
            await ctx.send("ボイスチャンネルから退出しました。")
        else:
            await ctx.voice_client.disconnect()
            user_audio_data.clear()
            await ctx.send("ボイスチャンネルから退出しました。")
    else:
        await ctx.send("Botはボイスチャンネルに参加していません。")

# --- 音声処理のメインロジック (TTS関数呼び出し部分を修正) ---
async def process_and_respond(ctx: commands.Context, audio_path: str):
    """音声ファイルを処理し、AI応答を生成して再生する"""
    if not os.path.exists(audio_path):
        print(f"Audio file not found: {audio_path}")
        await ctx.send("エラー: 録音ファイルが見つかりません。")
        return

    vc = voice_clients.get(ctx.guild.id)
    if not vc or not vc.is_connected():
        print("Bot is not connected to a voice channel for playback.")
        await ctx.send("エラー: Botが応答を再生するためのボイスチャンネルに接続していません。")
        # 一時ファイルを削除しておく
        try: os.remove(audio_path)
        except OSError: pass
        return

    try:
        # 1. Whisperで文字起こし (非同期実行)
        await ctx.send(f"録音ファイルを処理中... ({os.path.basename(audio_path)})")
        transcribed_text = await asyncio.to_thread(transcribe_audio, audio_path)
        if transcribed_text.startswith("Error:"):
            await ctx.send(f"文字起こしエラー: {transcribed_text}")
            return # エラー時はここで終了

        await ctx.send(f"文字起こし結果: 「{transcribed_text}」")

        # 2. AI(LM Studio)で応答生成 (非同期実行)
        await ctx.send("AI応答を生成中 (LM Studio)...")
        ai_response = await asyncio.to_thread(get_ai_response, transcribed_text)
        if ai_response.startswith("Error:"):
            await ctx.send(f"AI応答生成エラー: {ai_response}")
            return # エラー時はここで終了

        await ctx.send(f"AIの応答: 「{ai_response}」")

        # 3. VOICEVOX(YS4)で音声合成 (非同期実行)
        await ctx.send(f"音声(YS4)を生成中 (VOICEVOX)...")
        tts_result = await asyncio.to_thread(generate_ys4_speech, ai_response)

        # generate_ys4_speech がエラー時に文字列メッセージを返すようにしたのでチェック
        if isinstance(tts_result, str) and tts_result.startswith("Error:"):
            await ctx.send(f"音声合成エラー: {tts_result}")
            return # エラー時はここで終了
        elif tts_result is None: # 何らかの理由で None が返ってきた場合 (旧仕様の名残)
            await ctx.send("音声合成中に不明なエラーが発生しました。")
            return
        else:
             # 成功時は tts_result に音声データのbytesが入っている
             tts_audio_data = tts_result


        # 4. Discordで再生
        # 再生用に一時ファイルに保存
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_tts_file:
            temp_tts_path = temp_tts_file.name
            temp_tts_file.write(tts_audio_data)
            print(f"Saved temporary TTS audio to {temp_tts_path}")

        if vc.is_playing():
            vc.stop() # 再生中なら停止

        await ctx.send("応答を再生します...")
        audio_source = discord.FFmpegPCMAudio(temp_tts_path)
        vc.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(cleanup_tts_file(temp_tts_path, e), bot.loop))

    except Exception as e:
        print(f"Error during process_and_respond: {e}")
        await ctx.send(f"処理中に予期せぬエラーが発生しました: {e}")

    finally:
        # Whisper用の一時ファイルを削除
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"Deleted temporary transcription file: {audio_path}")
        except OSError as e:
            print(f"Error deleting temporary transcription file {audio_path}: {e}")

async def cleanup_tts_file(filepath: str, error: Exception | None):
    """再生終了後に呼ばれるコールバック (TTS一時ファイル削除用)"""
    if error:
        print(f'Player error: {error}')
    try:
        # 少し待ってから削除 (ファイルがまだ掴まれている場合があるため)
        await asyncio.sleep(1)
        if os.path.exists(filepath):
             os.remove(filepath)
             print(f"Deleted temporary TTS file: {filepath}")
    except OSError as e:
        print(f"Error deleting temporary TTS file {filepath}: {e}")


@bot.command(name='listen')
async def listen_command(ctx: commands.Context):
    """短時間、音声を録音して処理します"""
    vc = voice_clients.get(ctx.guild.id)
    if not vc or not vc.is_connected():
        await ctx.send("Botがボイスチャンネルに参加していません。`!join`コマンドを使用してください。")
        return
    if vc.is_recording():
        await ctx.send("現在録音中です。")
        return

    user_audio_data.clear() # 前のデータをクリア

    await ctx.send(f"{RECORDING_TIMEOUT_SECONDS}秒間、音声を録音します...")

    vc.start_recording(UserAudioSink(), recording_finished_callback, ctx)

    await asyncio.sleep(RECORDING_TIMEOUT_SECONDS)

    if vc.is_recording():
        vc.stop_recording()
        await ctx.send("録音を終了しました。処理を開始します。")
    else:
        await ctx.send("録音は既に停止しています。")


# 録音終了時に呼び出されるコールバック (変更なし)
async def recording_finished_callback(sink: UserAudioSink, ctx: commands.Context):
    print("Recording finished callback triggered.")
    await asyncio.sleep(0.5) # cleanup処理の完了を少し待つ

    processed_users = 0
    audio_paths_to_process = list(user_audio_data.items()) # イテレーション用にコピー
    user_audio_data.clear() # 元の辞書はクリア

    if not audio_paths_to_process:
         await ctx.send("録音されましたが、処理できる音声データが見つかりませんでした。")
         return

    # デモでは簡単化のため、最初に見つかった音声だけ処理
    user_id, audio_path = audio_paths_to_process[0]
    print(f"Processing recorded audio for user {user_id}: {audio_path}")
    # バックグラウンドで処理を開始し、完了を待たない
    asyncio.create_task(process_and_respond(ctx, audio_path))
    processed_users += 1

    # 残りのファイルがあれば削除（複数ユーザー同時処理しない場合）
    for uid, path in audio_paths_to_process[1:]:
        try:
            if os.path.exists(path):
                 os.remove(path)
                 print(f"Deleted unused audio file: {path}")
        except OSError as e:
            print(f"Error deleting unused audio file {path}: {e}")


# --- Botの実行 ---
if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN is not set in .env file.")
    # LM Studioの場合はAPIキーチェックは削除
    # elif not OPENAI_API_KEY:
    #     print("Error: OPENAI_API_KEY is not set.")
    elif YS4_SPEAKER_ID is None or not isinstance(YS4_SPEAKER_ID, int):
         print(f"Error: YS4_SPEAKER_ID ({YS4_SPEAKER_ID}) is not a valid integer. Please check VOICEVOX '/speakers' and update the script.")
    elif not whisper_model:
        print("Error: Whisper model could not be loaded. Bot cannot start.")
    else:
        try:
            # VOICEVOXとLM Studioのサーバーが起動しているか簡単なチェック
            try:
                requests.get(f"{VOICEVOX_URL}/version", timeout=2)
                print(f"VOICEVOX engine found at {VOICEVOX_URL}")
            except requests.exceptions.RequestException:
                print(f"Warning: Could not connect to VOICEVOX engine at {VOICEVOX_URL}. Please ensure it is running.")
                # 続行するかどうかは要検討

            try:
                # LM Studioは /v1/models などで疎通確認できる場合がある
                lm_studio_client.models.list() # ダミーリクエスト
                print(f"LM Studio API endpoint seems reachable at {LM_STUDIO_API_BASE}")
            except openai.APIConnectionError:
                 print(f"Warning: Could not connect to LM Studio API at {LM_STUDIO_API_BASE}. Please ensure the server is running.")
                 # 続行するかどうかは要検討
            except Exception as e:
                 print(f"Warning: Could not verify LM Studio connection ({e}).")


            print("Starting Discord Bot...")
            bot.run(DISCORD_BOT_TOKEN)
        except discord.LoginFailure:
            print("Error: Invalid Discord Bot Token.")
        except Exception as e:
            print(f"An error occurred while running the bot: {e}")