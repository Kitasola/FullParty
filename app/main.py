# 必要なライブラリとモジュールをインポート
import os
import discord
from dotenv import load_dotenv
import sqlite3
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# SQLite データベースのセットアップ
# サーバーごとの設定（例: イベント作成のデフォルトチャンネル）を保存するためのデータベースを作成
db_path = "server_settings.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# サーバー設定テーブル
cursor.execute("""
CREATE TABLE IF NOT EXISTS server_settings (
    guild_id INTEGER PRIMARY KEY,
    channel_id INTEGER
)
""")

# イベントとチャンネルのマッピングテーブル
cursor.execute("""
CREATE TABLE IF NOT EXISTS event_channels (
    event_id INTEGER PRIMARY KEY,
    channel_id INTEGER
)
""")
conn.commit()

# イベントとチャンネルのマッピングテーブルにメッセージ送信済みフラグを追加
try:
    cursor.execute("""
    ALTER TABLE event_channels ADD COLUMN message_sent BOOLEAN DEFAULT 0
    """)
    conn.commit()
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("Column 'message_sent' already exists. Skipping ALTER TABLE.")
    else:
        raise

# 環境変数の読み込み
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DEV_GUILD_ID = os.getenv("DEV_GUILD_ID")

# 環境変数から環境タイプとギルドIDを取得
ENV_TYPE = os.getenv("ENV_TYPE", "production")  # デフォルトは本番環境
DEV_GUILD_ID = os.getenv("DEV_GUILD_ID")  # 開発環境用ギルドID

# スケジューラの初期化
scheduler = AsyncIOScheduler()

# イベント参加者を監視するタスク
async def monitor_event_participants():
    for guild in client.guilds:
        try:
            events = await guild.fetch_scheduled_events()
            for event in events:
                if event.status == discord.EventStatus.scheduled:
                    attendees = [user async for user in event.users()]
                    required_attendees = int(event.name.split("@")[1])  # 募集人数をevent.nameから抽出
                    if len(attendees) >= required_attendees:
                        cursor.execute("SELECT channel_id, message_sent FROM event_channels WHERE event_id = ?", (event.id,))
                        result = cursor.fetchone()
                        if result:
                            channel_id, message_sent = result
                            if not message_sent:
                                channel = guild.get_channel(channel_id)
                                if channel:
                                    await channel.send(f"〆 {event.name} {event.description}")
                                    cursor.execute("UPDATE event_channels SET message_sent = 1 WHERE event_id = ?", (event.id,))
                                    conn.commit()
        except Exception as e:
            print(f"Error while monitoring events in guild {guild.name}: {e}")

# 古いイベントを削除するタスク
async def cleanup_old_events():
    scheduler.pause_job('monitor_event_participants')
    for guild in client.guilds:
        try:
            events = await guild.fetch_scheduled_events()
            for event in events:
                if (discord.utils.utcnow() - event.start_time).total_seconds() > 86400:  # 1日以上経過
                    await event.delete()
                    print(f"削除されたイベント: {event.name}")
        except Exception as e:
            print(f"Error while cleaning up events in guild {guild.name}: {e}")
    scheduler.resume_job('monitor_event_participants')

# スケジューラにタスクを追加
scheduler.add_job(monitor_event_participants, 'interval', minutes=1)  # 1分ごとに実行
scheduler.add_job(cleanup_old_events, 'cron', hour=5)  # 毎日午前5時に実行

# カスタム Bot クラス
class MyBot(commands.Bot):
    async def setup_hook(self):
        scheduler.start()

# Bot のセットアップ
intents = discord.Intents.default()
intents.guild_scheduled_events = True  # スケジュールされたイベントの Intent を有効化
client = MyBot(command_prefix="/", intents=intents)

@client.event
async def on_ready():
    # Bot が起動したときにログを出力し、スラッシュコマンドを同期
    print(f"Logged in as {client.user}")
    try:
        if ENV_TYPE == "development":
            # 開発環境: ギルドコマンドとして登録
            if DEV_GUILD_ID:
                guild = discord.Object(id=int(DEV_GUILD_ID))
                synced = await client.tree.sync(guild=guild)
                print(f"Synced {len(synced)} commands to guild {DEV_GUILD_ID}.")
            else:
                print("DEV_GUILD_ID is not set. Cannot sync commands in development environment.")
        else:
            # 本番環境: グローバルコマンドとして登録
            synced = await client.tree.sync()
            print(f"Synced {len(synced)} global commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@client.event
async def on_interaction(interaction: discord.Interaction):
    # 本番環境で除外ギルドIDが設定されている場合、そのギルドからのリクエストを無視
    if ENV_TYPE == "production" and DEV_GUILD_ID and str(interaction.guild_id) == DEV_GUILD_ID:
        print(f"Ignoring interaction from excluded guild {DEV_GUILD_ID}.")
        return

    await client.process_application_commands(interaction)

# デフォルトチャンネルを設定するスラッシュコマンド
@client.tree.command(name="set_channel", description="イベント作成のデフォルトチャンネルを設定します。")
@app_commands.describe(channel="デフォルトに設定するボイスチャンネルです。")
async def set_channel(interaction: discord.Interaction, channel: discord.VoiceChannel):
    guild_id = interaction.guild.id
    channel_id = channel.id

    # データベースにデフォルトチャンネルを保存
    cursor.execute("REPLACE INTO server_settings (guild_id, channel_id) VALUES (?, ?)", (guild_id, channel_id))
    conn.commit()

    await interaction.response.send_message(f"デフォルトチャンネルを {channel.mention} に設定しました。", ephemeral=True)

# ゲーム募集イベントを作成するスラッシュコマンド
@client.tree.command(name="create_event", description="ゲーム募集イベントを作成します。")
@app_commands.describe(number_of_players="募集人数 (デフォルト: 4)", start_time="開始時間 (hh:mm形式、例: 21:00)", game_name="募集するゲーム名 (デフォルト: VALORANT)")
async def create_event(interaction: discord.Interaction, number_of_players: int = 4, start_time: str = "21:00", game_name: str = "VALORANT"):
    # 開始時間を検証
    try:
        start_time_obj = datetime.strptime(start_time, "%H:%M")
        # Asia/Tokyoのタイムゾーンを適用
        tokyo_tz = timezone(timedelta(hours=9))
        now_tokyo = datetime.now(tokyo_tz)
        start_time_utc = now_tokyo.replace(hour=start_time_obj.hour, minute=start_time_obj.minute, second=0, microsecond=0).astimezone(timezone.utc)

        # 入力された時間が過去の場合
        if start_time_utc < now_tokyo.astimezone(timezone.utc):
            await interaction.response.send_message("開始時間が過去の時間です。未来の時間を指定してください。", ephemeral=True)
            return

        # デフォルトの21:00が指定され、現在時刻が21:00以降の場合
        if start_time == "21:00" and now_tokyo.hour >= 21:
            start_time_utc = (now_tokyo + timedelta(minutes=30)).replace(second=0, microsecond=0).astimezone(timezone.utc)
    except ValueError:
        await interaction.response.send_message("開始時間の形式が正しくありません。hh:mm形式で入力してください (例: 21:00)。", ephemeral=True)
        return

    guild_id = interaction.guild.id
    cursor.execute("SELECT channel_id FROM server_settings WHERE guild_id = ?", (guild_id,))
    result = cursor.fetchone()

    if not result:
        await interaction.response.send_message("デフォルトチャンネルが設定されていません。/set_channel コマンドを使用して設定してください。", ephemeral=True)
        return

    channel_id = result[0]
    channel = interaction.guild.get_channel(channel_id)

    if not channel:
        await interaction.response.send_message("デフォルトチャンネルが無効です。/set_channel コマンドを使用して再設定してください。", ephemeral=True)
        return

    # イベントを作成
    event_name = f"{game_name}募集 @{number_of_players}"
    description = f"開始時間: {start_time}"
    event = await interaction.guild.create_scheduled_event(
        name=event_name,
        description=description,
        start_time=start_time_utc,
        channel=channel,
        entity_type=discord.EntityType.voice,
        privacy_level=discord.PrivacyLevel.guild_only
    )

    # イベントIDと作成チャンネルIDをデータベースに保存
    cursor.execute("INSERT INTO event_channels (event_id, channel_id) VALUES (?, ?)", (event.id, interaction.channel_id))
    conn.commit()

    # イベント作成メッセージをスラッシュコマンドへの返信として送信
    await interaction.response.send_message(f"{event.url}", ephemeral=False)

# Bot を実行
client.run(TOKEN)