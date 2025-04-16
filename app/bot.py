import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from commands import register_commands
from tasks import register_tasks
from config import ENV_TYPE, DEV_GUILD_ID

# スケジューラの初期化
scheduler = AsyncIOScheduler()

# カスタム Bot クラス
class MyBot(commands.Bot):
    async def setup_hook(self):
        scheduler.start()
        register_commands(self)
        register_tasks(self, scheduler)

# Bot のセットアップ
intents = discord.Intents.default()
intents.guild_scheduled_events = True  # スケジュールされたイベントの Intent を有効化
intents.message_content = True  # メッセージ内容の Intent を有効化
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
                print("Syncing commands to development guild...")
                synced = await client.tree.sync(guild=guild)
                print(f"Synced {len(synced)} commands to guild {DEV_GUILD_ID}.")
            else:
                print("DEV_GUILD_ID is not set. Cannot sync commands in development environment.")
        else:
            # 本番環境: グローバルコマンドとして登録
            print("Syncing global commands...")
            synced = await client.tree.sync()
            print(f"Synced {len(synced)} global commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")