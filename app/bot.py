# discord.pyライブラリをインポート
import discord
# discord.ext.commandsをインポート
from discord.ext import commands
# 非同期スケジューラをインポート
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# コマンド登録用の関数をインポート
from commands import register_commands
# タスク登録用の関数をインポート
from tasks import register_tasks
# 環境変数の設定をインポート
from config import ENV_TYPE, DEV_GUILD_ID

# スケジューラの初期化
scheduler = AsyncIOScheduler()

# カスタム Bot クラス
class MyBot(commands.Bot):
    async def setup_hook(self):
        # スケジューラを開始
        scheduler.start()
        # コマンドを登録
        register_commands(self)
        # タスクを登録
        register_tasks(self, scheduler)

# Bot のセットアップ
intents = discord.Intents.default()
# スケジュールされたイベントの Intent を有効化
intents.guild_scheduled_events = True
# メッセージ内容の Intent を有効化
intents.message_content = True
client = MyBot(command_prefix="/", intents=intents)

@client.event
async def on_ready():
    # Bot が起動したときにログを出力し、スラッシュコマンドを同期
    print(f"Logged in as {client.user}")
    try:
        # スラッシュコマンドの同期
        print("Syncing global commands...")
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} global commands.")
        if ENV_TYPE == "development":
            # 開発環境: ギルドコマンドとして登録
            if DEV_GUILD_ID:
                guild = discord.Object(id=int(DEV_GUILD_ID))
                client.tree.copy_global_to(guild=guild)
                print(f"Synced commands to guild {DEV_GUILD_ID}.")
            else:
                print("DEV_GUILD_ID is not set. Cannot sync commands in development environment.")
                
    except Exception as e:
        print(f"Error syncing commands: {e}")