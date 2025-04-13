# main.py
import os
import discord
from discord.ext import commands
from discord import app_commands # スラッシュコマンド用
import logging
from dotenv import load_dotenv
import db_manager # データベースモジュール
import llm_handler # LLMモジュール
import asyncio

# --- 初期設定 ---
load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Botのインテント設定 (メッセージ内容とDMを読む権限が必要)
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.guild_messages = True # サーバーでのメッセージも受け取る

# Botオブジェクトの作成
bot = commands.Bot(command_prefix="!", intents=intents) # プレフィックスは今は使わないが形式上

# ロガー設定
discord.utils.setup_logging(level=logging.INFO) # INFOレベル以上をログ出力
logger = logging.getLogger('discord')

# --- イベントハンドラ ---
@bot.event
async def on_ready():
    """Botが起動したときに実行される"""
    logger.info(f'Logged in as {bot.user.name} ({bot.user.id})')
    await db_manager.initialize_database() # データベース初期化
    # スラッシュコマンドを同期
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

# --- ヘルパー関数 ---
def is_dm(interaction: discord.Interaction) -> bool:
    """インタラクションがDMで行われたか判定する"""
    return interaction.guild is None

# --- スラッシュコマンド定義 ---

@bot.tree.command(name="help", description="Botの使い方を表示します。")
async def help_command(interaction: discord.Interaction):
    """ヘルプコマンド"""
    embed = discord.Embed(title="YourSelf LM (Discord Proto) の使い方", color=discord.Color.blue())
    embed.description = "あなた自身の分身(AIアバター)と対話できるBotです。"

    embed.add_field(name="`/add_info` (DM専用)", value="あなたの情報をAIに教えます。\n例: `/add_info type:habit content:語尾に「～だね」ってよく使う`\n**typeの種類:** `habit`(口癖/文体), `likes`(好きなもの), `profile`(自己紹介), `tone`(話し方) など自由に設定できます。", inline=False)
    embed.add_field(name="`/show_info` (DM専用)", value="登録されているあなたの情報を表示します。", inline=False)
    embed.add_field(name="`/reset` (DM専用)", value="登録されているあなたの情報を全て削除します。", inline=False)
    embed.add_field(name="`/chat`", value="AIアバターに話しかけます。\n例: `/chat message:今日の調子はどう？`", inline=False)
    embed.add_field(name="`/help`", value="このヘルプを表示します。", inline=False)

    embed.add_field(
        name="データ管理について",
        value=(
            "`/add_info` で登録された情報はBot内部のデータベースに保存されます。\n"
            "情報の登録、確認、削除は **DMでのみ** 行えます。\n"
            "`/chat` はサーバーチャンネルでも利用できますが、その際は登録された情報が応答生成に使われます。\n"
            "プライバシーに十分配慮し、公開されても問題ない範囲の情報をご利用ください。"
        ),
        inline=False
    )
    await interaction.response.send_message(embed=embed, ephemeral=True) # ephemeral=Trueで本人にのみ表示

# --- 情報管理コマンド (DM専用) ---

@bot.tree.command(name="add_info", description="あなたの情報をAIに教えます。(DMでのみ実行可能)")
@app_commands.describe(
    info_type="情報の種類 (例: habit, likes, profile, tone)",
    content="情報の内容"
)
async def add_info_command(interaction: discord.Interaction, info_type: str, content: str):
    """情報追加コマンド"""
    if not is_dm(interaction):
        await interaction.response.send_message("このコマンドはDMでのみ実行できます。", ephemeral=True)
        return

    user_id = interaction.user.id
    success = await db_manager.add_user_info(user_id, info_type.lower(), content) # typeは小文字で統一

    if success:
        await interaction.response.send_message(f"情報タイプ `{info_type}` を登録/更新しました。", ephemeral=True)
    else:
        await interaction.response.send_message("情報の登録中にエラーが発生しました。", ephemeral=True)

@bot.tree.command(name="show_info", description="登録されているあなたの情報を表示します。(DMでのみ実行可能)")
async def show_info_command(interaction: discord.Interaction):
    """情報表示コマンド"""
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
        # 長すぎる内容は省略するなどの工夫も可能
        display_content = (content[:100] + '...') if len(content) > 100 else content
        embed.add_field(name=f"`{info_type}`", value=display_content, inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="reset", description="登録されているあなたの情報を全て削除します。(DMでのみ実行可能)")
async def reset_command(interaction: discord.Interaction):
    """情報リセットコマンド"""
    if not is_dm(interaction):
        await interaction.response.send_message("このコマンドはDMでのみ実行できます。", ephemeral=True)
        return

    user_id = interaction.user.id
    # 確認ステップを入れる方が親切かもしれないが、プロトタイプでは省略
    success = await db_manager.delete_user_info(user_id)

    if success:
        await interaction.response.send_message("登録情報を全て削除しました。", ephemeral=True)
    else:
        await interaction.response.send_message("情報の削除中にエラーが発生しました。", ephemeral=True)

# --- チャットコマンド ---

@bot.tree.command(name="chat", description="AIアバターに話しかけます。")
@app_commands.describe(message="AIアバターへのメッセージ")
async def chat_command(interaction: discord.Interaction, message: str):
    """チャットコマンド"""
    user_id = interaction.user.id
    await interaction.response.defer(thinking=True) # 応答生成に時間がかかるため、考え中...表示

    # ユーザー情報をDBから取得
    user_db_info = await db_manager.get_user_info(user_id)

    # LLMに応答生成を依頼
    ai_response = await llm_handler.generate_response(user_id, message, user_db_info)

    # 応答を送信 (followup.sendを使う)
    await interaction.followup.send(f"> {interaction.user.mention}: {message}\n\n{ai_response}")


# --- Botの実行 ---
if __name__ == "__main__":
    if BOT_TOKEN is None:
        logger.critical("DISCORD_BOT_TOKEN is not set in .env file.")
    elif os.getenv("OPENAI_API_KEY") is None:
        logger.critical("OPENAI_API_KEY is not set in .env file.")
    else:
        bot.run(BOT_TOKEN)