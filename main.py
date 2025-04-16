# main.py
import os
import discord
from discord.ext import commands
from discord import app_commands
import logging
import logging.handlers
from dotenv import load_dotenv
import db_manager
import llm_handler
import asyncio
import signal
import sys
import platform # プラットフォーム判定用

# --- 初期設定 ---
load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
LM_STUDIO_URL = os.getenv("LM_STUDIO_BASE_URL")
LOG_FILE = "bot.log"

# --- ロガー設定 ---
log_formatter = logging.Formatter('%(asctime)s [%(levelname)-5.5s] [%(name)-12.12s]: %(message)s')
log_level = logging.INFO

root_logger = logging.getLogger()
root_logger.setLevel(log_level)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
root_logger.addHandler(console_handler)

file_handler = None # グローバルでアクセスできるように初期化
try:
    file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)
except Exception as e:
    root_logger.error(f"Failed to set up file logging to {LOG_FILE}: {e}")

discord_logger = logging.getLogger('discord')
logger = logging.getLogger('discord.main')

# --- Bot設定 ---
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.guild_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- シグナルハンドラ & 終了処理 ---
shutdown_requested = False # 複数回シグナルを受け取った場合のフラグ

async def handle_exit(sig: signal.Signals, loop: asyncio.AbstractEventLoop):
    """非同期の終了処理"""
    global shutdown_requested
    if shutdown_requested:
        logger.warning("Shutdown already requested, ignoring additional signal.")
        return
    shutdown_requested = True # フラグを立てる

    logger.warning(f"Received exit signal {sig.name}... Shutting down gracefully.")

    # ログハンドラのクローズ
    if file_handler:
        logger.info(f"Closing log file handler for {LOG_FILE}...")
        file_handler.close()
        root_logger.removeHandler(file_handler)

    # Discord Bot を閉じる
    logger.info("Closing Discord Bot connection...")
    try:
        await bot.close()
        logger.info("Discord Bot closed.")
    except Exception as e:
        logger.error(f"Error while closing the bot: {e}")

    # イベントループの停止 (bot.close() が完了すれば通常不要だが、念のため)
    # loop.stop() # これは非同期コンテキストからは呼ばない方が良い

def sync_signal_handler(sig: int, frame):
    """同期的なシグナルハンドラ (Windows用)"""
    logger.debug(f"Caught signal {sig} in sync handler.")
    loop = asyncio.get_running_loop()
    # 非同期関数 handle_exit をイベントループで安全に実行するようスケジュール
    loop.call_soon_threadsafe(asyncio.create_task, handle_exit(signal.Signals(sig), loop))

# --- イベントハンドラ ---
@bot.event
async def on_ready():
    global file_handler # グローバル変数を更新する可能性があるため宣言
    logger.info(f'Logged in as {bot.user.name} ({bot.user.id})')
    try:
        await db_manager.initialize_database()
        logger.info("Database check/initialization complete.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # await bot.close()
        # return

    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

    # --- シグナルハンドラ登録 ---
    loop = asyncio.get_running_loop()
    current_platform = platform.system()

    if current_platform == "Windows":
        logger.info("Running on Windows. Registering SIGINT handler using signal.signal().")
        try:
            # Windows では SIGINT (Ctrl+C) のみ捕捉可能
            signal.signal(signal.SIGINT, sync_signal_handler)
            # SIGTERM は Windows では通常 signal() で捕捉できない
            # signal.signal(signal.SIGTERM, sync_signal_handler) # これは機能しない可能性が高い
        except ValueError as e:
             logger.error(f"Could not set signal handler on Windows (might be running in an environment where it's restricted): {e}")
        except Exception as e:
             logger.error(f"An unexpected error occurred setting signal handler on Windows: {e}")

    elif current_platform in ("Linux", "Darwin"): # Linux or macOS
        logger.info(f"Running on {current_platform}. Registering SIGINT and SIGTERM handlers using loop.add_signal_handler().")
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(
                    sig,
                    lambda s=sig: asyncio.create_task(handle_exit(s, loop))
                )
            except NotImplementedError:
                 # 予期せず add_signal_handler が使えない環境だった場合 (WSL旧版など?)
                 logger.warning(f"loop.add_signal_handler for {sig.name} is not implemented on this {current_platform} system. Falling back to signal.signal for SIGINT if possible.")
                 if sig == signal.SIGINT:
                     try:
                        signal.signal(signal.SIGINT, sync_signal_handler)
                     except Exception as e:
                        logger.error(f"Fallback signal.signal(SIGINT) registration failed: {e}")

            except Exception as e:
                 logger.error(f"An unexpected error occurred setting signal handler for {sig.name} on {current_platform}: {e}")
    else:
        logger.warning(f"Running on unrecognized platform '{current_platform}'. Signal handling might not be fully functional.")
        # SIGINTだけでも試みる
        try:
            signal.signal(signal.SIGINT, sync_signal_handler)
            logger.info("Attempted to register SIGINT handler using signal.signal() on unrecognized platform.")
        except Exception as e:
            logger.error(f"Could not set signal handler on {current_platform}: {e}")


# --- ヘルパー関数 ---
def is_dm(interaction: discord.Interaction) -> bool:
    return interaction.guild is None

# --- スラッシュコマンド定義 (変更なし) ---
@bot.tree.command(name="help", description="Botの使い方を表示します。")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="YourSelf LM (Discord Proto) の使い方", color=discord.Color.blue())
    embed.description = "あなた自身の分身(AIアバター)と対話できるBotです。"
    embed.add_field(name="`/add_info` (DM専用)", value="あなたの情報をAIに教えます。\n例: `/add_info type:habit content:語尾に「～だね」ってよく使う`\n**typeの種類:** `habit`(口癖/文体), `likes`(好きなもの), `profile`(自己紹介), `tone`(話し方) など自由に設定できます。", inline=False)
    embed.add_field(name="`/show_info` (DM専用)", value="登録されているあなたの情報を表示します。", inline=False)
    embed.add_field(name="`/reset` (DM専用)", value="登録されているあなたの情報 (`/add_info`で設定したもの) を全て削除します。", inline=False)
    embed.add_field(name="`/clear_history` (DM専用)", value="これまでのAIとの会話履歴を全て削除します。", inline=False)
    embed.add_field(name="`/chat`", value="AIアバターに話しかけます。\n例: `/chat message:今日の調子はどう？`", inline=False)
    embed.add_field(name="`/help`", value="このヘルプを表示します。", inline=False)
    embed.add_field(
        name="データ管理について",
        value=(
            "`/add_info` で登録された情報はBot内部のデータベースに保存されます。\n"
            "ユーザー情報 (`/add_info`, `/show_info`, `/reset`) および会話履歴 (`/clear_history`) の管理は **DMでのみ** 行えます。\n"
            "`/chat` はサーバーチャンネルでも利用できますが、その際は登録された情報が応答生成に使われます。\n"
            "プライバシーに十分配慮し、公開されても問題ない範囲の情報をご利用ください。\n"
            f"ログは実行ディレクトリの `{LOG_FILE}` に記録されます。"
        ),
        inline=False
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="add_info", description="あなたの情報をAIに教えます。(DMでのみ実行可能)")
@app_commands.describe(info_type="情報の種類 (例: habit, likes, profile, tone)", content="情報の内容")
async def add_info_command(interaction: discord.Interaction, info_type: str, content: str):
    if not is_dm(interaction):
        await interaction.response.send_message("このコマンドはDMでのみ実行できます。", ephemeral=True)
        return
    user_id = interaction.user.id
    success = await db_manager.add_user_info(user_id, info_type.lower(), content)
    if success:
        await interaction.response.send_message(f"情報タイプ `{info_type}` を登録/更新しました。", ephemeral=True)
    else:
        await interaction.response.send_message("情報の登録中にエラーが発生しました。", ephemeral=True)

@bot.tree.command(name="show_info", description="登録されているあなたの情報を表示します。(DMでのみ実行可能)")
async def show_info_command(interaction: discord.Interaction):
    if not is_dm(interaction):
        await interaction.response.send_message("このコマンドはDMでのみ実行できます。", ephemeral=True)
        return
    user_id = interaction.user.id
    user_data = await db_manager.get_user_info(user_id)
    if not user_data:
        await interaction.response.send_message("登録されている情報はありません。", ephemeral=True)
        return
    embed = discord.Embed(title=f"{interaction.user.display_name}さんの登録情報", color=discord.Color.green())
    for info_type, content in user_data.items():
        display_content = (content[:100] + '...') if len(content) > 100 else content
        embed.add_field(name=f"`{info_type}`", value=display_content, inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="reset", description="登録されているあなたの情報を全て削除します。(DMでのみ実行可能)")
async def reset_info_command(interaction: discord.Interaction):
    if not is_dm(interaction):
        await interaction.response.send_message("このコマンドはDMでのみ実行できます。", ephemeral=True)
        return
    user_id = interaction.user.id
    success = await db_manager.delete_user_info(user_id)
    if success:
        await interaction.response.send_message("登録されていたユーザー情報を全て削除しました。", ephemeral=True)
    else:
        await interaction.response.send_message("ユーザー情報の削除中にエラーが発生しました。", ephemeral=True)

@bot.tree.command(name="clear_history", description="これまでの会話履歴を全て削除します。(DMでのみ実行可能)")
async def clear_history_command(interaction: discord.Interaction):
    if not is_dm(interaction):
        await interaction.response.send_message("このコマンドはDMでのみ実行できます。", ephemeral=True)
        return
    user_id = interaction.user.id
    success = await db_manager.delete_conversation_history(user_id)
    if success:
        await interaction.response.send_message("会話履歴を全て削除しました。", ephemeral=True)
    else:
        await interaction.response.send_message("会話履歴の削除中にエラーが発生しました。", ephemeral=True)
@bot.tree.command(name="chat", description="AIアバターに話しかけます。")
@app_commands.describe(message="AIアバターへのメッセージ")
async def chat_command(interaction: discord.Interaction, message: str):
    user_id = interaction.user.id
    await interaction.response.defer(thinking=True, ephemeral=False)
    try:
        user_db_info = await db_manager.get_user_info(user_id)
        ai_response = await llm_handler.generate_response(user_id, message, user_db_info)

        # 応答メッセージ全体を組み立てる
        # ユーザーのメッセージ引用部分も文字数にカウントされることに注意
        user_quote = f"> {interaction.user.mention}: {message}\n\n"
        full_response_text = ai_response # LLMの応答のみを変数に

        # Discordの文字数制限
        MAX_CHARS = 2000

        # --- メッセージ分割ロジック ---
        messages_to_send = []
        # 最初のメッセージにはユーザーの引用を含める
        first_message_content = user_quote + full_response_text

        if len(first_message_content) <= MAX_CHARS:
            # 2000文字以下ならそのまま送信
            messages_to_send.append(first_message_content)
        else:
            # 2000文字を超える場合は分割する
            # 最初のチャンク (引用符 + 応答の冒頭)
            remaining_chars_first = MAX_CHARS - len(user_quote)
            if remaining_chars_first <= 0: # 引用だけで2000文字超える場合(レアケース)
                 logger.warning("User quote itself exceeds character limit.")
                 # 引用符だけ送るか、エラーにするかなど対応が必要
                 messages_to_send.append(user_quote[:MAX_CHARS]) # 強制的に切り詰め
                 # 応答部分は別途送る (ただし引用なし)
                 response_part = full_response_text
            else:
                 messages_to_send.append(user_quote + full_response_text[:remaining_chars_first])
                 response_part = full_response_text[remaining_chars_first:]

            # 残りの応答部分を2000文字ごとに分割
            # (ここでは単純な文字数分割。改行や単語境界を考慮するとより良い)
            while len(response_part) > 0:
                chunk = response_part[:MAX_CHARS]
                messages_to_send.append(chunk)
                response_part = response_part[MAX_CHARS:]

        # --- 分割したメッセージを送信 ---
        if not messages_to_send:
             logger.warning(f"No messages to send for user {user_id} after processing.")
             await interaction.followup.send("(空の応答)") # 何か送る必要がある
             return

        # 最初のチャンクは followup.send で送信
        await interaction.followup.send(messages_to_send[0])

        # 2番目以降のチャンクがある場合は、続けて送信
        # interaction.followup.send は複数回呼び出せる
        if len(messages_to_send) > 1:
            for chunk in messages_to_send[1:]:
                 # await interaction.channel.send(chunk) # こちらでも良い
                 await interaction.followup.send(chunk) # followupを続ける

    except Exception as e:
        logger.error(f"Error during chat command for user {user_id}: {e}", exc_info=True)
        try:
            # defer 済みの interaction に対するエラー通知
            if interaction.response.is_done():
                 await interaction.followup.send("申し訳ありません、応答の生成または送信中にエラーが発生しました。", ephemeral=True)
            else:
                 # defer 前にエラーが発生した場合 (可能性は低い)
                 await interaction.response.send_message("申し訳ありません、コマンドの処理中にエラーが発生しました。", ephemeral=True)
        except discord.NotFound:
            logger.warning(f"Could not send error followup for chat command to user {user_id}, interaction invalid.")
        except Exception as inner_e:
            logger.error(f"Failed to send error followup message to user {user_id}: {inner_e}")

# --- Botの実行 ---
if __name__ == "__main__":
    if BOT_TOKEN is None:
        logger.critical("FATAL: DISCORD_BOT_TOKEN is not set.")
        exit(1)

    if LM_STUDIO_URL is None:
        logger.warning("WARN: LM_STUDIO_BASE_URL is not set.")

    logger.info("Starting Discord Bot...")
    try:
        bot.run(BOT_TOKEN, log_handler=None)
    except discord.LoginFailure:
        logger.critical("FATAL: Failed to log in. Check the DISCORD_BOT_TOKEN.")
    except Exception as e:
        logger.critical(f"FATAL: An error occurred while running the bot: {e}", exc_info=True)
    finally:
        # 終了処理 (シグナルハンドラで呼ばれていなくても念のため)
        # file_handlerが存在し、かつstreamがNoneでなければ（=closeされていなければ）閉じる
        if file_handler and file_handler.stream:
             logger.info("Closing log file handler in finally block (if not already closed).")
             try:
                 file_handler.close()
             except Exception as e:
                 logger.error(f"Error closing file handler in finally block: {e}")
        logger.info("Bot process finished.")